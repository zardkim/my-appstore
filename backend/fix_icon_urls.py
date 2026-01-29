#!/usr/bin/env python3
"""
아이콘 URL을 절대 경로에서 상대 경로로 변환
기존: http://localhost:8100/static/icons/1.png
변환: /static/icons/1.png
"""
import os
import sys
import re

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.product import Product
from sqlalchemy import func


def fix_icon_urls():
    """DB에 저장된 icon_url을 상대 경로로 변경"""
    db = SessionLocal()

    try:
        # 절대 URL 패턴 (http:// 또는 https://로 시작)
        products = db.query(Product).filter(
            Product.icon_url.like('http://%')
        ).all()

        if not products:
            print("✅ 수정할 icon_url이 없습니다.")
            return

        print(f"📋 총 {len(products)}개의 제품 icon_url을 수정합니다.\n")

        updated_count = 0
        for product in products:
            old_url = product.icon_url

            # URL에서 /static/ 이후 부분만 추출
            # 예: http://localhost:8100/static/icons/1.png -> /static/icons/1.png
            match = re.search(r'(/static/.+)', old_url)
            if match:
                new_url = match.group(1)
                product.icon_url = new_url
                updated_count += 1
                print(f"[{product.id}] {product.title[:40]}")
                print(f"  ❌ {old_url}")
                print(f"  ✅ {new_url}\n")

        if updated_count > 0:
            db.commit()
            print(f"\n✅ {updated_count}개의 icon_url을 성공적으로 변경했습니다.")
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
    print("Icon URL 상대 경로 변환 스크립트")
    print("=" * 60)
    print()

    fix_icon_urls()
