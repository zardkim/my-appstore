#!/usr/bin/env python3
"""
스크린샷 URL을 절대 경로에서 상대 경로로 변환
기존: http://localhost:8100/static/screenshots/1_screenshot_0.png
변환: /static/screenshots/1_screenshot_0.png
"""
import os
import sys
import re

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.product import Product


def fix_screenshot_urls():
    """DB에 저장된 screenshots URL을 상대 경로로 변경"""
    db = SessionLocal()

    try:
        # screenshots가 있는 모든 제품 조회
        products = db.query(Product).filter(
            Product.screenshots.isnot(None)
        ).all()

        if not products:
            print("✅ 수정할 screenshots가 없습니다.")
            return

        print(f"📋 총 {len(products)}개의 제품을 확인합니다.\n")

        updated_count = 0
        for product in products:
            if not product.screenshots or not isinstance(product.screenshots, list):
                continue

            # 절대 URL이 있는지 확인
            has_absolute_url = any(
                isinstance(url, str) and url.startswith('http')
                for url in product.screenshots
            )

            if not has_absolute_url:
                continue

            old_screenshots = product.screenshots.copy()
            new_screenshots = []

            for url in product.screenshots:
                if isinstance(url, str) and url.startswith('http'):
                    # URL에서 /static/ 이후 부분만 추출
                    match = re.search(r'(/static/.+)', url)
                    if match:
                        new_url = match.group(1)
                        new_screenshots.append(new_url)
                    else:
                        new_screenshots.append(url)
                else:
                    new_screenshots.append(url)

            product.screenshots = new_screenshots
            updated_count += 1

            print(f"[{product.id}] {product.title[:40]}")
            print(f"  ❌ {old_screenshots}")
            print(f"  ✅ {new_screenshots}\n")

        if updated_count > 0:
            db.commit()
            print(f"\n✅ {updated_count}개의 제품 screenshots를 성공적으로 변경했습니다.")
        else:
            print("\n⚠️  변경된 항목이 없습니다.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Screenshots URL 상대 경로 변환 스크립트")
    print("=" * 60)
    print()

    fix_screenshot_urls()
