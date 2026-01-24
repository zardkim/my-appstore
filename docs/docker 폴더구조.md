# Synology NAS Docker 폴더 구조

## 기본 폴더 구조

Synology NAS의 Container Manager(Docker)에서 MyApp Store를 실행할 때 다음과 같은 폴더 구조를 사용합니다:

```
/volume1/docker/myappstore/
├── db/              # PostgreSQL 데이터베이스 데이터
├── redis/           # Redis 캐시 데이터
└── data/            # 애플리케이션 데이터 (자동 생성되는 하위 폴더 포함)
    ├── library/     # 소프트웨어 파일 저장 위치 (사용자가 스캔할 폴더)
    ├── icons/       # 자동 생성: 다운로드한 아이콘
    ├── screenshots/ # 자동 생성: 스크린샷
    ├── eximage/     # 자동 생성: 게시판 이미지
    ├── patches/     # 자동 생성: 패치/크랙 파일
    ├── logs/        # 자동 생성: 애플리케이션 로그
    ├── attachments/ # 자동 생성: 첨부 파일
    └── config/      # 자동 생성: 설정 파일
```

## 폴더 설명

### `/volume1/docker/myappstore/db`
- PostgreSQL 데이터베이스 파일 저장
- 영구 데이터 보관
- **수동 생성 필요**

### `/volume1/docker/myappstore/redis`
- Redis 캐시 데이터 저장
- 캐시 영속성 (AOF)
- **수동 생성 필요**

### `/volume1/docker/myappstore/data`
- 모든 애플리케이션 데이터 저장
- **수동 생성 필요**
- 하위 폴더는 애플리케이션이 자동으로 생성

### `/volume1/docker/myappstore/data/library`
- 사용자가 스캔할 소프트웨어 파일 저장
- **수동 생성 필요**
- 이 폴더 또는 하위 폴더를 스캔 경로로 설정

## Backend/Frontend 소스 코드는?

**backend와 frontend 폴더는 볼륨 마운트하지 않습니다.**

이유:
- Docker 이미지 빌드 시 소스 코드가 이미지에 포함됨
- 프로덕션 환경에서는 소스 코드 마운트 불필요
- 개발 환경에서만 Hot Reload를 위해 마운트

## 초기 폴더 생성 명령어 (Synology SSH)

```bash
# Synology NAS에 SSH 접속 후 실행
sudo mkdir -p /volume1/docker/myappstore/{db,redis,data/library}
sudo chown -R 1000:1000 /volume1/docker/myappstore
```

또는 File Station에서 직접 생성:
1. File Station 열기
2. `docker` 폴더로 이동
3. 우클릭 → 새 폴더 생성 → `myappstore`
4. `myappstore` 내부에 `db`, `redis`, `data` 폴더 생성
5. `data` 내부에 `library` 폴더 생성

## NAS 소프트웨어 폴더 추가 마운트 (선택사항)

기존 NAS의 소프트웨어 폴더를 읽기 전용으로 추가 마운트:

```yaml
volumes:
  - /volume1/Software:/library/NAS:ro
```

이렇게 하면 `/library/NAS` 경로로 기존 소프트웨어에 접근 가능합니다.