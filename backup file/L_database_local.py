import json
import csv
import os
import logging
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup

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
            response = requests.get("https://www.dhlottery.co.kr/common.do?method=main", 
                                  timeout=15, headers=headers)
            response.raise_for_status()
            
            # HTML 파싱하여 최신 회차 추출
            soup = BeautifulSoup(response.content, 'html.parser')
            lotto_element = soup.select_one('#lottoDrwNo')
            
            if not lotto_element:
                return False, "최신 회차 정보를 찾을 수 없습니다"
                
            latest_web_round = int(lotto_element.text)
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
    
    def __init__(self, database_instance=None, on_progress=None, on_finished=None):
        self.db = database_instance or init_local_database()
        self.on_progress = on_progress
        self.on_finished = on_finished
    
    def start(self):
        """업데이트 확인 시작"""
        if not self.db:
            if self.on_finished:
                self.on_finished("데이터베이스 연결 실패")
            return
        
        if self.on_progress:
            self.on_progress("업데이트 확인 중...")
        
        # 업데이트 필요 여부 확인
        needs_update, message = self.db.check_for_updates()
        
        if self.on_finished:
            if needs_update:
                self.on_finished(f"업데이트 필요: {message}")
            else:
                self.on_finished(f"최신 상태: {message}")