"""
테스트 제품의 메타데이터를 수정하여 더 정확한 정보로 업데이트
"""
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.product import Product
from app.core.web_crawler import WebCrawler
from app.core.ai_metadata import AIMetadataGenerator
from app.core.filename_standardizer import FilenameStandardizer
import html

async def fix_metadata():
    """테스트 제품의 메타데이터 수정"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("테스트 제품 메타데이터 수정")
        print("=" * 80)

        # 웹 크롤러 초기화
        crawler = WebCrawler()

        # 테스트 폴더의 제품들만 선택
        products = db.query(Product).filter(
            Product.folder_path.like('/library/test_samples/%')
        ).all()

        print(f"\n수정할 제품: {len(products)}개")

        for idx, product in enumerate(products, 1):
            print(f"\n{'=' * 80}")
            print(f"{idx}/{len(products)}: {product.title}")
            print("-" * 80)

            # 검색 쿼리 생성
            search_query = product.title

            # 웹 크롤링 실행
            print(f"🔍 웹 크롤링: {search_query}")
            web_data = await crawler.search_web(search_query)

            if web_data:
                # 공식 웹사이트 업데이트 (우선순위: DuckDuckGo > 다른 소스)
                if web_data.get('official_website'):
                    # FileHippo가 아닌 실제 공식 사이트 찾기
                    website = web_data.get('official_website', '')
                    if 'filehippo.com' not in website:
                        product.official_website = website
                        print(f"   ✅ 공식 웹사이트: {website}")
                    else:
                        # additional_sources에서 찾기
                        print(f"   ⚠️  FileHippo 발견, 다른 소스 찾는 중...")

                # 상세 설명 디코딩 및 정리
                if web_data.get('additional_info'):
                    raw_desc = web_data['additional_info']
                    # HTML 엔티티 디코딩
                    decoded_desc = html.unescape(raw_desc)
                    # 줄바꿈 정리
                    lines = [line.strip() for line in decoded_desc.split('|') if line.strip()]
                    # FileHippo 다운로드 페이지는 제외
                    filtered_lines = [
                        line for line in lines
                        if 'FileHippo 다운로드 페이지' not in line and len(line) > 20
                    ]
                    product.detailed_description = ' | '.join(filtered_lines)
                    print(f"   ✅ 상세 설명 업데이트")

                # 스크린샷 업데이트
                if web_data.get('screenshots'):
                    # FileHippo 일반 아이콘 제거
                    screenshots = [
                        url for url in web_data['screenshots']
                        if 'cabb87.png' not in url  # Avast 아이콘 제거
                    ]
                    product.screenshots = screenshots
                    print(f"   ✅ 스크린샷: {len(screenshots)}개")

                    # 첫 스크린샷을 아이콘으로 사용 (일반 아이콘이 아닌 경우)
                    if screenshots and 'cabb87.png' in (product.icon_url or ''):
                        product.icon_url = screenshots[0]
                        print(f"   ✅ 아이콘 업데이트: {screenshots[0][:60]}...")

                # 크롤링 소스 업데이트
                if web_data.get('web_sources'):
                    product.crawled_from = {
                        source: True for source in web_data['web_sources']
                    }

            # AI로 더 나은 설명 생성
            print(f"🤖 AI 설명 생성 중...")
            try:
                ai_gen = AIMetadataGenerator(provider="gemini", model="gemini-2.5-flash")
                ai_data = await ai_gen.generate_metadata(product.title, "")

                # AI 설명이 더 나은 경우 업데이트
                if ai_data.get('description') and len(ai_data['description']) > len(product.description or ''):
                    if 'software' not in ai_data['description'].lower():  # 너무 일반적이지 않은 경우
                        product.description = ai_data['description']
                        print(f"   ✅ AI 설명 업데이트: {ai_data['description'][:60]}...")
            except Exception as e:
                print(f"   ⚠️  AI 생성 실패: {e}")

            print(f"\n   현재 상태:")
            print(f"   - 제목: {product.title}")
            print(f"   - 설명: {(product.description or 'N/A')[:60]}...")
            print(f"   - 공식 사이트: {product.official_website or 'N/A'}")
            print(f"   - 아이콘: {(product.icon_url or 'N/A')[:60]}...")
            print(f"   - 스크린샷: {len(product.screenshots or [])}개")

            # 딜레이
            if idx < len(products):
                await asyncio.sleep(3)

        # 커밋
        db.commit()

        print("\n" + "=" * 80)
        print("메타데이터 수정 완료!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fix_metadata())
