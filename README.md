# 🎰 6/45 로또 생성기

[![Build APK](https://github.com/your-username/lotto-kivy/actions/workflows/build-apk.yml/badge.svg)](https://github.com/your-username/lotto-kivy/actions/workflows/build-apk.yml)

## 📱 소개

17가지 다양한 알고리즘을 사용하여 로또 번호를 생성하는 모바일/데스크톱 애플리케이션입니다. 
과거 당첨번호 분석 기반의 통계적 접근법과 다양한 패턴 분석을 통해 로또 번호를 생성합니다.

## ✨ 주요 기능

### 🎲 17가지 번호 생성 알고리즘
1. **기본 랜덤** - 완전 무작위 생성
2. **패턴 분석 (자주)** - 자주 나온 번호 기반
3. **패턴 분석 (드물게)** - 잘 안 나온 번호 기반
4. **홀수/짝수 균형** - 홀짝 비율 최적화
5. **숫자 범위 분포** - 구간별 균등 분포
6. **소수 번호 포함** - 소수 포함 조합
7. **번호 총합 기반** - 당첨번호 총합 패턴 분석
8. **연속 번호 포함** - 연속 번호 조합
9. **핫/콜드 번호 조합** - 자주/드물게 나온 번호 믹스
10. **자주 나온 번호 쌍 기반** - 함께 나온 번호 분석
11. **끝자리 패턴 분석** - 끝자리 숫자 패턴
12. **통계적 최적화** - 종합 통계 분석
13. **이월수/미출현수 조합** - 연속 당첨/미당첨 분석
14. **동일 끝수 조합** - 같은 끝자리 조합
15. **궁합수 분석** - 상극 번호 제외
16. **데이터 기반 조합** - 모든 데이터 종합 분석
17. **모든 방법 조합** - 전체 알고리즘 조합

### 📊 데이터 관리
- **자동 업데이트**: 동행복권에서 최신 당첨번호 자동 수집
- **과거 당첨번호 조회**: 원하는 회차 범위 검색
- **로컬 데이터베이스**: 오프라인에서도 사용 가능
- **데이터 검증**: 번호 유효성 자동 검사

### 🎨 사용자 인터페이스
- **다국어 지원**: 한글 폰트 자동 설정
- **애니메이션**: 번호 생성 시 볼 애니메이션
- **모바일 최적화**: 터치 인터페이스 지원
- **반응형 디자인**: 다양한 화면 크기 대응

## 🚀 빠른 시작

### Android APK 다운로드
1. [Releases](https://github.com/your-username/lotto-kivy/releases) 페이지 방문
2. 최신 APK 파일 다운로드
3. 안드로이드 기기에 설치

### 로컬 개발 환경 설정

#### 필요 조건
- Python 3.9+
- Git

#### 설치 방법
```bash
# 1. 저장소 클론
git clone https://github.com/your-username/lotto-kivy.git
cd lotto-kivy

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 3. 의존성 설치
pip install kivy requests beautifulsoup4

# 4. 애플리케이션 실행
python main.py
```

## 🔧 APK 빌드

### GitHub Actions (자동 빌드)
1. 코드를 `main` 브랜치에 푸시
2. GitHub Actions가 자동으로 APK 빌드
3. Actions 탭에서 빌드 진행 상황 확인
4. 완료 후 Artifacts에서 APK 다운로드

### 로컬 빌드 (수동)
```bash
# 1. buildozer 설치
pip install buildozer

# 2. 시스템 의존성 설치 (Ubuntu/WSL)
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip \\
  autoconf libtool pkg-config zlib1g-dev libncurses5-dev \\
  libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 3. APK 빌드
buildozer android debug
```

## 📁 프로젝트 구조

```
lotto-kivy/
├── main.py                    # 메인 애플리케이션
├── lotto.kv                   # UI 레이아웃 (Kivy)
├── L_lotto_logic.py          # 로또 번호 생성 로직
├── L_database_local.py       # 로컬 데이터베이스
├── L_animation.py            # 애니메이션 효과
├── L_config.py               # 설정 파일
├── lotto_dataman.py          # 데이터 관리자
├── lotto_data.csv            # 로컬 데이터 파일
├── buildozer.spec            # Android 빌드 설정
├── .github/workflows/        # GitHub Actions
│   └── build-apk.yml         # APK 빌드 워크플로우
└── README.md                 # 프로젝트 문서
```

## 🛠️ 기술 스택

- **UI 프레임워크**: [Kivy](https://kivy.org/) 2.3.1
- **언어**: Python 3.11+
- **네트워킹**: requests, beautifulsoup4
- **빌드 도구**: buildozer
- **CI/CD**: GitHub Actions
- **플랫폼**: Android, Windows, macOS, Linux

## 📝 사용법

### 기본 사용
1. 앱 실행 후 생성 방법 선택
2. 게임 수 입력 (기본 5게임)
3. "번호 생성" 버튼 클릭
4. 애니메이션과 함께 결과 확인

### 당첨번호 조회
1. "당첨번호 조회" 탭 선택
2. 조회할 회차 범위 입력
3. "조회" 버튼 클릭
4. 결과 팝업에서 당첨번호 확인

### 데이터 업데이트
- 앱 시작 시 자동으로 최신 데이터 확인
- 새로운 회차 발견 시 자동 업데이트
- 수동 업데이트도 가능

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## ⚠️ 면책 조항

이 애플리케이션은 오락 목적으로만 제작되었습니다. 로또 번호 생성은 완전히 무작위이며, 당첨을 보장하지 않습니다. 
책임감 있는 게임을 즐기시기 바랍니다.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 [Issues](https://github.com/your-username/lotto-kivy/issues)를 통해 연락해 주세요.

---

**즐거운 로또 번호 생성 되세요! 🍀**