"""
샘플 데이터 생성 스크립트
- 스토어 (Discover) 제품 20개 + 버전
- 검색된 목록 (ScanList) 스캔 항목 30개 (분류별 골고루)

실행: python3 scripts/seed_sample_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# .env 수동 로드
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, _, v = line.partition('=')
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

DB_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/myappstore')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()

# ─── 스토어 제품 샘플 데이터 ───────────────────────────────────────

PRODUCTS = [
    {
        "title": "Adobe Photoshop 2024",
        "subtitle": "포토샵 2024",
        "vendor": "Adobe Inc.",
        "category": "Graphics",
        "description": "세계 최고의 이미지 편집 소프트웨어. 사진 보정, 디지털 아트, 3D 디자인까지 지원.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Adobe_Photoshop_CC_icon.svg/512px-Adobe_Photoshop_CC_icon.svg.png",
        "license_type": "Commercial",
        "platform": "Windows, macOS",
        "official_website": "https://www.adobe.com/products/photoshop.html",
        "folder": "/library/Adobe/Photoshop_2024",
        "versions": [
            ("v25.9.0", "Adobe_Photoshop_2024_v25.9.0_x64.exe", 4_200_000_000),
            ("v25.8.0", "Adobe_Photoshop_2024_v25.8.0_x64.exe", 4_150_000_000),
        ],
    },
    {
        "title": "Microsoft Office 365",
        "subtitle": "오피스 365",
        "vendor": "Microsoft Corporation",
        "category": "Office",
        "description": "Word, Excel, PowerPoint 등 업무 생산성 도구 모음.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Microsoft_Office_logo_%282019%E2%80%93present%29.svg/512px-Microsoft_Office_logo_%282019%E2%80%93present%29.svg.png",
        "license_type": "Subscription",
        "platform": "Windows, macOS",
        "official_website": "https://www.microsoft.com/microsoft-365",
        "folder": "/library/Microsoft/Office_365",
        "versions": [
            ("v16.0.17628", "Microsoft_Office_365_2024_x64.iso", 3_800_000_000),
        ],
    },
    {
        "title": "Visual Studio Code",
        "subtitle": "VS Code",
        "vendor": "Microsoft Corporation",
        "category": "Development",
        "description": "경량 오픈소스 코드 에디터. 다양한 언어와 확장 프로그램 지원.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Visual_Studio_Code_1.35_icon.svg/512px-Visual_Studio_Code_1.35_icon.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://code.visualstudio.com",
        "folder": "/library/Microsoft/VSCode",
        "versions": [
            ("v1.85.2", "VSCodeSetup-x64-1.85.2.exe", 102_400_000),
            ("v1.84.0", "VSCodeSetup-x64-1.84.0.exe", 100_000_000),
        ],
    },
    {
        "title": "7-Zip",
        "subtitle": "7집",
        "vendor": "Igor Pavlov",
        "category": "Utility",
        "description": "고압축률을 자랑하는 무료 오픈소스 파일 압축 프로그램.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/7-Zip_Logo.svg/512px-7-Zip_Logo.svg.png",
        "license_type": "Free",
        "platform": "Windows",
        "official_website": "https://www.7-zip.org",
        "folder": "/library/Utility/7-Zip",
        "versions": [
            ("v24.08", "7z2408-x64.exe", 1_600_000),
            ("v23.01", "7z2301-x64.exe", 1_500_000),
        ],
    },
    {
        "title": "VLC Media Player",
        "subtitle": "VLC 미디어 플레이어",
        "vendor": "VideoLAN",
        "category": "Media",
        "description": "거의 모든 멀티미디어 파일을 재생할 수 있는 무료 오픈소스 미디어 플레이어.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/VLC_Icon.svg/512px-VLC_Icon.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://www.videolan.org",
        "folder": "/library/Media/VLC",
        "versions": [
            ("v3.0.21", "vlc-3.0.21-win64.exe", 41_000_000),
        ],
    },
    {
        "title": "AutoCAD 2024",
        "subtitle": "오토캐드 2024",
        "vendor": "Autodesk",
        "category": "Engineering",
        "description": "2D/3D CAD 설계 소프트웨어. 건축, 기계, 토목 설계의 표준 도구.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Autocad_2024_logo.svg/512px-Autocad_2024_logo.svg.png",
        "license_type": "Commercial",
        "platform": "Windows",
        "official_website": "https://www.autodesk.com/products/autocad",
        "folder": "/library/Autodesk/AutoCAD_2024",
        "versions": [
            ("v24.3", "AutoCAD_2024_English_Win_64bit.exe", 3_500_000_000),
        ],
    },
    {
        "title": "WinRAR",
        "subtitle": "윈라",
        "vendor": "RARLAB",
        "category": "Utility",
        "description": "RAR 및 ZIP 포맷을 지원하는 강력한 파일 압축/해제 프로그램.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/WinRAR.svg/512px-WinRAR.svg.png",
        "license_type": "Trial",
        "platform": "Windows",
        "official_website": "https://www.rarlab.com",
        "folder": "/library/Utility/WinRAR",
        "versions": [
            ("v7.01", "winrar-x64-701.exe", 3_600_000),
            ("v6.24", "winrar-x64-624.exe", 3_500_000),
        ],
    },
    {
        "title": "Notepad++",
        "subtitle": "노트패드++",
        "vendor": "Don Ho",
        "category": "Development",
        "description": "무료 오픈소스 텍스트/코드 에디터. 다양한 프로그래밍 언어 구문 강조 지원.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Notepad%2B%2B_Logo.svg/512px-Notepad%2B%2B_Logo.svg.png",
        "license_type": "Free",
        "platform": "Windows",
        "official_website": "https://notepad-plus-plus.org",
        "folder": "/library/Development/Notepad++",
        "versions": [
            ("v8.6.7", "npp.8.6.7.Installer.x64.exe", 4_200_000),
        ],
    },
    {
        "title": "DaVinci Resolve",
        "subtitle": "다빈치 리졸브",
        "vendor": "Blackmagic Design",
        "category": "Media",
        "description": "전문가용 영상 편집 및 색보정 소프트웨어. 무료 버전도 강력한 기능 제공.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/DaVinci_Resolve_17_logo.svg/512px-DaVinci_Resolve_17_logo.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://www.blackmagicdesign.com/products/davinciresolve",
        "folder": "/library/Media/DaVinci_Resolve",
        "versions": [
            ("v19.0.1", "DaVinci_Resolve_19.0.1_Windows.zip", 5_900_000_000),
        ],
    },
    {
        "title": "Malwarebytes",
        "subtitle": "말웨어바이트",
        "vendor": "Malwarebytes Inc.",
        "category": "Security",
        "description": "악성코드 탐지 및 제거 전문 보안 프로그램.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Malwarebytes_logo.svg/512px-Malwarebytes_logo.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS",
        "official_website": "https://www.malwarebytes.com",
        "folder": "/library/Security/Malwarebytes",
        "versions": [
            ("v5.1.4", "MBSetup.exe", 80_000_000),
        ],
    },
    {
        "title": "Blender",
        "subtitle": "블렌더",
        "vendor": "Blender Foundation",
        "category": "Graphics",
        "description": "무료 오픈소스 3D 모델링, 애니메이션, 렌더링 소프트웨어.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Blender_logo_no_text.svg/512px-Blender_logo_no_text.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://www.blender.org",
        "folder": "/library/Graphics/Blender",
        "versions": [
            ("v4.1.1", "blender-4.1.1-windows-x64.msi", 780_000_000),
            ("v4.0.2", "blender-4.0.2-windows-x64.msi", 760_000_000),
        ],
    },
    {
        "title": "Git",
        "subtitle": "깃",
        "vendor": "Software Freedom Conservancy",
        "category": "Development",
        "description": "분산 버전 관리 시스템. 소스코드 이력 추적 및 협업 도구.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Git-logo.svg/512px-Git-logo.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://git-scm.com",
        "folder": "/library/Development/Git",
        "versions": [
            ("v2.44.0", "Git-2.44.0-64-bit.exe", 62_000_000),
        ],
    },
    {
        "title": "FileZilla",
        "subtitle": "파일질라",
        "vendor": "FileZilla Project",
        "category": "Network",
        "description": "FTP/SFTP/FTPS 파일 전송 클라이언트. 드래그앤드롭 인터페이스 지원.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/FileZilla_logo.svg/512px-FileZilla_logo.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://filezilla-project.org",
        "folder": "/library/Network/FileZilla",
        "versions": [
            ("v3.66.5", "FileZilla_3.66.5_win64-setup.exe", 12_000_000),
        ],
    },
    {
        "title": "Substance Painter",
        "subtitle": "서브스턴스 페인터",
        "vendor": "Adobe Inc.",
        "category": "Graphics",
        "description": "3D 텍스처 페인팅 및 머티리얼 제작 소프트웨어.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Adobe_Substance_3D_Painter_icon.svg/512px-Adobe_Substance_3D_Painter_icon.svg.png",
        "license_type": "Commercial",
        "platform": "Windows, macOS",
        "official_website": "https://www.adobe.com/products/substance3d-painter.html",
        "folder": "/library/Adobe/Substance_Painter_2024",
        "versions": [
            ("v10.1.0", "Substance_3D_Painter_10.1.0_Win64.exe", 2_100_000_000),
        ],
    },
    {
        "title": "PotPlayer",
        "subtitle": "팟플레이어",
        "vendor": "Kakao Corp.",
        "category": "Media",
        "description": "국산 강력한 멀티미디어 플레이어. 다양한 코덱 내장, 자막 지원.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/PotPlayer_logo.png/128px-PotPlayer_logo.png",
        "license_type": "Free",
        "platform": "Windows",
        "official_website": "https://potplayer.daum.net",
        "folder": "/library/Media/PotPlayer",
        "versions": [
            ("v231201", "PotPlayerSetup64.exe", 22_000_000),
        ],
    },
    {
        "title": "GIMP",
        "subtitle": "짐프",
        "vendor": "GIMP Development Team",
        "category": "Graphics",
        "description": "무료 오픈소스 이미지 편집기. Photoshop의 무료 대안.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/The_GIMP_icon_-_gnome.svg/512px-The_GIMP_icon_-_gnome.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://www.gimp.org",
        "folder": "/library/Graphics/GIMP",
        "versions": [
            ("v2.10.36", "gimp-2.10.36-setup.exe", 260_000_000),
        ],
    },
    {
        "title": "OBS Studio",
        "subtitle": "OBS 스튜디오",
        "vendor": "OBS Project",
        "category": "Media",
        "description": "무료 오픈소스 방송 및 화면 녹화 소프트웨어.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/OBS_Studio_Logo.svg/512px-OBS_Studio_Logo.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://obsproject.com",
        "folder": "/library/Media/OBS_Studio",
        "versions": [
            ("v30.1.2", "OBS-Studio-30.1.2-Windows.exe", 360_000_000),
        ],
    },
    {
        "title": "MySQL Workbench",
        "subtitle": "MySQL 워크벤치",
        "vendor": "Oracle Corporation",
        "category": "Development",
        "description": "MySQL 데이터베이스 설계, 개발, 관리를 위한 통합 GUI 도구.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/en/thumb/6/62/MySQL.svg/512px-MySQL.svg.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://www.mysql.com/products/workbench/",
        "folder": "/library/Development/MySQL_Workbench",
        "versions": [
            ("v8.0.36", "mysql-workbench-community-8.0.36-winx64.msi", 47_000_000),
        ],
    },
    {
        "title": "HandBrake",
        "subtitle": "핸드브레이크",
        "vendor": "HandBrake Team",
        "category": "Media",
        "description": "무료 오픈소스 동영상 변환 프로그램. 다양한 포맷 지원.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/HandBrake_Icon.png/128px-HandBrake_Icon.png",
        "license_type": "Free",
        "platform": "Windows, macOS, Linux",
        "official_website": "https://handbrake.fr",
        "folder": "/library/Media/HandBrake",
        "versions": [
            ("v1.7.3", "HandBrake-1.7.3-x86_64-Win_GUI.exe", 18_000_000),
        ],
    },
    {
        "title": "WinSCP",
        "subtitle": "윈SCP",
        "vendor": "Martin Přikryl",
        "category": "Network",
        "description": "Windows용 무료 FTP/SFTP/SCP 클라이언트. 탐색기 스타일 인터페이스.",
        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/WinSCP_Logo.png/128px-WinSCP_Logo.png",
        "license_type": "Free",
        "platform": "Windows",
        "official_website": "https://winscp.net",
        "folder": "/library/Network/WinSCP",
        "versions": [
            ("v6.3.4", "WinSCP-6.3.4-Setup.exe", 14_000_000),
        ],
    },
]

# ─── 스캔 항목 샘플 데이터 ────────────────────────────────────────

SCAN_ITEMS = [
    # 제품 분류 (product)
    ("Adobe_Illustrator_2024_v28.0_x64.exe",     "/library/Adobe/Illustrator_2024",     "product"),
    ("CorelDRAW_X8_Full_Setup.exe",              "/library/Corel/CorelDRAW_X8",         "product"),
    ("Premiere_Pro_2024_v24.0_x64.exe",          "/library/Adobe/Premiere_Pro_2024",    "product"),
    ("After_Effects_2024_v24.0.exe",             "/library/Adobe/After_Effects_2024",   "product"),
    ("Sony_Vegas_Pro_21_Setup.exe",              "/library/Sony/Vegas_Pro_21",          "product"),
    ("FL_Studio_21.2_Full_Setup.exe",            "/library/Image_Line/FL_Studio_21",    "product"),
    ("Ableton_Live_11_Suite_Setup.exe",          "/library/Ableton/Live_11_Suite",      "product"),
    ("Steinberg_Cubase_13_Pro_Setup.exe",        "/library/Steinberg/Cubase_13_Pro",    "product"),
    ("Reaper_v7.04_x64.exe",                     "/library/Cockos/Reaper_7",            "product"),
    ("DiskGenius_Professional_5.6.iso",          "/library/Eassos/DiskGenius_5",        "product"),

    # 패치 분류 (patch)
    ("Adobe_Photoshop_2024_Patch_v2.exe",        "/library/Adobe/Photoshop_2024",       "patch"),
    ("CorelDRAW_X8_KeyGen.exe",                  "/library/Corel/CorelDRAW_X8",         "patch"),
    ("Office_2021_Activator.exe",                "/library/Microsoft/Office_2021",      "patch"),
    ("WinRAR_7_Keygen.exe",                      "/library/Utility/WinRAR",             "patch"),
    ("Vegas_Pro_21_Crack.zip",                   "/library/Sony/Vegas_Pro_21",          "patch"),

    # 언어팩 분류 (language_pack)
    ("Adobe_Photoshop_2024_Korean_lang.zip",     "/library/Adobe/Photoshop_2024",       "language_pack"),
    ("FL_Studio_21_Korean_langpack.zip",         "/library/Image_Line/FL_Studio_21",    "language_pack"),
    ("Vegas_Pro_21_ko_KR_language.zip",          "/library/Sony/Vegas_Pro_21",          "language_pack"),
    ("DaVinci_Resolve_19_KOR_language.zip",      "/library/Media/DaVinci_Resolve",      "language_pack"),
    ("Blender_4.1_ko_translation.zip",           "/library/Graphics/Blender",           "language_pack"),

    # 메뉴얼 분류 (manual)
    ("Adobe_Photoshop_2024_Manual_KO.pdf",       "/library/Adobe/Photoshop_2024",       "manual"),
    ("AutoCAD_2024_Reference_Guide.pdf",         "/library/Autodesk/AutoCAD_2024",      "manual"),
    ("DaVinci_Resolve_19_Manual_EN.pdf",         "/library/Media/DaVinci_Resolve",      "manual"),
    ("Blender_4.1_User_Manual.pdf",              "/library/Graphics/Blender",           "manual"),
    ("FL_Studio_21_Getting_Started.pdf",         "/library/Image_Line/FL_Studio_21",    "manual"),

    # 업데이트 분류 (update)
    ("Adobe_Photoshop_2024_Update_25.9.1.exe",   "/library/Adobe/Photoshop_2024",       "update"),
    ("Office_365_Cumulative_Update_Feb2024.msu", "/library/Microsoft/Office_365",       "update"),
    ("AutoCAD_2024_SP1_Update.exe",              "/library/Autodesk/AutoCAD_2024",      "update"),
    ("Blender_4.1.1_Bugfix_Update.zip",          "/library/Graphics/Blender",           "update"),
    ("VLC_3.0.21_Security_Update.exe",           "/library/Media/VLC",                  "update"),
]


def run():
    from app.models.product import Product
    from app.models.version import Version
    from app.models.filename_violation import FilenameViolation

    print("=" * 60)
    print("샘플 데이터 생성 시작")
    print("=" * 60)

    # ─ 1. migration 확인 ────────────────────────────────────────
    try:
        db.execute(text("SELECT classification FROM filename_violations LIMIT 1"))
        print("✓ DB 마이그레이션 확인 완료 (classification 컬럼 존재)")
    except Exception:
        print("⚠  filename_violations 테이블에 classification 컬럼이 없습니다.")
        print("   다음 명령어로 마이그레이션을 실행하세요:")
        print("   cd backend && alembic upgrade head")
        print("")
        print("   또는 DB에 직접 컬럼을 추가합니다...")
        try:
            db.execute(text("""
                ALTER TABLE filename_violations
                  ADD COLUMN IF NOT EXISTS classification VARCHAR(20) NOT NULL DEFAULT 'product',
                  ADD COLUMN IF NOT EXISTS classification_auto BOOLEAN NOT NULL DEFAULT TRUE
            """))
            db.commit()
            print("   ✓ 컬럼 추가 완료")
        except Exception as e2:
            print(f"   ✗ 컬럼 추가 실패: {e2}")
            db.rollback()
            return

    # ─ 2. 스토어 제품 생성 ────────────────────────────────────────
    print("\n[1/2] 스토어 제품 생성 중...")
    created_products = 0
    skipped_products = 0

    for p in PRODUCTS:
        # 이미 존재하는지 확인 (folder_path 기준)
        existing = db.query(Product).filter(Product.folder_path == p["folder"]).first()
        if existing:
            skipped_products += 1
            continue

        product = Product(
            title=p["title"],
            subtitle=p.get("subtitle", ""),
            vendor=p["vendor"],
            category=p["category"],
            description=p["description"],
            icon_url=p.get("icon_url", ""),
            license_type=p.get("license_type", ""),
            platform=p.get("platform", "Windows"),
            official_website=p.get("official_website", ""),
            folder_path=p["folder"],
            release_date="2024",
            features=[f"{p['title']} 주요 기능 1", f"{p['title']} 주요 기능 2", "멀티 플랫폼 지원"],
            system_requirements={"OS": "Windows 10/11 64-bit", "RAM": "8GB 이상", "Storage": "10GB 이상"},
        )
        db.add(product)
        db.flush()  # ID 생성

        # 버전 추가
        for ver_name, file_name, file_size in p.get("versions", []):
            file_path = f"{p['folder']}/{file_name}"
            existing_ver = db.query(Version).filter(Version.file_path == file_path).first()
            if not existing_ver:
                ver = Version(
                    product_id=product.id,
                    version_name=ver_name,
                    file_name=file_name,
                    file_path=file_path,
                    file_size=file_size,
                    release_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                )
                db.add(ver)

        created_products += 1
        print(f"  + {p['title']}")

    db.commit()
    print(f"  → 생성: {created_products}개, 건너뜀(이미 존재): {skipped_products}개")

    # ─ 3. 스캔 항목 생성 ────────────────────────────────────────
    print("\n[2/2] 스캔 항목 생성 중...")
    created_items = 0
    skipped_items = 0

    for file_name, folder_path, classification in SCAN_ITEMS:
        # 이미 존재하는지 확인
        existing = db.query(FilenameViolation).filter(
            FilenameViolation.folder_path == folder_path,
            FilenameViolation.file_name == file_name,
        ).first()
        if existing:
            skipped_items += 1
            continue

        item = FilenameViolation(
            folder_path=folder_path,
            file_name=file_name,
            violation_type="scanned",
            violation_details="스캔된 파일",
            is_resolved=False,
            classification=classification,
            classification_auto=True,
            created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
        )
        db.add(item)
        created_items += 1
        print(f"  + [{classification:13s}] {file_name}")

    db.commit()
    print(f"  → 생성: {created_items}개, 건너뜀(이미 존재): {skipped_items}개")

    # ─ 결과 통계 ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    from sqlalchemy import func, case
    total_products = db.query(Product).count()
    total_scans = db.query(FilenameViolation).filter(FilenameViolation.is_resolved == False).count()

    by_class = db.execute(text("""
        SELECT classification, COUNT(*) as cnt
        FROM filename_violations
        WHERE is_resolved = FALSE
        GROUP BY classification
        ORDER BY cnt DESC
    """)).fetchall()

    print(f"✓ 총 제품 수: {total_products}개")
    print(f"✓ 총 스캔 항목: {total_scans}개")
    print("  분류별:")
    for row in by_class:
        print(f"    {row[0]:15s}: {row[1]}개")
    print("=" * 60)
    print("완료!")


if __name__ == "__main__":
    try:
        run()
    finally:
        db.close()
