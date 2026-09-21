# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.77] - 2026-09-21

### Fixed
- **언더스코어 파일명에서 포터블 감지·서비스팩 분류가 실패하던 버그** — 테스트 스위트를 작성하다 발견했습니다. 정규식 `\b`는 `_`를 단어 문자로 취급해 경계가 생기지 않습니다. 이 라이브러리는 언더스코어 파일명이 대부분이라 영향이 큽니다

  | 입력 | 이전 | 수정 후 |
  |---|---|---|
  | `HeidiSQL_12.21_64_Portable.zip` | 포터블 아님 ❌ | 포터블 ✅ |
  | `Portable_App.zip` | 포터블 아님 ❌ | 포터블 ✅ |
  | `app_sp2.exe` | `product` ❌ | `update` ✅ |

  `(?<![a-z0-9])...(?![a-z0-9])`로 영숫자 경계를 직접 지정했습니다. "Greenshot"이 `green`으로 오탐되지 않는 것도 테스트로 고정했습니다.

  ⚠️ **이미 등록된 데이터에는 소급 적용되지 않습니다.** 기존 제품/버전의 `is_portable`과 스캔 항목의 `classification`은 재스캔/재분류가 필요합니다.

### Added
- **테스트 스위트 (1계층)** — `backend/tests/` 90개 테스트, 약 2초. 커버리지 수치가 아니라 과거에 실제로 터진 버그를 회귀 테스트로 고정하는 것을 우선했습니다
  - `test_parser.py`, `test_classifier.py`, `test_confidence.py`, `test_security.py`, `test_config_masking.py`(v1.4.65 회귀), `test_discord_notifier.py`
  - CI에 `test` 잡 추가. `build-and-push`가 `[schema-check, test]`에 의존합니다

### Removed
- **죽은 테이블 3개 제거** (마이그레이션 `e4a861c32785`) — 운영 DB에서 행 수가 전부 0임을 확인했습니다
  - `unmatched_items` — v1.4.64에서 모델·API 제거, 테이블만 남아 있었음
  - `scan_history` — 초기 커밋 이후 미사용. 실제 이력은 `scan_history.json` 파일
  - `metadata_cache` — v1.4.64에서 사용처 제거. "신뢰도 신호로 쓸 여지"가 보존 사유였으나 신뢰도 스코어링은 규칙 기반 `core/confidence.py`로 구현되어 이 테이블을 쓰지 않았습니다
- `app/models/metadata_cache.py` 및 export 제거

### Changed
- **`build.sh`에서 이미지 빌드/푸시 제거** — 버전 bump + 커밋 + 태그 + push까지만 합니다. 이미지는 GitHub Actions만 만듭니다. 예전에는 로컬 빌드 후 푸시하고 tag push가 CI를 트리거해 같은 태그를 다시 빌드해 덮어썼습니다(1.4.69에서 실제 발생)
- **`CLAUDE.md` 정정** — 구현된 적 없는 "9개 소스 웹 크롤링" 폐기 기록, "Hybrid Caching 3계층"을 실재하는 2계층으로 정정, 규모 기술을 실측값으로 교체(v1.4.76 / 81개 `.py` 15,276줄 / 라우터 24개 / 모델 15개), 스키마·릴리스·레지스트리 정책 추가

## [1.4.76] - 2026-09-21

### Added
- **CI에서 스키마 드리프트 차단** — 모델과 마이그레이션이 어긋난 채로 이미지가 빌드되지 않습니다
  - `.github/workflows/docker-build.yml`에 `schema-check` 잡 추가: postgres를 띄워 빈 DB에 `alembic upgrade head` 적용 후 `alembic check`로 모델과 대조
  - `build-and-push`가 `needs: schema-check`로 의존하므로, 어긋나면 빌드가 아예 진행되지 않습니다
  - 2026-09에 `activity_logs`/`product_videos`/`share_links` 세 테이블이 Alembic 밖에서만 만들어지던 드리프트가 실제로 쌓였었고, 그 상태로 `create_all()`을 제거했다면 신규 설치에서 테이블이 사라졌을 것입니다

### Changed
- `alembic/env.py`에 `include_object` 필터 추가 — `alembic check`를 가드로 쓰려면 "의도적으로 다른" 부분을 차이로 보고하지 않아야 합니다. 세 부류를 제외하며 각각 이유를 주석에 남겼습니다
  - 손수 만든 GIN 인덱스 9개 — `gin_trgm_ops`는 모델로 표현할 수 없어 마이그레이션의 raw SQL로 만듭니다. 걸러내지 않으면 `drop_index`를 제안하고, 지우면 검색이 시퀀셜 스캔으로 돌아갑니다
  - 보류 중인 죽은 테이블(`unmatched_items`, `scan_history`)과 컬럼(`products.crawled_from`)

### 검증
정상 상태에서 `No new upgrade operations detected.`(종료코드 0), 모델에 임시 컬럼을 하나 넣은 역검증에서 `Detected added column`(종료코드 255)을 확인했습니다. 필터가 넓어져 가드가 무력해지지 않았음을 확인한 것입니다.

이로써 **A-2(스키마 관리 Alembic 통일) 5단계가 모두 완료**되었습니다.

## [1.4.75] - 2026-09-21

### Changed
- **스키마 정본을 Alembic 하나로 통일** — 그동안 스키마를 만드는 곳이 세 군데였습니다: `alembic/versions/`, `entrypoint.sh`의 수동 DDL, `main.py`의 `create_all()` + ALTER 안전망. 정본이 갈라져 실제로 장애가 났었습니다(v1.4.68: `products.release_year`가 배포 진입점에 반영되지 않아 목록 조회 500)
  - `entrypoint.sh` (200 → 158줄): 수동 DDL 15개 제거, Alembic 실행으로 대체
  - `main.py` (67줄 제거): `create_all()` + ALTER 안전망 4블록 제거
- **마이그레이션 모드 자동 판정** — 기존 배포 DB는 `create_all()`로 만들어져 `alembic_version`이 없습니다. 그 상태로 `upgrade`를 돌리면 첫 리비전에서 죽으므로, DB 상태를 보고 모드를 고릅니다. **수동 `stamp`가 필요 없습니다.**

  | DB 상태 | 동작 |
  |---|---|
  | 테이블 0개 | `alembic upgrade head` |
  | 테이블 있음 / 버전 없음 | `stamp head` → `upgrade head` |
  | `alembic_version` 있음 | `alembic upgrade head` |
  | 최신보다 오래된 DB | 누락 항목 출력 후 **exit 1** |

  마지막 항목을 둔 이유: 오래된 DB를 무조건 head로 stamp하면 **실제로는 없는 컬럼을 있다고 기록**하게 됩니다. 표본 검사(3개 테이블 + `products.release_year`, `users.email`, `filename_violations.classification`)로 조용한 오기록을 막습니다.

### Docs
- **`CLAUDE.md`에 Git/레지스트리 정책 명시** — 이 프로젝트는 **GitHub와 Docker Hub만** 사용합니다. Harbor·Gitea는 사용하지 않습니다. 전역 규칙(Harbor 기본)에 대한 의도적 예외이며, 1.4.69에서 같은 태그에 서로 다른 빌드가 올라간 사고가 계기입니다

### ⚠️ 주의
이번 릴리스부터 **Alembic 실패 = 앱 기동 실패**입니다. 이전에는 안전망이 덮어줬습니다. 문제 발생 시 이미지 태그를 `1.4.74`로 되돌리면 즉시 복구됩니다.

## [1.4.74] - 2026-09-21

### Fixed
- **배포 이미지에 Alembic 마이그레이션이 들어있지 않던 문제** — `Dockerfile`이 `./app`·`requirements.txt`·`entrypoint.sh`만 복사해서, 컨테이너 안에서 `alembic` 명령이 `No config file 'alembic.ini' found`로 실패했습니다
  - `alembic` 실행파일은 설치돼 있었으나 **실행할 대상이 없었습니다.** 즉 마이그레이션은 배포 환경에서 한 번도 실행 가능한 적이 없었고, 이것이 `entrypoint.sh`가 `ALTER TABLE`/`CREATE INDEX`를 직접 짜 넣고 `main.py`가 `create_all()` + ALTER 안전망을 두게 된 근본 원인입니다
  - `Dockerfile.prod`에는 해당 COPY가 이미 있었으나, CI가 빌드하는 `Dockerfile`에만 빠져 있었습니다

### Added
- **DB 마이그레이션** `adab022231f3` — Alembic 밖에서만 만들어지던 살아있는 테이블 3개(`activity_logs`, `product_videos`, `share_links`)를 Alembic으로 편입
  - **추가 전용**입니다. 자동 생성분의 파괴적 연산(죽은 테이블 삭제, 손수 만든 GIN 인덱스 삭제, `crawled_from` 컬럼 삭제)은 전부 제거했습니다
  - `entrypoint.sh`에만 있던 `idx_posts_title_trgm`, `idx_filename_violations_file_name_trgm`도 동일 이름 + `IF NOT EXISTS`로 추가
- `app/models/__init__.py`에 `ActivityLog` 등록 — 빠져 있어서 `alembic revision --autogenerate`가 `drop_table('activity_logs')`를 생성할 위험이 있었습니다

### Removed
- **죽은 코드 1,191줄 제거** (도달 가능성 검증 후)
  - `core/ai_metadata_old.py`(558), `core/metadata_enricher_old.py`(235), `core/bing_image_search.py`(97) — 임포트 0곳
  - `core/filename_standardizer.py`(270) — 죽은 `_old` 파일만 임포트, API 라우트 없음
  - `models/scan_history.py`(31) — 미사용 import 한 줄뿐. 실제 스캔 이력은 `scan_history.json` 파일
  - `products.crawled_from` 모델/스키마 필드 — 값을 쓰는 코드가 삭제된 `_old` 파일뿐, 프론트 참조 0건 (DB 컬럼 자체는 유지)
  - 백엔드 `print()` 27건 중 24건이 이 파일들에 있어 함께 해소되었습니다

### 배포 후 필요한 조치
운영 DB에는 `alembic_version` 테이블이 없습니다(`create_all()`로 만들어졌기 때문). 이 릴리스를 반영한 뒤 **한 번만** 실행하세요:
```
docker exec myapp-backend alembic stamp head
```
SQL을 실행하지 않고 "이 DB는 이미 최신"이라고 기록만 남깁니다. 이 작업 없이 `alembic upgrade head`를 돌리면 `relation "products" already exists`로 실패합니다.

## [1.4.73] - 2026-09-21

### Fixed
- **다운로드 이어받기(HTTP Range) 복구** — 프로덕션 빌드가 다시 X-Accel-Redirect 경로(`/api/download/{id}`)를 사용합니다. Nginx가 파일을 직접 서빙하므로 중단된 다운로드를 이어받을 수 있습니다
  - 전제 조건이 해소되어 되돌린 것입니다: 운영 NAS compose의 `frontend` 서비스에 `volumes:` 블록이 통째로 없어 Nginx가 라이브러리를 읽지 못했고, 그래서 v1.4.67~v1.4.71 동안 X-Accel 다운로드가 전부 404였습니다. backend에만 파일이 보여 스캔·목록은 정상이라 발견이 늦었습니다
  - backend와 동일한 라이브러리 폴더를 frontend에도 `:ro`로 마운트하고 컨테이너를 재생성해 확인했습니다

### Changed
- `frontend/src/utils/env.js` 주석에 전제 조건(frontend도 라이브러리를 마운트해야 함), 확인 명령(`docker exec myapp-frontend ls /app/data/library/`), 누락 시 증상을 명시했습니다

### Docs
- **docker-compose** 3개 파일의 라이브러리 추가 폴더 마운트 주석 정리 — backend/frontend 양쪽에 동일한 경고를 배치해 한쪽만 추가하는 실수를 막고, 예시를 실제 운영 구성(`/volume2/App`, `/volume3/App2`)으로 교체했습니다
  - `docker-compose.prod.yml`의 backend에는 예시 블록이 아예 없어 추가
  - `docker-compose.dev.yml`의 잘못된 예시 경로(`/library/NAS:ro`) 교정 — `SCAN_BASE_PATH`가 `/app/data/library`이므로 `/library/...`는 스캔되지 않습니다

## [1.4.72] - 2026-09-21

### Fixed
- **다운로드**: 운영에서 모든 파일 다운로드가 404로 실패하던 문제 복구 — 프론트엔드가 다시 백엔드 직접 스트리밍(`/api/download/direct/{id}`)을 사용하도록 되돌림
  - 원인은 X-Accel-Redirect 경로가 동작하려면 frontend 컨테이너의 Nginx가 라이브러리 파일을 직접 읽어야 하는데, 운영 frontend 컨테이너의 `/app/data/library`가 비어 있었던 것. backend는 같은 파일을 읽을 수 있어 `/direct`는 정상이었다
  - 실제 `myappstore-frontend:1.4.70` 이미지로 재현 검증: 파일이 있으면 200(+Range 요청 시 206), 빈 디렉터리면 운영과 동일한 404(Content-Length 153, Content-Disposition 존재)
  - Nginx 설정·경로 인코딩(한글/공백)·alias는 정상임을 확인 — 설정 문제가 아니라 파일 가시성 문제

### Changed
- **다운로드**: 위 조치로 다운로드 이어받기(HTTP Range)가 일시적으로 비활성화됨. frontend 컨테이너가 라이브러리를 보게 되면 `frontend/src/utils/env.js`의 주석대로 한 줄로 되돌릴 수 있다

### Added
- **운영**: NAS 재부팅 시 유실되는 라이브러리 바인드 마운트를 복구하는 스크립트 추가 (`scripts/synology-mount-library.sh`)
  - `/proc/mounts`를 직접 확인해 중복 마운트를 방지, 겹쳐 쌓인 마운트 감지 및 정리(`--umount`), 상태 확인(`--status`), 부팅 직후 볼륨 대기 지원
  - DSM 작업 스케줄러의 부팅-up 트리거에 root로 등록해 사용

## [1.4.71] - 2026-09-19

> 이 버전은 **git 태그가 없습니다**(버전 bump 커밋 `6f6cb8a`만 존재). Docker 이미지
> `1.4.71`은 Docker Hub와 Harbor에 정상적으로 존재하며, 소급 태깅은 해당 태그의
> 이미지를 현재 소스로 재빌드하게 되므로 의도적으로 공백으로 둡니다.

### Security
- **의존성**: PostgreSQL 클라이언트 보안 업데이트 — `psycopg2-binary` 2.9.9 → 2.9.13 (번들 libpq 16.0 → 17.11), CVE-2024-10977 / CVE-2025-12818 해소
- **docker-compose**: 3개 compose 파일 전부 postgres 이미지를 `15.19-alpine`으로 고정

## [1.4.70] - 2026-09-14

### Fixed
- **PWA**: 재배포 후 홈 화면에 추가한 PWA에서 제품/게시글 상세 페이지 클릭이 아무 반응 없이 멈추던 문제 수정
  - 원인: `GET /` 응답에 `Cache-Control` 헤더가 없어 브라우저가 휴리스틱 캐싱을 적용, 낡은 `index.html`이 가리키는 옛 해시 청크가 404가 되어 동적 import가 실패하고 vue-router가 이를 조용히 무시 (`index.html`의 `<meta http-equiv="Cache-Control">`은 브라우저의 캐시 판단에 쓰이지 않는다)
  - `nginx.conf`: `index.html`과 `manifest.json`에 `no-cache, must-revalidate`를 실제 HTTP 헤더로 전송
  - `nginx.conf`: `/assets/`에 `try_files $uri =404`를 적용해 없는 청크가 HTML로 응답되지 않도록 차단
  - `nginx.conf`: 전역 `error_page 404 /index.html` 제거 (`location /`의 `try_files`가 SPA 라우트를 이미 처리)
  - `router/index.js`: 청크 로드 실패 시 1회 하드 내비게이션으로 자가 복구 (10초 쿨다운)

### Changed
- **알림**: 디스코드 embed에서 제품 링크 제거 (썸네일·필드는 유지)

## [1.4.69] - 2026-09-14

### Added
- **알림**: 디스코드 웹훅 알림 추가 (설정 > 일반설정) — 새 앱이 등록되거나 기존 앱에 새 버전이 추가되면 디스코드 채널로 공지
  - 웹훅 URL 화이트리스트 검증(SSRF 방어), 메시지당 embed 10개 청킹, 커밋 완료 후 백그라운드 전송으로 스캔 응답 지연 없음
  - 관리자 전용 테스트 전송 엔드포인트 (`POST /api/notifications/discord/test`) — 저장된 웹훅을 사용
  - 웹훅 URL은 `SENSITIVE_FIELDS`로 등록되어 API 응답에서 항상 마스킹
  - 알림은 스캔 항목을 AI 매칭해 앱이 실제로 등록될 때 전송된다. 스케줄러 자동 스캔은 스캔 항목만 쌓으므로 알림을 발생시키지 않는다

## [1.4.68] - 2026-08-26

### Added
- **AI 제공자**: Claude(Anthropic) 메타데이터 생성 지원 추가 (설정 > 메타데이터 설정 > AI 모델 설정에서 선택 가능)
- **메타데이터 생성**: URL 또는 파일(txt/nfo/md/pdf) 원문을 소스로 사용하는 메타데이터 생성 엔드포인트 추가 - AI가 임의로 지어내지 않고 주어진 텍스트 안에서만 추출
- **스캔**: 스캔 폴더 내 설명 파일(.txt/.nfo/.md) 자동 감지 + 원클릭 메타데이터 생성 UI
- **신뢰도 배지**: 제조사/출시연도/구체적인 이름 여부 기반 규칙형 신뢰도 스코어링을 AI 검색 결과에 배지로 표시
- **제품 상세**: `release_year`(출시 연도) 필드 추가 - 같은 이름이지만 연도가 다른 소프트웨어(예: AutoCAD 2026 vs 2027)가 같은 제품으로 오매칭되는 문제의 구조적 개선
- **다운로드**: 브라우저 다운로드 중단 후 이어받기(HTTP Range / 206 Partial Content) 지원 - 문서화만 되어 있고 실제로는 연결되지 않았던 Nginx X-Accel-Redirect 구성을 정상화하여 Nginx가 파일을 직접 서빙
- **제품 상세**: "플러그인/스킨" 탭 추가 (패치 탭과 동일한 업로드/다운로드/설명 구조), 검색된 목록 페이지의 분류 옵션에도 추가

### Fixed
- **보안**: 관리자 API 응답(`GET /api/config/`)에 AI API 키가 평문으로 그대로 노출되던 문제 수정 - 항상 마스킹 처리
- **보안**: 백업 ZIP에 포함되는 config.json에서 API 키 등 민감 정보 제거
- **AI 매칭**: 파일명의 버전(예: v25.0)과 제품의 release_year(연도)처럼 서로 다른 종류의 값을 비교해 정상적인 후보까지 오탐 차단하던 버그 수정
- **DB**: `release_year` 컬럼 마이그레이션이 실제 배포 진입점(entrypoint.sh는 Alembic을 호출하지 않음)에는 적용되지 않아 목록 조회가 500 에러로 실패하던 문제 수정 - main.py의 스키마 안전망에 추가
- **정리**: 사용되지 않던 unmatched.py/UnmatchedItem 서브시스템(어디서도 라우팅되지 않던 죽은 코드) 제거

### Deployment
- **docker-compose**: `CLAUDE_API_KEY` 환경변수 추가 (선택사항 - Settings UI에서도 설정 가능)
- **docker-compose**: 다운로드 이어받기를 위해 frontend 컨테이너에 library 볼륨 읽기 전용 마운트(`./data:/app/data:ro`) 추가 필요
- **Nginx**: `frontend/nginx.conf`에 `/protected` internal location 추가 (X-Accel-Redirect 대상)

## [1.4.63] - 2026-08-02

### Fixed
- **보안**: 프로덕션 환경에서 전역 예외 핸들러가 응답에 Python traceback을 포함하던 문제 수정
- **보안**: 인증 없이 DB 스키마/row count/traceback을 노출하던 `/api/products/diag` 진단 엔드포인트 제거
- **보안**: 폴더 브라우저(`/api/filesystem/browse`, `/create-directory`)가 SCAN_BASE_PATH·등록된 스캔 폴더 밖의 임의 경로에 접근 가능하던 문제 수정 (경로 탐색 방지)
- **캐시**: 제품 삭제/버전 등록해제/삭제파일 정리 시 존재하지 않는 `"products:*"` 패턴으로 캐시를 무효화해 삭제된 제품이 최대 5분간 목록에 계속 노출되던 버그 수정 (`product_detail`, `search_suggestions` 캐시 누락분도 함께 보강)
- **매칭**: 연도/에디션이 다른 소프트웨어(예: AutoCAD 2026 vs 2027)가 AI 메타데이터의 title에서 연도가 생략될 경우 같은 제품으로 오인 매칭되던 버그 수정 (폴더명 기반 폴백 추출 + AI 프롬프트 보강)

### Changed
- **홈 화면 카테고리**: `/api/products/by-category`가 하드코딩된 9개 카테고리 대신 config.json 기반 카테고리 목록을 사용하도록 변경
- **캐시 무효화**: Redis `KEYS` 대신 `SCAN` 커서 사용 (대규모 캐시에서 Redis 블로킹 방지)

### Performance
- **검색**: products.title/subtitle/vendor에 pg_trgm GIN 인덱스 추가 (기존에는 실제로 존재하지 않아 ILIKE 검색이 매번 시퀀셜 스캔이었음)
- **DB**: `versions.product_id`에 인덱스 추가 (FK였지만 Postgres가 자동 인덱싱하지 않아 대부분의 조회 쿼리가 풀스캔이었음)
- **스캔**: 수동/자동 스캔 중 FastAPI 이벤트 루프가 블로킹되어 다른 API 요청이 응답하지 못하던 문제 수정 (동기 파일시스템 I/O를 스레드로 분리)

### Deployment
- **docker-compose**: 누락되어 있던 `VIDEOS_DIR`, `ATTACHMENTS_DIR` 환경변수 추가
- **DB 마이그레이션**: `a1b2c3d4e5f7` 리비전 추가 (pg_trgm GIN 인덱스, versions.product_id 인덱스) — 배포 시 `alembic upgrade head` 필요

## [1.4.56] - 2026-03-16

### Changed
- **사용자 관리**: 수정 버튼 제거, 비밀번호 버튼 → 비밀번호 초기화(랜덤 생성)로 변경
- **사용자 관리**: 신규 사용자 생성 시 활성 상태(is_active=True) 명시적 설정
- **푸터**: Discord 아이콘+텍스트 한 줄로 표시 (`inline-flex` 적용)
- **README**: 스크린샷 경로를 raw.githubusercontent.com 절대 URL로 변경
- **버전**: 1.4.56

## [1.4.54] - 2026-03-16

### Added
- **스크린샷**: README에 한국어/영어 스크린샷 섹션 추가 (screenshot/kor, screenshot/eng)
- **활동 로그 번역키**: `activityLog.actions.*` 14개 action 번역키 추가 (ko.js / en.js)

### Changed
- **검색된 목록**: 분류명 "제품" → "소프트웨어"로 변경
- **푸터**: Discord 링크 업데이트 (https://discord.gg/8amwMw2X)
- **README**: Bing Image Search → Google Custom Search(Image) 설명으로 변경
- **README**: 버전 뱃지 1.4.54로 업데이트

### Fixed
- **ProductDetail.vue**: `@/api/attachments.js` 동적 import 오류 → 상대 경로로 수정

## [1.4.13] - 2026-02-28

### Fixed
- **ProductDetail.vue**: `@/api/attachments.js` 동적 import 오류 수정 → 상대 경로로 변경

### Changed
- **검색된 목록 분류명**: "제품" → "소프트웨어" (ko.js / en.js)

## [1.4.12] - 2026-02-28

### Added
- **스캔 목록 (ScanList.vue)**: 파일 스캔 후 검색된 목록 화면 전면 개편
  - 상단 분류 탭 필터: 전체 / 제품 / 패치 / 언어팩 / 메뉴얼 / 업데이트
  - 분류별 통계 카드 (클릭으로 바로 필터 전환)
  - 각 항목에 분류 배지 + 드롭다운으로 수동 분류 변경 가능
  - AI 검색 버튼 (제품 분류일 때만 표시)
  - 패치/언어팩/메뉴얼/업데이트 등록 다이얼로그: 제품 검색 후 Attachment로 등록
- **자동 분류**: 스캔 시 파일명·폴더명 키워드 기반 자동 분류 (`core/classifier.py`)
- **제품 상세 탭 개편**: 자료실 탭 → 패치/언어팩/메뉴얼/업데이트 4개 탭으로 분리
- **버전→분류 변경**: 버전 탭에서 파일을 패치/언어팩/메뉴얼/업데이트로 재분류 (Version → Attachment 변환)
- **DB 마이그레이션**: `filename_violations.classification`, `classification_auto` 컬럼 추가
- **API 엔드포인트**: `/api/scan-items/` (기존 `/api/filename-violations/`과 하위 호환 유지)
  - `GET /api/scan-items/` - 분류/검색/페이지네이션 필터 지원
  - `GET /api/scan-items/stats` - 분류별 통계
  - `PATCH /api/scan-items/{id}/classify` - 수동 분류 변경
  - `POST /api/scan-items/{id}/register` - 분류에 따른 등록 처리
  - `POST /api/attachments/from-version/{version_id}` - 버전→첨부파일 변환

### Changed
- 네비게이션: 파일명 위반 목록 → 검색된 목록 (`/scan-list`)
- `Attachment.type` 값 정규화: `crack` → `patch`, 비표준 → `patch`

### Removed
- `unmatched.py` 백엔드 라우터 제거 (UnmatchedItem 기능 사용 중단)
- 일치/불일치 판단 UI, 해결됨 표시 기능 제거

## [1.4.0] - 2026-02-25

### Added
- **제품 공유 기능**: 모든 사용자가 제품을 외부에 안전하게 공유할 수 있는 기능 추가
  - 1회성 공유 링크 (사용 후 자동 만료)
  - 최대 5일 기간 제한 (사용자 선택 1~5일)
  - 8자리 랜덤 비밀번호 자동 생성 (대소문자+숫자 조합)
  - 비밀번호 5회 실패 시 링크 자동 잠금 (보안)
  - 사용자당 활성 링크 최대 20개 제한
  - IP 로깅으로 감사 추적
- **ShareLink DB 모델**: `share_links` 테이블 추가
- **공유 API** (`/api/share`):
  - `POST /create` - 공유링크 생성
  - `GET /my-links` - 내 공유링크 목록
  - `DELETE /{id}` - 공유링크 삭제
  - `GET /view/{token}` - 공유 페이지 정보 (비인증)
  - `POST /access/{token}` - 비밀번호 인증 및 제품 정보 반환 (비인증, 1회성)
  - `GET /admin/all` - 전체 목록 (관리자)
- **공유 버튼**: 제품 상세 페이지 헤더에 공유 버튼 추가 (모든 사용자)
- **ShareDialog.vue**: 공유링크 생성 다이얼로그 (기간 선택, 메모, 생성 결과 표시)
- **ShareView.vue**: 공유 접근 페이지 (`/share/:token`, 비인증)
- **ShareManage.vue**: 공유링크 관리 페이지 (`/my/share-links`)
- **사이드바/모바일 메뉴**: "내 공유링크" 메뉴 항목 추가
- **번역 키**: `share.*` 키를 ko.js/en.js에 추가

## [1.3.21] - 2026-02-24

### Fixed
- **401 리디렉션 루프 방지**: `frontend/src/api/client.js`의 401 핸들러가 공개 페이지(`/login`, `/register`, `/setup`)에 이미 있을 때 로그인 페이지로 리디렉션하지 않도록 수정 — 회원가입 페이지에서 발생하던 무한 리디렉션 루프 해소
- **회원가입 상태 확인 오류 처리 개선**: `frontend/src/views/Register.vue`에 "등록 마감"과 구별되는 별도의 오류 상태(`statusCheckFailed`) 추가, 재시도 버튼 추가, 상태 확인 로직을 재사용 가능한 함수로 리팩터링
- **등록 상태 API 캐싱 방지**: `backend/app/api/auth.py`의 registration-status 엔드포인트에 `Cache-Control: no-cache` 헤더 추가 — 브라우저 캐싱으로 인한 오래된 상태 반환 문제 해소

### Added
- **i18n 키 추가 (ko.js / en.js)**: `statusCheckFailedDesc` 및 `retry` 번역 키를 한국어/영어 로케일에 추가


## [1.3.20] - 2026-02-24

### Fixed
- **제품 버전 다운로드 안 되는 문제 수정**: `download()` 함수가 `localStorage`만 읽어 "로그인 상태 유지" 미선택 시 토큰이 null이 되어 401 오류 발생. `sessionStorage` fallback 추가
- **TipsWrite TinyMCE 이미지 업로드 동일 오류 수정**: 에디터 내 이미지 업로드 핸들러도 같은 `localStorage`-only 문제. `sessionStorage` fallback 추가

## [1.3.19] - 2026-02-24

### Fixed
- **시놀로지 Container Manager 이미지 업데이트 감지 수정**: Dockerfile에 OCI 표준 라벨(`org.opencontainers.image.*`) 추가. Container Manager가 버전·빌드일시·Git 커밋을 읽어 업데이트 여부를 올바르게 감지
- **GitHub Actions 빌드 메타데이터 전달**: `VERSION`·`BUILD_DATE`·`VCS_REF`를 build-args로 Dockerfile에 주입. Docker 이미지 라벨에 버전 정보 포함

## [1.3.18] - 2026-02-24

### Added
- **제품 상세 이전/다음 이동**: 헤더에 ◄ ► 버튼 추가 — 인접 제품으로 이동 가능. 버튼 비활성화 시 흐리게 표시, 호버 시 제품명 툴팁
- **모바일 스와이프 네비게이션**: 제품 상세 페이지에서 좌/우 스와이프(60px 이상)로 이전/다음 제품 이동. 수직 스크롤과 구분됨
- **모바일 인접 제품 표시줄**: 콘텐츠 상단에 이전/다음 제품명 표시 바 (모바일 전용, `lg:hidden`)
- **백엔드 `GET /products/{id}/adjacent`**: 이전(더 높은 id)/다음(더 낮은 id) 제품 정보 반환 엔드포인트

## [1.3.17] - 2026-02-24

### Fixed
- **팁&테크 목록 모바일 필터 2줄 레이아웃**: 카테고리/정렬 셀렉트가 모바일에서 세로로 쌓이던 문제 수정 — 1줄: 카테고리+정렬 나란히, 2줄: 검색창 전체 너비로 배치
- **TipsWrite 모바일 패딩 최적화**: 헤더/컨텐츠/폼 카드 고정 `px-8`/`p-8`을 모바일 반응형(`px-4 sm:px-8`, `p-4 sm:p-6 lg:p-8`)으로 변경. 헤더 취소 버튼 모바일에서 아이콘만 표시. 카테고리+공지 행 모바일 세로 스택 처리
- **TipsDetail 모바일 패딩/텍스트 최적화**: 헤더/포스트 카드/첨부파일/댓글 섹션 고정 패딩을 반응형으로 변경. 제목 `text-3xl` → `text-xl sm:text-2xl lg:text-3xl`. 스크랩 버튼 모바일 아이콘만 표시. 작성자/조회수 정보 모바일 세로 스택 처리

## [1.3.16] - 2026-02-23

### Fixed
- **모바일 검색창 상단 이동**: 하단 내비게이션의 검색 버튼 클릭 시 검색창이 하단 바 위에 표시되던 것을 화면 최상단에 고정되도록 변경. slide-down 애니메이션 및 iOS safe-area 대응
- **설정 - 메타데이터 API 키 모바일 오버플로우 수정**: 마스킹된 API 키 텍스트(`AIzaSy••`, `sk-••` 등)가 화면 너비를 초과하던 문제 수정. `min-w-0` + `truncate` 적용으로 말줄임 처리
- **설정 - 폴더 추가 안내문구 모바일 최적화**: 긴 명령어 코드(`-v /path/...`, `ln -s /path/...`)가 화면을 벗어나던 문제 수정. 코드 블록을 항목 아래 별도 줄에 배치하고 가로 스크롤로 처리

## [1.3.15] - 2026-02-23

### Fixed
- **로그인 상태 유지 30일 미작동 수정**: `.env`의 `ACCESS_TOKEN_EXPIRE_MINUTES=30`(분)이 기본값(30일)을 덮어써 항상 30분 후 로그아웃되던 문제 수정. 백엔드 로그인에 `remember_me` 파라미터 추가 — 체크 시 30일, 미체크 시 설정값 토큰 발급
- **API 클라이언트 sessionStorage 토큰 누락 수정**: request interceptor가 `localStorage`만 확인하여 세션 미유지 사용자의 API 요청에 Authorization 헤더 누락. `sessionStorage` fallback 추가 및 401 시 양쪽 스토리지 동시 정리
- **스캔 예외 추가 실패 수정**: 소프트웨어 확장자 파일에 `*.ext` 와일드카드 패턴 시도 시 백엔드 차단 오류 발생. 항상 파일명 자체를 예외 패턴으로 등록하도록 수정
- **파일명 위반 목록 위반 유형 레이블 수정**: 검색된 목록에 "언더스코어 과다" 등 위반 유형 메시지 표시 → "스캔됨" 파란 뱃지로 통일
- **스크린샷 슬롯별 URL 추가 수정**: v-for 내 이벤트 핸들러 `idx` 클로저 캡처 문제로 항상 슬롯1에만 저장되던 문제 수정. `activeUrlSlot` ref 사용으로 교체

## [1.3.14] - 2026-02-23

### Added
- **스크린샷 슬롯별 URL 교체**: 제품 상세 → 스크린샷 탭에서 이미지가 채워진 슬롯에도 링크(URL) 아이콘 버튼 추가 (호버 시 슬롯 좌하단 표시). 빈 슬롯/채워진 슬롯 모두 URL로 추가/교체 가능
- **`POST /images/download-screenshot-slot/{id}?slot={slot}&url={url}`** 엔드포인트: 특정 슬롯에 URL 이미지를 다운로드하여 저장 (기존 슬롯 파일 자동 삭제 후 교체)
- **`imagesApi.downloadScreenshotBySlot(productId, url, slot)`**: 프론트엔드 API 클라이언트 메서드 추가

### Changed
- **Bing Image Search 기본값 OFF**: `bingImageSearch` 기본값을 `true` → `false`로 변경 (설정에서 명시적으로 활성화해야 사용 가능)

## [1.3.13] - 2026-02-23

### Fixed
- **config.py 어드민 판별 enum 버그 수정**: `current_user.role != "admin"` (enum vs 문자열 비교 → 항상 True) → `current_user.role.value != "admin"` 으로 수정. 이 버그로 인해 어드민 포함 모든 사용자가 항상 마스킹된 config를 받았고, 로그인 후 API 키 "저장됨" 표시가 정상 동작하지 않던 근본 원인

### Changed
- **Bing Image Search ON/OFF 토글**: Settings → Metadata에서 이미지 검색 기능 자체를 활성화/비활성화할 수 있는 토글 추가. 토글 OFF 시 API 키 입력 영역 숨김 및 검색 엔드포인트에서 비활성화 응답 반환
- **config.json 마이그레이션**: 서버 시작 시 `googleApiKey`, `googleSearchEngineId` 필드 자동 삭제 및 `bingImageSearch: true` 기본값 추가

## [1.3.12] - 2026-02-23

### Changed
- **이미지 검색 엔진 교체**: Google Custom Search API → **Bing Image Search API** (Azure Cognitive Services)
  - Google Programmable Search Engine의 "전체 웹 검색" 옵션 폐지로 실질적 검색 불가 문제 해결
  - Bing은 전체 웹 이미지 검색 지원, 월 1,000건 무료 (F0 티어)
  - `backend/app/core/bing_image_search.py` 신규 생성
  - `images.py`: `GoogleImageSearcher` → `BingImageSearcher`, `bingApiKey` config 읽기
  - `config.py`: `SENSITIVE_FIELDS`에 `bingApiKey` 추가, 기본값에서 Google 키 제거
  - `Settings.vue`: Google API 키 + Search Engine ID 섹션 → Bing API 키 단일 입력으로 교체
  - `ko.js` / `en.js`: 로케일 문자열 Bing 기준으로 업데이트

## [1.3.11] - 2026-02-23

### Fixed
- **Google Image Search Misconfiguration Detection**: When Google Programmable Search Engine returns `totalResults: "0"` (indicating it is NOT configured for "Search the entire web"), now raises a clear error instead of showing "검색 결과가 없습니다". New message guides user to: (1) visit https://programmablesearchengine.google.com, (2) enable "전체 웹 검색", (3) enable "이미지 검색" feature.
- **Image search error propagation**: `GOOGLE_SEARCH_ENGINE_MISCONFIGURED` sentinel exception propagates from `google_image_search.py` through `images.py` with actionable setup instructions.

## [1.3.10] - 2026-02-23

### Fixed
- **AI Metadata 400 Error (Root Fix)**: `/metadata/test` endpoint was receiving API key from frontend — but `GET /api/config/metadata` returns `***` (masked) for non-admin users, so `***` was sent to Gemini → "API key not valid". Fixed: backend now ALWAYS reads API key directly from `config.json` (same as `/scan/test-ai-api` which worked). Frontend no longer sends API keys — only sends `ai_provider` / `ai_model` / `custom_prompt`.
- **MetadataTestDialog / ViolationAISearchDialog**: Removed `geminiApiKey`/`openaiApiKey` refs and config reads for sensitive fields; server sources keys from config internally.

## [1.3.9] - 2026-02-22

### Fixed
- **AI Matching Always Blocked**: `filename_violations.py` and `scan.py` were checking `metadata_config.get('useAI', False)` — but config stores `scanMethod: 'ai'`, never `useAI: true` → always `False` → all AI matching blocked with "AI 비활성화" error. Fixed to `scanMethod == 'ai'`
- **API Key Never Saved (First Entry)**: Settings.vue `saveMetadataSettings` sent `geminiApiKey: editingGeminiKey ? value : ''` — when no key existed yet (`hasGeminiKey=false`), `editingGeminiKey` was also `false` → sent `''` → backend preserved existing `''` → key never written. Fixed: also sends value when `!hasGeminiKey` (first-time entry)
- **ViolationAISearchDialog Mobile**: Error action buttons now stack vertically on mobile (`grid grid-cols-1 sm:grid-cols-3`); save button expands to full width on mobile; modal height constrained with `max-height: 100dvh`

## [1.3.8] - 2026-02-22

### Fixed
- **API Key Not Persisting (Root Fix)**: Completely removed Fernet encryption from config.py — was the root cause of all API key issues since Docker restart regenerated the encryption key making stored ENC: values unreadable
- **API Key Overwrite Prevention**: `update_config_section` now preserves existing non-empty sensitive fields when incoming value is empty string — prevents accidental key overwrite when saving other settings
- **Legacy ENC: Cleanup**: `_migrate_config()` now detects and clears unreadable ENC:-prefixed values on load (user prompted to re-enter)

### Changed
- **API Key UX in Settings**: API key fields now show "저장됨 ✓" green badge instead of actual key value — click "수정" button to change, "취소" to cancel — key is never sent to frontend after save, preventing exposure and accidental overwrite

## [1.3.7] - 2026-02-22

### Fixed
- **AI Matching 400 Error (Critical)**: `products.py` and `scan.py` regenerate-metadata endpoints were creating `AIMetadataGenerator()` without `provider` parameter, defaulting to OpenAI even when Gemini is configured — Gemini API key was sent to OpenAI endpoint → 400 "API key not valid"
- **Wrong API Key Field**: `products.py` read `'apiKey'` (old legacy field) instead of `'openaiApiKey'`/`'geminiApiKey'`; now reads provider-specific key
- **Wrong Method Call**: `generate_metadata()` (non-existent) → `generate_detailed_metadata()` with proper field mapping (`developer`→`vendor`, `description_short`→`description`)
- **Google Image Search ENC: Values**: `images.py` read `config.json` directly, bypassing ENC: decryption; now uses `load_config()` which handles legacy encrypted values

## [1.3.6] - 2026-02-22

### Fixed
- **API Key Not Saving**: Removed Fernet encryption from config storage — encryption key file didn't persist across Docker restarts causing decryption failures; API keys are now stored as plaintext in config.json (personal NAS use)
- **API Key Field Name Mismatch**: Default config used `apiKey` but code saved/read `openaiApiKey`; added auto-migration on load (`apiKey` → `openaiApiKey`) and updated default config
- **AI 400 Error in FilenameViolations**: Added `apiKey` fallback when reading OpenAI key so legacy configs still work after migration
- **docker-compose.yml Version Tag**: Changed hardcoded `1.2.1` → `latest` so Synology Container Manager detects image updates automatically

### Changed
- **TinyMCE Mobile Optimization (TipsDetail)**: Responsive prose size (`prose-sm/base/lg`), reduced padding on mobile, added CSS for table overflow-scroll, image max-width, code word-wrap, heading size scaling
- **TinyMCE Mobile Optimization (ProductDetail Install)**: Added `.tinymce-content` CSS class with same mobile-responsive rules for installation guide tab

## [1.3.5] - 2026-02-21

### Added
- **사이드바 통합검색**: 데스크탑 사이드바 상단에 검색바 추가, 검색어 입력 후 Enter로 스토어 페이지 이동
- **모바일 검색**: 모바일 하단 네비에 검색 아이콘 추가, 탭 시 검색 오버레이 표시 후 스토어 이동
- **스토어 URL 검색 파라미터**: `/discover?search=키워드` URL로 검색 상태 전달 지원
- **로그인 30일 유지**: 로그인 페이지에 "로그인 상태 유지 (30일)" 체크박스 추가 — 체크 시 localStorage, 미체크 시 sessionStorage 사용
- **스토어 NEW 배지**: 등록 후 3일 이내 신규 제품에 카드 좌상단 NEW 배지 표시

### Changed
- **Scraps 모바일 최적화**: 모바일에서 카드뷰 표시 (router-link 기반), 데스크탑은 기존 테이블뷰 유지
- **스크린샷 URL 추가 슬롯별 적용**: 전역 "URL로 추가" 버튼 제거, 각 빈 슬롯(1~4)에 개별 URL 입력창 추가
- **팁&테크 모바일 클릭 수정**: 모바일 카드 `<div @click>` → `<router-link>` 변경으로 iOS 클릭 딜레이 해소
- **Discover 무한스크롤 모바일 수정**: IntersectionObserver root를 `.main-content-area` 스크롤 컨테이너로 지정

## [1.3.4] - 2026-02-21

### Fixed
- **i18n Missing Keys in Product Edit**: Added `featuresHint`, `featuresPlaceholder`, `addRequirement`, `formatsHint`, `formatsPlaceholder` keys to `ko.js` and `en.js`; product detail edit mode now shows properly translated placeholder/hint text instead of raw key strings
- **Rescan After Product Delete**: `cleanup_deleted_files()` API and `_cleanup_deleted_files()` scanner function now reset `FilenameViolation.is_resolved=False` before deleting products (previously only `delete_product()` did this); also fixed `_add_scanned_file()` to reset orphaned violations (is_resolved=True but product_id=NULL after CASCADE) so files always re-appear in detected list after product deletion

## [1.3.3] - 2026-02-21

### Fixed
- **Settings Navigation from AI Error**: `sections.some()` was called on a Vue computed ref (not an array) in `onMounted`, throwing a `TypeError` that caused the entire settings initialization to fail — fixing this also resolves the next two issues
- **URL Overwrite After AI Error**: Because `onMounted` threw early, `accessUrl` and `apiUrl` were never updated from `config.json`, staying at their `VITE_APP_URL`/`VITE_BACKEND_URL` ENV defaults (e.g., `https://app.nuripc.kr`); now fixed by the above
- **API Key Disappears After AI Error**: Same root cause — config was never loaded, so metadata settings (including API key) displayed empty; now fixed
- **AI Search Dialog Positioning**: Changed `md:inset-x-auto` → `md:inset-x-0` so the modal has proper left/right anchors; with `mx-auto` and `max-w-4xl`, the dialog now centers horizontally on desktop

## [1.3.2] - 2026-02-21

### Fixed
- **Attachment Upload in Docker**: `ATTACHMENTS_DIR` was hardcoded to dev path (`/home/nuricom/.../attachments`); fixed to use `settings.ATTACHMENTS_DIR` and added env var to `docker-compose.yml` (`/app/data/attachments`)
- **API Key Singleton**: `_get_fernet()` now uses a module-level singleton (`_fernet_instance`) so the same Fernet key is used throughout the process lifetime, preventing key mismatch when file persistence fails
- **Scan Exclusion Validation**: Software file extensions (`.exe`, `.iso`, `.zip` etc.) can no longer be added to file pattern exclusions; validated in both frontend and backend

## [1.3.1] - 2026-02-21

### Fixed
- **Scanner SQL Transaction**: Each file's DB operation now wrapped in savepoint (`begin_nested()`), preventing `InFailedSqlTransaction` when one file fails
- **API Key Persistence**: Encryption key now stored in `data/.encryption_key` file (volume-mounted), survives Docker rebuilds; legacy SECRET_KEY-encrypted values auto-migrate on next save
- **Mobile Home Spacing**: Increased bottom padding from `pb-20` to `pb-28` to prevent bottom nav overlap
- **Docker Image URL**: TinyMCE external images now saved with relative path `/static/eximage/...` instead of full `http://localhost:8110/...`, fixing broken image links in Docker/reverse proxy environments
- **Login Token Expiry**: Fixed `ACCESS_TOKEN_EXPIRE_MINUTES` default in `docker-compose.yml` to 43200 (30 days)

## [1.3.0] - 2026-02-21

### Added
- **Infinite Scroll**: Store(Discover) page replaced pagination with IntersectionObserver-based infinite scroll
- **Product Detail Edit**: Features, System Requirements, Supported Formats now editable in product detail edit mode
- **Screenshot URL Add**: Added URL input to add screenshots by URL in product detail page
- **Same-folder File Grouping**: Files in the same folder are now recognized as the same product during AI matching
- **Duplicate Detection Message**: AI matching now shows clear duplicate info when a similar product already exists
- **Login Persistence**: Token expiry extended to 30 days; frontend validates JWT `exp` claim on startup
- **Screenshot URL API**: `addScreenshotByUrl()` function connects to `downloadScreenshots` API endpoint

### Changed
- **AI Search Text**: Renamed "AI 매칭" → "AI 검색" throughout UI (ko/en locales, tooltips, messages)
- **Tips Attachment Limits**: Max file size 10MB → 500MB, max file count 5 → 20 (frontend + backend)
- **Filename Rule Check Removed**: Scanner no longer validates filename naming conventions; only scan exclusion rules apply
- **Favorites Layout**: Reduced card size (6-column grid, 48px icon, compact padding)
- **Scraps Layout**: Reduced table row height and font size; date column hidden on mobile
- **Home Mobile Spacing**: Added `pb-20` bottom padding on mobile to prevent content cutoff

### Fixed
- **TinyMCE Edit Mode**: Content now displayed correctly when editing Tips posts (added `setContent()` after API load)
- **External Image Save**: Fixed httpx client with `follow_redirects=True, verify=False`; use `get_backend_url()` instead of empty `BACKEND_URL`
- **Product Rescan After Delete**: `delete_product()` now resets `FilenameViolation.is_resolved` to `False` so files can be rescanned
- **AI Matching Duplicate Order**: `create-product` response now includes `is_duplicate`/`duplicate_reason` fields; frontend shows info dialog on duplicates
- **Same-folder AI Matching**: Both `create-product` and `create-product-with-metadata` endpoints now group and match all unresolved violations in the same folder together

## [1.2.0] - 2026-02-10

### Added
- **Version-Aware AI Matching**: AI auto-matcher now differentiates products by version (e.g., Office 2003/2007/2010 as separate products)
  - Added `extract_version_from_title()` for year/version extraction
  - Pre-check existing products before making AI API calls to reduce costs
- **PWA Scroll Containment**: Fixed mobile PWA scroll bounce issues
  - Added `overscroll-behavior: none` and `position: fixed` on html
  - Safe area support with `env(safe-area-inset-bottom)` for iPhone home indicator
  - `touch-action: pan-x` on bottom nav to prevent vertical gesture conflicts
- **Missing i18n Key**: Added `openaiPricingTitle` translation key for both Korean and English
- **Standard PWA Meta Tag**: Added `mobile-web-app-capable` alongside existing Apple-specific tag

### Changed
- **Mobile Optimization**: Comprehensive responsive improvements across multiple pages
  - Home/Favorites/Scraps: Scrollable headers on mobile (no longer fixed), reduced banner height
  - FilenameViolations: Split action buttons for mobile/desktop, compact stats cards
  - ChangePassword: Responsive padding, back button, mobile-friendly inputs
  - Discover: Separated search input from sort/cleanup buttons on mobile
  - Settings: Registration settings flex-col layout on mobile
  - ViolationAISearchDialog: Full-screen on mobile with always-visible apply button
  - ImageManager: Responsive padding and text sizes

### Fixed
- **Image Upload Display**: API now returns relative paths instead of full URLs for proper proxy routing
  - Logo upload/download endpoints return `/static/...` paths
  - Frontend `getIconUrl()`/`getScreenshotUrl()` extract relative paths from legacy full URLs
- **AI Matching Duplicates**: Existing product check moved before AI call to prevent waste
- **Apply Button Not Clickable**: ViolationAISearchDialog modal restructured with flex column layout
- **Debug Console Logs**: Removed 4 debug `console.log` statements from Settings.vue

## [1.2.2-beta] - 2026-01-19

### Added
- **Patch Links Feature**: Added ability to add up to 5 related links in product detail page patches/cracks section
  - Admin can add/edit/delete links with title and URL
  - Links are displayed for all users with click-to-open functionality
  - Added translation keys for link feature in Korean and English
  - Added database migration for `patch_links` JSON field in products table

### Fixed
- **Scrap Date Localization**: Fixed hardcoded 'ko-KR' locale in Scraps page date formatting
  - Date format now follows current language setting (localStorage or browser language)
- **Database Migration**: Added Alembic migration and field validators for patch_links feature
  - Fixed "Exception in ASGI application" error
  - Added conversion logic between PatchLink objects and database JSON storage

### Technical Changes
- `backend/app/models/product.py`: Added `patch_links` JSON column
- `backend/app/schemas/product.py`: Added `PatchLink` schema and field validator
- `backend/app/api/products.py`: Added validation for max 5 links and object-to-dict conversion
- `frontend/src/views/ProductDetail.vue`: Added link management UI (183+ lines)
- `frontend/src/views/Scraps.vue`: Dynamic locale support for date formatting

## [1.2.1-beta] - 2026-01-19

### Fixed
- **Category Label Display**: Fixed category labels to display from config.json instead of translation system
  - Settings - Category Management now shows Korean labels correctly
  - Changed `getCategoryLabel()` function to prioritize config.json labels
  - Updated "Source" category label from "소스" to "소스코드"
  - Synchronized default config across backend and config.json

### Technical Changes
- `frontend/src/views/Settings.vue`: Modified `getCategoryLabel()` to use config.json labels first
- `data/config.json`: Updated Source category label
- `backend/app/api/config.py`: Synced default config

## [1.2.0-beta] - 2026-01-03

### Added
- **Complete i18n Support**: Full internationalization with auto language detection
  - Korean and English language support
  - Automatic language detection from browser settings
  - Language switcher in UI
  - All UI elements translated (2000+ translation keys)

### Changed
- Enhanced filename parsing rules for better AI matching
- Improved documentation with parsing patterns analysis (1,836 files analyzed)
- Simplified CORS settings in documentation

## [1.0.0] - 2025-12-29

### Features

#### Phase 1 - MVP
- Implemented Docker environment (FastAPI + Vue + PostgreSQL)
- Added basic file scanning from configured folders to database
- Implemented login and download functionality
- Created basic list view UI
- Added JWT authentication with OAuth2PasswordBearer
- Implemented first-run setup page for admin account creation

#### Phase 2 - Metadata & AI Integration
- Enhanced filename parsing algorithms (FilenameParser with noise word filtering)
- Integrated OpenAI API (GPT-4o-mini) for automatic metadata generation
- Implemented icon crawling and local storage (IconCache with httpx)
- Added fallback mechanism when AI is unavailable
- Created admin page with AI toggle option

#### Phase 3 - Enhancement
- Implemented auto-scan scheduler (APScheduler with cron expressions)
- Added scheduler management UI (AdminScheduler.vue)
- Created ScanHistory tracking model
- Implemented advanced search and filtering (category, vendor, search)
- Added autocomplete suggestions
- Optimized download with X-Accel-Redirect headers
- Implemented category-based product grouping (Netflix-style)
- Added scheduler persistence via Settings table

#### Additional Features
- Implemented favorites and scraps functionality
- Added Tips & Tech board with TinyMCE editor
- Created folder browser for scan path configuration
- Implemented mobile responsive layout
- Added dark mode support
- Implemented internationalization (i18n) with Vue I18n
- Added user management and invitation system
- Implemented metadata testing dialog
- Added filename violation tracking
- Created unmatched items management system

### Infrastructure
- Set up version management system
- Implemented automatic versioning with standard-version
- Added version API endpoints
- Created CHANGELOG automation

---

**Note**: This is the first stable release (v1.0.0). Previous development was tracked in phases but not versioned.
