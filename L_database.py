import logging
import requests
import time
import threading
from typing import Optional, Tuple, List, Callable
from bs4 import BeautifulSoup
from supabase import create_client, Client
from L_config import SUPABASE_URL, SUPABASE_KEY, BASE_URL

logger = logging.getLogger(__name__)

supabase: Optional[Client] = None

def init_supabase() -> Optional[Client]:
    """Supabase 클라이언트를 초기화하고 반환합니다."""
    global supabase
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Supabase 클라이언트 초기화 성공")
            return supabase
        except Exception as e:
            logger.error(f"Supabase 연결 오류: {e}")
            return None
    logger.error("Supabase URL 또는 KEY가 설정되지 않았습니다.")
    return None

def load_lotto_data_from_supabase() -> Tuple[Optional[List[List[int]]], str]:
    """Supabase에서 로또 데이터 로드"""
    if not supabase:
        return None, "데이터베이스 연결이 설정되지 않았습니다."
    
    try:
        response = supabase.table('lotto_data').select('num1, num2, num3, num4, num5, num6').order('round').execute()
        
        if response.data:
            winning_numbers = []
            for row in response.data:
                numbers = [row['num1'], row['num2'], row['num3'], row['num4'], row['num5'], row['num6']]
                if all(1 <= x <= 45 for x in numbers) and len(set(numbers)) == 6:
                    winning_numbers.append(sorted(numbers))
            
            if winning_numbers:
                logger.info(f"데이터 로드 성공: {len(winning_numbers)}개 당첨 번호")
                return (winning_numbers, f"데이터 로드 성공: 총 {len(winning_numbers)}개의 당첨 번호를 불러왔습니다.")
            else:
                logger.warning("유효한 데이터를 찾지 못함")
                return ([], "데이터베이스에서 유효한 데이터를 찾지 못했습니다.")
        else:
            logger.info("데이터베이스가 비어있음")
            return ([], "데이터베이스가 비어있습니다.")
    except Exception as e:
        logger.error(f"데이터베이스 조회 오륙: {e}")
        return None, f"데이터베이스 조회 중 오류 발생: {str(e)[:50]}"

class DatabaseUpdater(threading.Thread):
    def __init__(self, supabase_client: Client, on_progress: Callable[[str], None], on_finished: Callable[[str], None]):
        super().__init__()
        self.supabase = supabase_client
        self.on_progress = on_progress
        self.on_finished = on_finished
        self.daemon = True # 메인 앱 종료 시 스레드도 함께 종료

    def run(self):
        try:
            self.on_progress("DB 최신 회차 확인 중...")
            response = self.supabase.table('lotto_data').select('round').order('round', desc=True).limit(1).execute()
            latest_local_round = response.data[0]['round'] if response.data else 0
            self.on_progress(f"DB 최신 회차: {latest_local_round}회")

            self.on_progress("웹 최신 회차 확인 중...")
            
            # 네트워크 요청 재시도 로직 추가
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                        'Connection': 'keep-alive'
                    }
                    response = requests.get("https://www.dhlottery.co.kr/common.do?method=main", 
                                          timeout=15, headers=headers)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise Exception(f"네트워크 연결 실패 (최대 재시도 초과): {e}")
                    self.on_progress(f"연결 재시도 중... ({attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)  # 지수 백오프
            
            # HTML 파싱 및 안전한 요소 선택
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 여러 선택자 시도
            latest_web_round = None
            selectors = ['#lottoDrwNo', '.lotto_drw_no', '[id*="drw"]', 'strong[id*="drw"]']
            
            for selector in selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        latest_web_round = int(element.get_text().strip())
                        break
                except (ValueError, AttributeError):
                    continue
            
            if latest_web_round is None:
                raise Exception("웹사이트에서 최신 회차 정보를 찾을 수 없습니다")
            
            self.on_progress(f"웹 최신 회차: {latest_web_round}회")

            if latest_local_round >= latest_web_round:
                self.on_finished(f"데이터가 최신입니다 ({latest_local_round}회)")
                return

            start_round = latest_local_round + 1
            new_data = []
            for round_num in range(start_round, latest_web_round + 1):
                self.on_progress(f"{round_num}회 데이터 수집 중...")
                win_nums, bonus_num = self._get_winning_numbers(round_num)
                if win_nums and bonus_num:
                    new_data.append({
                        'round': round_num, 'num1': win_nums[0], 'num2': win_nums[1], 'num3': win_nums[2],
                        'num4': win_nums[3], 'num5': win_nums[4], 'num6': win_nums[5], 'bonus': bonus_num
                    })
                time.sleep(0.2)

            if new_data:
                self.on_progress(f"{len(new_data)}개 데이터 저장 중...")
                self.supabase.table('lotto_data').upsert(new_data).execute()
                self.on_finished(f"업데이트 완료! ({len(new_data)}개 추가)")
            else:
                self.on_finished("업데이트 할 새로운 데이터가 없습니다.")

        except requests.exceptions.Timeout:
            logger.error("업데이트 스레드 오류: 네트워크 연결 시간 초과")
            self.on_finished("업데이트 오류: 네트워크 연결 시간 초과")
        except requests.exceptions.ConnectionError:
            logger.error("업데이트 스레드 오류: 네트워크 연결 실패")
            self.on_finished("업데이트 오류: 네트워크 연결 실패")
        except ValueError as e:
            logger.error(f"업데이트 스레드 오류: 데이터 형식 오류 - {e}")
            self.on_finished(f"업데이트 오륙: 데이터 형식 오류")
        except Exception as e:
            logger.error(f"업데이트 스레드 오류: {e}")
            self.on_finished(f"업데이트 오류: {str(e)[:50]}")

    def _get_winning_numbers(self, round_number: int) -> Tuple[Optional[List[int]], Optional[int]]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                url = BASE_URL.format(round_number)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Connection': 'keep-alive'
                }
                response = requests.get(url, timeout=15, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                win_nums_spans = soup.select("div.win_result div.num.win p span.ball_645")
                bonus_num_span = soup.select_one("div.win_result div.num.bonus p span.ball_645")
                
                if len(win_nums_spans) == 6 and bonus_num_span:
                    try:
                        win_nums = [int(span.get_text().strip()) for span in win_nums_spans]
                        bonus_num = int(bonus_num_span.get_text().strip())
                        
                        # 데이터 유효성 검사
                        if (len(win_nums) == 6 and 
                            all(1 <= x <= 45 for x in win_nums) and 
                            1 <= bonus_num <= 45 and
                            len(set(win_nums)) == 6 and  # 중복 제거
                            bonus_num not in win_nums):  # 보너스 번호가 당첨번호에 없음
                            return win_nums, bonus_num
                        else:
                            logger.warning(f"{round_number}회 데이터 유효성 검사 실패")
                    except ValueError as e:
                        logger.error(f"{round_number}회 번호 파싱 오류: {e}")
                
                return None, None
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"{round_number}회 데이터 수집 오류 (최대 재시도 초과): {e}")
                    return None, None
                time.sleep(1 * (attempt + 1))  # 재시도 지연
            except Exception as e:
                logger.error(f"{round_number}회 데이터 수집 오류: {e}")
                return None, None
        
        return None, None