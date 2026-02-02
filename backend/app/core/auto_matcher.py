"""
통합 AI 자동 매칭 로직
모든 매칭 작업에서 동일한 로직을 사용하도록 통합
"""
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.filename_violation import FilenameViolation
from app.models.product import Product
from app.models.version import Version
from app.core.ai_metadata import AIMetadataGeneratorV2 as AIMetadataGenerator
from app.core.parser import FilenameParser
from app.core.redis_cache import invalidate_cache


async def match_violations_to_products(
    db: Session,
    violations: List[FilenameViolation],
    ai_provider: str,
    ai_model: str,
    api_key: str,
    skip_clarity_check: bool = False,
    provided_metadata: Optional[Dict] = None
) -> dict:
    """
    Violation들을 Product/Version으로 매칭하는 통합 함수

    Args:
        db: Database session
        violations: 매칭할 Violation 목록
        ai_provider: AI 제공자 (openai, gemini 등)
        ai_model: AI 모델명
        api_key: API 키
        skip_clarity_check: True면 파일명 명확성 검사 건너뜀 (수동 매칭용)
        provided_metadata: 사전 생성된 메타데이터 (수동 매칭용, None이면 자동 생성)

    Returns:
        {
            "matched": int,
            "failed": int,
            "errors": list,
            "products": list  # 생성/업데이트된 Product 목록
        }
    """
    results = {
        "matched": 0,
        "failed": 0,
        "errors": [],
        "products": []
    }

    if not violations:
        return results

    parser = FilenameParser()
    generator = AIMetadataGenerator()
    generator.api_key = api_key
    generator.model = ai_model
    generator.provider = ai_provider

    # 1단계: 분할 압축 파일 필터링 (자동 매칭에만 적용)
    if not skip_clarity_check:
        filtered_violations = []
        for violation in violations:
            if parser.is_split_archive(violation.file_name):
                # 분할 압축 파일은 스킵 (검색된 목록에 남김)
                continue
            filtered_violations.append(violation)
    else:
        # 수동 매칭은 모든 파일 처리
        filtered_violations = violations

    # 2단계: folder_path별로 그룹화
    folder_groups = {}
    for violation in filtered_violations:
        if violation.folder_path not in folder_groups:
            folder_groups[violation.folder_path] = []
        folder_groups[violation.folder_path].append(violation)

    # 3단계: AI로 파일명 명확성 판단 (자동 매칭에만 적용)
    if not skip_clarity_check:
        clear_folder_groups = {}
        for folder_path, violations_list in folder_groups.items():
            # 대표 파일명으로 명확성 판단 (첫 번째 파일)
            sample_filename = violations_list[0].file_name
            folder_name = os.path.basename(folder_path)

            try:
                is_clear = await generator.is_filename_clear_for_matching(
                    sample_filename,
                    folder_name
                )

                if is_clear:
                    # 명확한 파일명만 자동 매칭 대상에 포함
                    clear_folder_groups[folder_path] = violations_list
                # else: 불명확한 파일명은 검색된 목록에 남김

            except Exception as e:
                # AI 판단 실패 시 안전하게 True로 간주
                clear_folder_groups[folder_path] = violations_list
                results["errors"].append(f"Clarity check failed for {folder_path}: {str(e)}")
    else:
        # 수동 매칭은 명확성 검사 건너뜀
        clear_folder_groups = folder_groups

    # 4단계: Product 생성 및 Version 매칭
    for folder_path, violations_list in clear_folder_groups.items():
        try:
            # 이미 Product가 있는지 확인
            existing_product = db.query(Product).filter(
                Product.folder_path == folder_path
            ).first()

            # 메타데이터 준비
            if provided_metadata:
                # 수동 매칭: 사용자가 제공한 메타데이터 사용
                metadata = provided_metadata
            else:
                # 자동 매칭: AI로 메타데이터 생성
                folder_name = os.path.basename(folder_path)
                parsed_info = parser.parse(folder_name)
                software_name = parsed_info.get('software_name', folder_name)
                ai_metadata = await generator.generate_detailed_metadata(software_name)

                # AI 메타데이터 필드명 → Product 모델 필드명 매핑
                metadata = {
                    **ai_metadata,
                    # AI: description_short → Product: description
                    'description': ai_metadata.get('description_short') or ai_metadata.get('description', ''),
                    # AI: developer → Product: vendor
                    'vendor': ai_metadata.get('developer') or ai_metadata.get('vendor', ''),
                    # AI: description_detailed → Product: detailed_description
                    'detailed_description': ai_metadata.get('description_detailed') or ai_metadata.get('detailed_description')
                }

            # Product 생성 또는 업데이트
            if existing_product:
                product = existing_product

                # 사용자 제공 메타데이터가 있으면 업데이트
                if provided_metadata:
                    if metadata.get('title'):
                        product.title = metadata['title']
                    if metadata.get('subtitle'):
                        product.subtitle = metadata['subtitle']
                    if metadata.get('description'):
                        product.description = metadata['description']
                    if metadata.get('vendor'):
                        product.vendor = metadata['vendor']
                    if metadata.get('category'):
                        product.category = metadata['category']
                    if metadata.get('official_website'):
                        product.official_website = metadata['official_website']
                    if metadata.get('license_type'):
                        product.license_type = metadata['license_type']
                    if metadata.get('platform'):
                        product.platform = metadata['platform']
                    if metadata.get('detailed_description'):
                        product.detailed_description = metadata['detailed_description']
                    if metadata.get('features'):
                        product.features = metadata['features']
                    if metadata.get('system_requirements'):
                        product.system_requirements = metadata['system_requirements']
                    if metadata.get('supported_formats'):
                        product.supported_formats = metadata['supported_formats']
                    if metadata.get('installation_info'):
                        product.installation_info = metadata['installation_info']
                    if metadata.get('release_notes'):
                        product.release_notes = metadata['release_notes']
                    if metadata.get('release_date'):
                        product.release_date = metadata['release_date']
                    if metadata.get('icon_url'):
                        product.icon_url = metadata['icon_url']
                    if metadata.get('screenshots'):
                        product.screenshots = metadata['screenshots']
            else:
                # 새 Product 생성
                folder_name = os.path.basename(folder_path)
                parsed_info = parser.parse(folder_name)
                software_name = parsed_info.get('software_name', folder_name)

                # 포터블 여부 감지
                is_portable = False
                if violations_list:
                    filename_lower = violations_list[0].file_name.lower()
                    if 'portable' in filename_lower or '무설치' in violations_list[0].file_name:
                        is_portable = True

                # Product 생성
                if provided_metadata:
                    # 사용자 제공 메타데이터로 생성 (상세 필드 포함)
                    product = Product(
                        title=metadata.get('title', software_name),
                        subtitle=metadata.get('subtitle'),
                        description=metadata.get('description', f"{software_name} 소프트웨어"),
                        vendor=metadata.get('vendor', ''),
                        category=metadata.get('category', 'Utility'),
                        official_website=metadata.get('official_website'),
                        license_type=metadata.get('license_type'),
                        platform=metadata.get('platform'),
                        detailed_description=metadata.get('detailed_description'),
                        features=metadata.get('features'),
                        system_requirements=metadata.get('system_requirements'),
                        supported_formats=metadata.get('supported_formats'),
                        installation_info=metadata.get('installation_info'),
                        release_notes=metadata.get('release_notes'),
                        release_date=metadata.get('release_date'),
                        icon_url=metadata.get('icon_url', ''),
                        screenshots=metadata.get('screenshots'),
                        folder_path=folder_path,
                        is_portable=is_portable
                    )
                else:
                    # 자동 생성 메타데이터로 생성 (기본 필드만)
                    product = Product(
                        title=metadata.get('title', software_name),
                        description=metadata.get('description', f"{software_name} 소프트웨어"),
                        vendor=metadata.get('vendor', ''),
                        category=metadata.get('category', 'Utility'),
                        icon_url=metadata.get('icon_url', ''),
                        folder_path=folder_path,
                        is_portable=is_portable
                    )

                db.add(product)
                db.flush()  # Get product ID

            # Version 생성
            for violation in violations_list:
                file_path_str = os.path.join(violation.folder_path, violation.file_name)

                # 이미 Version이 있는지 확인
                existing_version = db.query(Version).filter(
                    Version.file_path == file_path_str
                ).first()

                if not existing_version:
                    # Version 생성
                    parsed = parser.parse(violation.file_name)
                    version_name = parsed.get('version', 'Unknown')

                    # 파일 크기 가져오기
                    file_size = 0
                    if os.path.exists(file_path_str):
                        file_size = os.path.getsize(file_path_str)

                    version = Version(
                        product_id=product.id,
                        file_name=violation.file_name,
                        file_path=file_path_str,
                        file_size=file_size,
                        version_name=version_name
                    )

                    db.add(version)
                    db.flush()  # Get version ID

                    # Violation에 매칭 정보 저장
                    violation.product_id = product.id
                    violation.version_id = version.id
                else:
                    # 기존 Version이 있으면 해당 정보 연결
                    violation.product_id = existing_version.product_id
                    violation.version_id = existing_version.id

                # Violation을 해결됨으로 표시
                violation.is_resolved = True
                results["matched"] += 1

            db.commit()
            db.refresh(product)

            # 생성/업데이트된 Product 정보 추가
            results["products"].append({
                "id": product.id,
                "title": product.title,
                "description": product.description,
                "vendor": product.vendor,
                "category": product.category,
                "icon_url": product.icon_url,
                "folder_path": product.folder_path
            })

        except Exception as e:
            db.rollback()
            results["failed"] += len(violations_list)
            results["errors"].append(f"Failed to process {folder_path}: {str(e)}")

    # 캐시 무효화 (매칭이 완료되면 항상 실행)
    if results["matched"] > 0:
        invalidate_cache([
            "products_list:*",
            "products_recent:*",
            "products_by_category:*",
            "search_suggestions:*",
            "stats_overview:*",
            "stats_categories:*"
        ])

    return results
