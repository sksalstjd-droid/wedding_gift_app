# Wedding Gift Manager

결혼식/행사 당일 축의금 입력과 사후 정리를 위한 Flask 기반 모바일 웹앱입니다.

장기 운영 서비스가 아니라 행사 당일과 사후 정리에 사용하는 일회성 실사용 도구를 목표로 합니다. 기본 DB는 SQLite이며, PythonAnywhere에서 SQLite 기준으로 테스트 배포할 수 있습니다.

## 주요 기능

- 모바일 기준 축의금 빠른 입력
- 신부측/신랑측 봉투번호 독립 관리
- 같은 구분 안에서 봉투번호 중복 방지
- 삭제 데이터는 soft delete 처리
- 최근 입력 카드 표시 및 삭제
- 전체 내역 검색, 구분 필터, 관계 미분류 필터
- 봉투순/금액순/관계순/식권순 정렬 및 오름차순/내림차순 토글
- 내역 수정/삭제
- 관계 미분류 정리
- 수정 화면에서 사용자 정의 관계 추가/삭제
- 통계 탭
  - 전체 현황
  - 관계별 통계
  - 금액별 통계
  - 식권 통계
  - 접수 구분 통계
- Excel 다운로드
- 선택사항: `ADMIN_PIN` 기반 간단한 PIN 접근 보호

## 기술 스택

- Backend: Flask
- DB: SQLite
- ORM: Flask-SQLAlchemy
- Template: Jinja2
- Frontend: HTML/CSS/Vanilla JS
- Excel Export: openpyxl

## 로컬 실행

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 접속합니다.

```text
http://127.0.0.1:5000
```

개발 모드로 실행하려면 `.env`에 `FLASK_DEBUG=1`을 설정합니다.

## 환경변수 예시

`.env` 파일은 git에 포함하지 않습니다.

```env
SECRET_KEY=change-this-to-a-random-secret
ADMIN_PIN=1234
FLASK_DEBUG=1
```

설명:

- `SECRET_KEY`: Flask session 보호용 값입니다. 배포 시 반드시 임의의 긴 값으로 설정하세요.
- `ADMIN_PIN`: 설정하면 사이트 접속 시 PIN 입력이 필요합니다. 설정하지 않으면 로컬 개발 편의를 위해 PIN 보호가 꺼집니다.
- `FLASK_DEBUG`: `1`이면 `python app.py` 실행 시 debug 모드가 켜집니다.

## 더미 데이터 생성

개발/테스트용 더미 데이터를 생성할 수 있습니다.

```bash
python scripts/seed_dummy_data.py
python scripts/seed_dummy_data.py --count 250
python scripts/seed_dummy_data.py --reset --count 250
```

주의:

- 기존 축의금 데이터가 있으면 기본 실행은 중단됩니다.
- 기존 데이터를 지우고 새로 만들 때만 `--reset`을 사용하세요.
- `--reset`은 `Gift`와 `RelationshipCategory` 데이터를 삭제합니다.

## 전체 초기화 주의

앱 입력 화면의 전체 초기화 기능은 축의금 내역과 사용자가 추가한 관계를 모두 삭제합니다.

이 작업은 되돌릴 수 없으므로 실제 행사 데이터가 있는 상태에서는 신중하게 사용하세요.

## PythonAnywhere + SQLite 테스트 배포 메모

1. PythonAnywhere에 프로젝트 파일을 업로드합니다.
2. 가상환경을 만들고 의존성을 설치합니다.

```bash
pip install -r requirements.txt
```

3. PythonAnywhere WSGI 파일에서 프로젝트 경로를 추가하고 `app`을 import합니다.

```python
import os
import sys

project_home = "/home/YOUR_USERNAME/wedding_gift_app"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ["SECRET_KEY"] = "change-this-to-a-random-secret"
os.environ["ADMIN_PIN"] = "change-this-pin"

from app import app as application
```

4. SQLite DB 파일은 기본적으로 프로젝트 루트의 `wedding_gift.db`를 사용합니다.
5. 배포 환경에서는 `SECRET_KEY`와 `ADMIN_PIN`을 반드시 설정하세요.
6. 이번 프로젝트는 일회성 소규모 사용을 전제로 하므로 SQLite 테스트 배포를 우선합니다.

## 데이터 규칙

- 봉투번호는 DB id와 별개입니다.
- 봉투번호 중복 기준은 `event_id + side + envelope_no`입니다.
- 신부측 #1과 신랑측 #1은 동시에 존재할 수 있습니다.
- 삭제는 `deleted_at`을 채우는 soft delete 방식입니다.
- 삭제된 데이터는 목록/검색/통계/엑셀/중복검사에서 제외됩니다.

## Icon attribution

Diamond ring icon designed by [Umeicon](https://www.flaticon.com/authors/umeicon) from [Flaticon](https://www.flaticon.com/).
