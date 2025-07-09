import base64
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# --- Configuration ---
# Supabase 설정 (인코딩됨)
_SB_URL = "aHR0cHM6Ly9uaXd0enZ3Y29kbW1qdm54Ynp4Zi5zdXBhYmFzZS5jbw=="
_SB_KEY = "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKemRYQmhZbUZ6WlNJc0luSmxaaUk2SW01cGQzUjZkbmRqYjJSdGJXcDJibmhpZW5obUlpd2ljbTlzWlNJNkltRnViMjRpTENKcFlYUWlPakUzTlRFM056VTVORGdzSW1WNGNDSTZNakEyTnpNMU1UazBPSDAuTnQ1dHN1ZHc4aXBJcEFqbkYwNDV2T0VnTms2Uk5mV0dzOHFCTmRSMlk2bw=="

def _decode_config() -> Tuple[Optional[str], Optional[str]]:
    """설정 디코딩"""
    try:
        url = base64.b64decode(_SB_URL).decode()
        key = base64.b64decode(_SB_KEY).decode()
        return url, key
    except Exception as e:
        logger.error(f"설정 디코딩 실패: {e}")
        return None, None

SUPABASE_URL, SUPABASE_KEY = _decode_config()
BASE_URL = "https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo={}"
