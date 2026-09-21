#!/bin/bash
#
# MyApp Store - 라이브러리 바인드 마운트 (Synology DSM)
#
# /volume2/App  -> /volume1/docker/myappstore/data/library/App
# /volume3/App2 -> /volume1/docker/myappstore/data/library/App2
#
# NAS를 재부팅하면 이 바인드 마운트가 사라지고, 그 상태로 컨테이너가 재생성되면
# 라이브러리가 빈 폴더로 보여 다운로드가 404로 실패한다.
#
# 설치:
#   1) 이 파일을 NAS의 /volume1/docker/myappstore/scripts/ 에 복사
#   2) chmod +x /volume1/docker/myappstore/scripts/synology-mount-library.sh
#   3) DSM > 제어판 > 작업 스케줄러 > 생성 > 트리거된 작업 > 사용자 정의 스크립트
#      - 사용자: root
#      - 이벤트: 부팅-up
#      - 실행 명령: /volume1/docker/myappstore/scripts/synology-mount-library.sh
#
# 이 스크립트는 마운트만 한다. 컨테이너는 재시작하지 않는다.
# 수동 실행도 안전하다(멱등). 이미 마운트돼 있으면 건너뛴다.
#
#   ./synology-mount-library.sh            마운트 (필요한 것만)
#   ./synology-mount-library.sh --status   현재 상태만 출력
#   ./synology-mount-library.sh --umount   바인드 마운트 해제
#
set -u

# 작업 스케줄러는 PATH가 최소한이라 명시한다
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

LIBRARY_ROOT="/volume1/docker/myappstore/data/library"
LOG_FILE="/volume1/docker/myappstore/data/logs/mount-library.log"

# "원본:대상폴더명" 형식. 대상은 LIBRARY_ROOT 아래에 만들어진다.
MOUNT_PAIRS="
/volume2/App:App
/volume3/App2:App2
"

# 부팅 직후에는 볼륨이 아직 준비되지 않았을 수 있다
WAIT_TIMEOUT=120
WAIT_INTERVAL=5


log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg"
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
    echo "$msg" >> "$LOG_FILE" 2>/dev/null
}

# 대상 경로가 이미 마운트 지점인지 확인 (중복 마운트 방지의 핵심)
#
# mount --bind 는 같은 대상에 몇 번이든 겹쳐 쌓인다. 쌓이면 /proc/mounts에
# 같은 대상이 여러 줄 생기고, 해제할 때도 횟수만큼 umount 해야 한다.
# 그래서 마운트 전에 반드시 이 검사를 통과해야 한다.
#
# mountpoint(1)는 DSM에 없을 수 있어 /proc/mounts를 직접 본다.
# 경로에 공백이 있으면 /proc/mounts에 \040으로 적히므로 같은 형태로 바꿔 비교한다.
is_mounted() {
    local target="$1"
    local escaped
    escaped=$(printf '%s' "$target" | sed 's/ /\\040/g')
    awk -v t="$escaped" '$2 == t { found = 1 } END { exit !found }' /proc/mounts
}

# 같은 대상에 몇 겹이나 쌓여 있는지
mount_count() {
    local target="$1"
    local escaped
    escaped=$(printf '%s' "$target" | sed 's/ /\\040/g')
    awk -v t="$escaped" '$2 == t { n++ } END { print n + 0 }' /proc/mounts
}

wait_for_source() {
    local src="$1"
    local waited=0
    while [ ! -d "$src" ]; do
        if [ "$waited" -ge "$WAIT_TIMEOUT" ]; then
            return 1
        fi
        sleep "$WAIT_INTERVAL"
        waited=$((waited + WAIT_INTERVAL))
    done
    return 0
}

do_status() {
    log "=== 마운트 상태 ==="
    echo "$MOUNT_PAIRS" | while IFS=: read -r src name; do
        [ -z "${src:-}" ] && continue
        local target="$LIBRARY_ROOT/$name"
        local n
        n=$(mount_count "$target")
        if [ "$n" -eq 0 ]; then
            log "  [  ] $src -> $target  (마운트 안 됨, 항목 $(ls -1 "$target" 2>/dev/null | wc -l)개)"
        elif [ "$n" -eq 1 ]; then
            log "  [OK] $src -> $target  (항목 $(ls -1 "$target" 2>/dev/null | wc -l)개)"
        else
            log "  [!!] $src -> $target  중복 마운트 ${n}겹 - umount로 정리 필요"
        fi
    done
}

do_umount() {
    log "=== 바인드 마운트 해제 ==="
    echo "$MOUNT_PAIRS" | while IFS=: read -r src name; do
        [ -z "${src:-}" ] && continue
        local target="$LIBRARY_ROOT/$name"
        local n
        n=$(mount_count "$target")
        if [ "$n" -eq 0 ]; then
            log "  건너뜀: $target (마운트 안 됨)"
            continue
        fi
        # 겹쳐 쌓인 만큼 반복해서 해제한다
        while [ "$n" -gt 0 ]; do
            if umount "$target" 2>/dev/null; then
                log "  해제: $target (남은 ${n}겹 중 1겹)"
            else
                log "  해제 실패: $target - 사용 중일 수 있음 (컨테이너 정지 후 재시도)"
                break
            fi
            n=$(mount_count "$target")
        done
    done
}

do_mount() {
    log "=== 라이브러리 바인드 마운트 시작 ==="

    if [ "$(id -u)" -ne 0 ]; then
        log "ERROR: root 권한이 필요하다 (작업 스케줄러에서 사용자를 root로 설정할 것)"
        exit 1
    fi

    if [ ! -d "$LIBRARY_ROOT" ]; then
        log "ERROR: 라이브러리 경로가 없다: $LIBRARY_ROOT"
        exit 1
    fi

    local mounted_any=0
    local failed=0

    # while 루프가 서브셸에서 돌면 변수가 안 남으므로 임시 파일로 결과를 모은다
    local result_file
    result_file=$(mktemp)

    echo "$MOUNT_PAIRS" | while IFS=: read -r src name; do
        [ -z "${src:-}" ] && continue
        target="$LIBRARY_ROOT/$name"

        # 1) 이미 마운트돼 있으면 아무것도 하지 않는다 (중복 방지)
        if is_mounted "$target"; then
            n=$(mount_count "$target")
            if [ "$n" -gt 1 ]; then
                log "  경고: $target 에 ${n}겹 중복 마운트됨 - --umount 후 재실행 권장"
            else
                log "  이미 마운트됨, 건너뜀: $src -> $target"
            fi
            continue
        fi

        # 2) 원본 볼륨이 준비될 때까지 대기 (부팅 직후 대비)
        if ! wait_for_source "$src"; then
            log "  ERROR: 원본이 ${WAIT_TIMEOUT}초 안에 나타나지 않음: $src"
            echo "failed" >> "$result_file"
            continue
        fi

        # 3) 대상 폴더 준비
        if [ ! -d "$target" ]; then
            mkdir -p "$target" || {
                log "  ERROR: 대상 폴더 생성 실패: $target"
                echo "failed" >> "$result_file"
                continue
            }
            log "  대상 폴더 생성: $target"
        fi

        # 4) 대상이 비어있지 않으면 경고 (바인드하면 기존 내용이 가려진다)
        if [ -n "$(ls -A "$target" 2>/dev/null)" ]; then
            log "  경고: $target 이 비어있지 않다 - 마운트하면 기존 내용이 가려진다"
        fi

        # 5) 바인드 마운트
        if mount --bind "$src" "$target"; then
            log "  마운트 성공: $src -> $target"
            echo "mounted" >> "$result_file"
        else
            log "  ERROR: 마운트 실패: $src -> $target"
            echo "failed" >> "$result_file"
        fi
    done

    # grep -c 는 매치가 없으면 "0"을 출력하고 exit 1 이다.
    # "|| echo 0" 을 붙이면 0이 두 번 출력되므로 붙이지 않는다.
    mounted_any=$(grep -c '^mounted$' "$result_file" 2>/dev/null)
    failed=$(grep -c '^failed$' "$result_file" 2>/dev/null)
    mounted_any=${mounted_any:-0}
    failed=${failed:-0}
    rm -f "$result_file"

    # 참고: 컨테이너 기동 후 호스트에서 만든 바인드 마운트는 컨테이너 안에서
    # 보이지 않는다(마운트 전파가 private). 이 스크립트는 마운트만 하고
    # 컨테이너는 건드리지 않으므로, 이미 떠 있는 컨테이너에 반영하려면
    # 직접 재시작해야 한다.
    if [ "$mounted_any" -gt 0 ]; then
        log "  새로 마운트: ${mounted_any}건"
    else
        log "  새로 마운트된 항목 없음"
    fi

    if [ "$failed" -gt 0 ]; then
        log "=== 완료 (실패 ${failed}건) ==="
        exit 1
    fi
    log "=== 완료 ==="
}


case "${1:-}" in
    --status) do_status ;;
    --umount) do_umount ;;
    "")       do_mount ;;
    *)        echo "사용법: $0 [--status|--umount]"; exit 2 ;;
esac
