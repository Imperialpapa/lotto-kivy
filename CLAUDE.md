# CLAUDE.md

## 프로젝트 개요
<!-- 프로젝트의 목적과 주요 기능을 간략하게 설명하세요 -->
이 프로젝트는 [프로젝트 설명]입니다.

## 기술 스택
- **언어**: Python 3.9+
- **프레임워크**: [Django/Flask/FastAPI 등]
- **데이터베이스**: [PostgreSQL/MySQL/SQLite 등]
- **기타 라이브러리**: [주요 의존성들]

## 프로젝트 구조
```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── views/
│   ├── utils/
│   └── config/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## 코딩 표준 및 컨벤션

### 코드 스타일
- **PEP 8** 준수
- **Black** 포매터 사용 (line length: 88)
- **isort** 사용하여 import 정렬
- **flake8** 또는 **pylint** 사용하여 코드 품질 검사

### 네이밍 컨벤션
- **변수/함수**: snake_case (예: `user_name`, `calculate_total`)
- **클래스**: PascalCase (예: `UserModel`, `DataProcessor`)
- **상수**: UPPER_SNAKE_CASE (예: `API_BASE_URL`, `MAX_RETRY_COUNT`)
- **파일명**: snake_case (예: `user_service.py`, `data_utils.py`)

### 함수 및 클래스 작성 가이드
```python
def process_user_data(user_id: int, include_metadata: bool = False) -> dict:
    """
    사용자 데이터를 처리하고 반환합니다.
    
    Args:
        user_id: 처리할 사용자 ID
        include_metadata: 메타데이터 포함 여부
        
    Returns:
        처리된 사용자 데이터 딕셔너리
        
    Raises:
        UserNotFoundError: 사용자를 찾을 수 없을 때
        ValidationError: 데이터 유효성 검사 실패 시
    """
    # 구현 코드
    pass
```

### 에러 처리
- 구체적인 예외 클래스 사용
- 적절한 에러 메시지 포함
- 로깅 추가 (logging 모듈 사용)

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"작업 실패: {e}")
    raise
```

## 개발 환경 설정

### 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 환경 변수
`.env` 파일을 사용하여 환경 변수 관리:
```
DATABASE_URL=postgresql://username:password@localhost/dbname
SECRET_KEY=your-secret-key
DEBUG=True
```

### 개발 도구 설정
```bash
# 개발 도구 설치
pip install black isort flake8 pytest

# 코드 포매팅
black .
isort .

# 린터 실행
flake8 .

# 테스트 실행
pytest
```

## 테스트 가이드라인

### 테스트 구조
- **단위 테스트**: `tests/unit/`
- **통합 테스트**: `tests/integration/`
- **테스트 데이터**: `tests/fixtures/`

### 테스트 작성 예시
```python
import pytest
from src.utils import calculate_total

class TestCalculateTotal:
    def test_calculate_total_with_positive_numbers(self):
        result = calculate_total([1, 2, 3])
        assert result == 6
    
    def test_calculate_total_with_empty_list(self):
        result = calculate_total([])
        assert result == 0
    
    def test_calculate_total_with_invalid_input(self):
        with pytest.raises(TypeError):
            calculate_total("not a list")
```

## 데이터베이스 관련

### 마이그레이션 관리
```bash
# 새 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate
```

### 쿼리 최적화
- N+1 쿼리 문제 방지
- 적절한 인덱스 사용
- 쿼리 결과 캐싱 고려

## 성능 및 보안 고려사항

### 성능
- 비동기 처리 사용 (asyncio, aiohttp)
- 데이터베이스 연결 풀링
- 메모리 사용량 모니터링

### 보안
- 입력 데이터 검증
- SQL 인젝션 방지
- 인증/인가 구현
- 민감한 정보 암호화

## 로깅 및 모니터링

### 로깅 설정
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 모니터링 포인트
- 응답 시간
- 에러율
- 메모리 사용량
- 데이터베이스 연결 상태

## 배포 및 운영

### 배포 체크리스트
- [ ] 모든 테스트 통과
- [ ] 환경 변수 설정 확인
- [ ] 데이터베이스 마이그레이션 적용
- [ ] 정적 파일 수집
- [ ] 보안 설정 확인

### 운영 모니터링
- 로그 수집 및 분석
- 성능 메트릭 모니터링
- 알림 설정

## 문서화 가이드라인

### 코드 문서화
- 모든 퍼블릭 함수/클래스에 docstring 작성
- 복잡한 로직에 주석 추가
- 타입 힌트 사용

### API 문서화
- OpenAPI/Swagger 스펙 사용
- 엔드포인트별 예시 요청/응답 포함

## 자주 사용하는 명령어

```bash
# 개발 서버 시작
python manage.py runserver

# 테스트 실행
pytest -v

# 코드 품질 검사
black --check .
isort --check-only .
flake8 .

# 의존성 업데이트
pip list --outdated
pip install --upgrade package-name
```

## 트러블슈팅

### 일반적인 문제 해결
1. **Import 에러**: PYTHONPATH 설정 확인
2. **데이터베이스 연결 실패**: 연결 정보 및 서비스 상태 확인
3. **메모리 부족**: 프로파일링 도구 사용하여 메모리 사용량 분석

### 개발 팁
- 가상환경 활성화 상태 확인
- 환경 변수 로드 확인
- 로그 레벨 조정하여 디버깅 정보 확인

## 추가 참고 자료

- [Python 공식 문서](https://docs.python.org/)
- [PEP 8 스타일 가이드](https://pep8.org/)
- [Django 문서](https://docs.djangoproject.com/) (Django 사용 시)
- [Flask 문서](https://flask.palletsprojects.com/) (Flask 사용 시)
- [FastAPI 문서](https://fastapi.tiangolo.com/) (FastAPI 사용 시)

---

**주의**: 이 문서는 프로젝트 특성에 맞게 수정하여 사용하세요. 불필요한 섹션은 제거하고, 프로젝트 고유의 요구사항을 추가하세요.