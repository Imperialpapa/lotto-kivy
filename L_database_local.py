import json
import csv
import os
import logging
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class LocalLottoDatabase:
    def __init__(self, data_file: str = "lotto_data.json"):
        self.data_file = data_file
        self.csv_file = data_file.replace('.json', '.csv')
        
    def load_data(self) -> List[Dict]:
        """로컬 JSON 파일에서 데이터 로드"""
        if not os.path.exists(self.data_file):
            logger.warning(f"데이터 파일 {self.data_file}이 존재하지 않습니다")
            return []
            
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"로컬에서 {len(data)}개 회차 데이터 로드")
            return data
        except Exception as e:
            logger.error(f"로컬 데이터 로드 실패: {e}")
            return []
    
    def load_data_from_csv(self) -> List[Dict]:
        """CSV 파일에서 데이터 로드 (APK용)"""
        if not os.path.exists(self.csv_file):
            logger.warning(f"CSV 데이터 파일 {self.csv_file}이 존재하지 않습니다")
            return []
            
        try:
            data = []
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 문자열을 정수로 변환
                    processed_row = {
                        'round': int(row['round']),
                        'num1': int(row['num1']),
                        'num2': int(row['num2']),
                        'num3': int(row['num3']),
                        'num4': int(row['num4']),
                        'num5': int(row['num5']),
                        'num6': int(row['num6']),
                        'bonus': int(row['bonus']),
                        'draw_date': row['draw_date']
                    }
                    data.append(processed_row)
            
            logger.info(f"CSV에서 {len(data)}개 회차 데이터 로드")
            return data
        except Exception as e:
            logger.error(f"CSV 데이터 로드 실패: {e}")
            return []
    
    def get_latest_round(self) -> Optional[int]:
        """최신 회차 번호 반환"""
        data = self.load_data()
        if not data:
            return None
        return max(item['round'] for item in data)
    
    def query_data_by_range(self, from_round: int, to_round: int) -> List[Dict]:
        """회차 범위로 데이터 조회"""
        data = self.load_data()
        if not data:
            return []
            
        filtered_data = [
            item for item in data 
            if from_round <= item['round'] <= to_round
        ]
        
        # 회차별로 내림차순 정렬
        filtered_data.sort(key=lambda x: x['round'], reverse=True)
        return filtered_data
    
    def check_for_updates(self) -> Tuple[bool, str]:
        """동행복권 웹사이트에서 최신 회차 확인"""
        try:
            # 메인 페이지에서 최신 회차 확인
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive'
            }
            response = requests.get("https://www.dhlottery.co.kr/common.do?method=main", 
                                  timeout=15, headers=headers)
            response.raise_for_status()
            
            # HTML 파싱하여 최신 회차 추출
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
                return False, "최신 회차 정보를 찾을 수 없습니다"
            latest_local_round = self.get_latest_round()
            
            if latest_local_round is None:
                return True, f"웹 최신 회차: {latest_web_round}회 (로컬 데이터 없음)"
            
            if latest_local_round >= latest_web_round:
                return False, f"최신 회차: {latest_local_round}회 (현재 최신 상태)"
            else:
                missing_rounds = latest_web_round - latest_local_round
                return True, f"새로운 데이터 {missing_rounds}회차 발견 (최신: {latest_web_round}회)"
            
        except Exception as e:
            logger.error(f"업데이트 확인 실패: {e}")
            return False, f"업데이트 확인 실패: {str(e)[:50]}"
    
    def get_winning_numbers(self, round_number: int) -> Tuple[Optional[List[int]], Optional[int]]:
        """특정 회차의 당첨번호 조회 (웹 스크래핑)"""
        try:
            url = f"https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo={round_number}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive'
            }
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            
            # BeautifulSoup으로 HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')
            win_nums_spans = soup.select("div.win_result div.num.win p span.ball_645")
            bonus_num_span = soup.select_one("div.win_result div.num.bonus p span.ball_645")
            
            if len(win_nums_spans) == 6 and bonus_num_span:
                try:
                    win_nums = [int(span.get_text().strip()) for span in win_nums_spans]
                    bonus_num = int(bonus_num_span.get_text().strip())
                    
                    # 데이터 유효성 검사
                    if (len(win_nums) == 6 and 
                        bonus_num and 
                        all(1 <= x <= 45 for x in win_nums) and 
                        1 <= bonus_num <= 45 and
                        len(set(win_nums)) == 6 and  # 중복 제거
                        bonus_num not in win_nums):  # 보너스 번호가 당첨번호에 없음
                        return win_nums, bonus_num
                except ValueError as e:
                    logger.error(f"{round_number}회 번호 파싱 오류: {e}")
                    
            return None, None
            
        except Exception as e:
            logger.error(f"{round_number}회 데이터 수집 오류: {e}")
            return None, None

def init_local_database(data_file: str = "lotto_data.json") -> Optional[LocalLottoDatabase]:
    """로컬 데이터베이스 초기화"""
    try:
        db = LocalLottoDatabase(data_file)
        # 데이터 파일 존재 여부 확인
        if not os.path.exists(data_file):
            # CSV 파일도 확인
            csv_file = data_file.replace('.json', '.csv')
            if not os.path.exists(csv_file):
                logger.error(f"데이터 파일이 존재하지 않습니다: {data_file}, {csv_file}")
                return None
        
        logger.info("로컬 데이터베이스 초기화 완료")
        return db
        
    except Exception as e:
        logger.error(f"로컬 데이터베이스 초기화 실패: {e}")
        return None

def load_lotto_data_from_local() -> Tuple[List[List[int]], str]:
    """로컬 파일에서 로또 데이터 로드 (기존 함수와 호환)"""
    try:
        db = init_local_database()
        if not db:
            return [], "로컬 데이터베이스 초기화 실패"
        
        # JSON 먼저 시도, 실패하면 CSV 시도 (APK 환경 고려)
        data = db.load_data()
        if not data:
            data = db.load_data_from_csv()
        
        if not data:
            return [], "데이터를 로드할 수 없습니다"
        
        # L_lotto_logic.py 형식에 맞게 변환 (번호만 추출)
        past_winnings = []
        for item in data:
            numbers = [item['num1'], item['num2'], item['num3'], 
                      item['num4'], item['num5'], item['num6']]
            past_winnings.append(numbers)
        
        return past_winnings, f"{len(data)}개 회차 데이터 로드 완료"
        
    except Exception as e:
        logger.error(f"로또 데이터 로드 실패: {e}")
        return [], f"데이터 로드 실패: {e}"

class LocalDatabaseUpdater:
    """로컬 데이터베이스 업데이터 (기존 DatabaseUpdater와 호환)"""
    
    def __init__(self, database_instance=None):
        self.db = database_instance or init_local_database()

    def start(self):
        """업데이트 확인 시작"""
        if not self.db:
            return False, "데이터베이스 연결 실패"
        
        # 업데이트 필요 여부 확인
        needs_update, message = self.db.check_for_updates()
        
        return needs_update, message
    
    def update_missing_rounds(self) -> Tuple[bool, str]:
        """누락된 회차 데이터를 웹에서 가져와서 로컬 파일에 업데이트"""
        if not self.db:
            return False, "데이터베이스 연결 실패"
        
        try:
            # 웹에서 최신 회차 확인
            needs_update, update_message = self.db.check_for_updates()
            
            if not needs_update:
                return False, update_message
            
            # 현재 로컬 데이터에서 최신 회차 및 웹 최신 회차 가져오기
            latest_local_round = self.db.get_latest_round() or 0
            latest_web_round = self._get_latest_web_round()
            
            if latest_web_round is None:
                return False, "웹에서 최신 회차를 가져올 수 없습니다"
            
            if latest_local_round >= latest_web_round:
                return False, f"이미 최신 상태입니다 ({latest_local_round}회)"
            
            # 누락된 회차들 수집
            missing_rounds = []
            for round_num in range(latest_local_round + 1, latest_web_round + 1):
                win_nums, bonus_num = self.db.get_winning_numbers(round_num)
                if win_nums and bonus_num:
                    # 추첨일자 가져오기 (기본값 설정)
                    draw_date = self._get_draw_date(round_num)
                    
                    round_data = {
                        'round': round_num,
                        'num1': win_nums[0],
                        'num2': win_nums[1], 
                        'num3': win_nums[2],
                        'num4': win_nums[3],
                        'num5': win_nums[4],
                        'num6': win_nums[5],
                        'bonus': bonus_num,
                        'draw_date': draw_date
                    }
                    missing_rounds.append(round_data)
                    logger.info(f"{round_num}회 데이터 수집 완료: {win_nums} + {bonus_num}")
                else:
                    logger.warning(f"{round_num}회 데이터 수집 실패")
            
            if not missing_rounds:
                return False, "수집할 수 있는 새로운 데이터가 없습니다"
            
            # 로컬 데이터 파일에 저장
            success = self._save_to_local_file(missing_rounds)
            
            if success:
                return True, f"{len(missing_rounds)}개 회차 업데이트 완료 ({latest_local_round + 1}회 ~ {latest_web_round}회)"
            else:
                return False, "데이터 저장 실패"
                
        except Exception as e:
            logger.error(f"누락된 회차 업데이트 오류: {e}")
            return False, f"업데이트 오류: {str(e)[:50]}"
    
    def _get_latest_web_round(self) -> Optional[int]:
        """웹에서 최신 회차 가져오기"""
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
            
            soup = BeautifulSoup(response.content, 'html.parser')
            selectors = ['#lottoDrwNo', '.lotto_drw_no', '[id*="drw"]', 'strong[id*="drw"]']
            
            for selector in selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        return int(element.get_text().strip())
                except (ValueError, AttributeError):
                    continue
            
            return None
        except Exception as e:
            logger.error(f"웹 최신 회차 가져오기 실패: {e}")
            return None
    
    def _get_draw_date(self, round_number: int) -> str:
        """회차에 따른 추첨일자 계산 (기본값)"""
        # 1회차는 2002년 12월 7일 토요일이었고, 매주 토요일마다 추첨
        from datetime import datetime, timedelta
        
        # 1회차 추첨일 (2002-12-07)
        first_draw_date = datetime(2002, 12, 7)
        
        # 각 회차는 7일 간격
        target_date = first_draw_date + timedelta(weeks=round_number - 1)
        
        return target_date.strftime('%Y-%m-%d')
    
    def _save_to_local_file(self, new_data: List[Dict]) -> bool:
        """새로운 데이터를 로컬 JSON 파일에 추가"""
        try:
            # 기존 데이터 로드
            existing_data = self.db.load_data()
            
            # 새로운 데이터 추가
            all_data = existing_data + new_data
            
            # 회차별로 정렬
            all_data.sort(key=lambda x: x['round'])
            
            # JSON 파일에 저장
            with open(self.db.data_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            # CSV 파일도 업데이트 (APK 호환성)
            self._update_csv_file(all_data)
            
            logger.info(f"로컬 파일 업데이트 완료: {len(new_data)}개 회차 추가")
            return True
            
        except Exception as e:
            logger.error(f"로컬 파일 저장 실패: {e}")
            return False
    
    def _update_csv_file(self, data: List[Dict]) -> None:
        """갱신된 데이터를 CSV 파일에도 저장"""
        try:
            fieldnames = ['round', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'bonus', 'draw_date']
            
            with open(self.db.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"CSV 파일 업데이트 완료: {self.db.csv_file}")
        except Exception as e:
            logger.error(f"CSV 파일 업데이트 실패: {e}")