"""
Gemini API에서 사용 가능한 모델 목록 확인
"""
import asyncio
import httpx
from app.config import settings

async def list_gemini_models():
    """사용 가능한 Gemini 모델 목록 가져오기"""
    api_key = settings.GEMINI_API_KEY

    print("=" * 80)
    print("Gemini API 사용 가능한 모델 확인")
    print("=" * 80)
    print(f"\nAPI 키: {api_key[:20]}...")
    print()

    # v1beta로 모델 목록 요청
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])

                print(f"✅ 총 {len(models)}개의 모델 발견\n")
                print("=" * 80)

                # generateContent를 지원하는 모델만 필터링
                generate_models = []
                for model in models:
                    name = model.get('name', '')
                    supported_methods = model.get('supportedGenerationMethods', [])

                    if 'generateContent' in supported_methods:
                        model_id = name.replace('models/', '')
                        generate_models.append(model_id)
                        print(f"✅ {model_id}")
                        print(f"   지원 메서드: {', '.join(supported_methods)}")
                        print()

                print("=" * 80)
                print(f"\n📌 generateContent를 지원하는 모델: {len(generate_models)}개")
                print("\n추천 모델:")
                for model in generate_models:
                    if 'flash' in model.lower():
                        print(f"  - {model} (빠른 버전)")
                    elif 'pro' in model.lower():
                        print(f"  - {model} (프로 버전)")

            else:
                print(f"❌ 오류: {response.status_code}")
                print(response.text)

    except Exception as e:
        print(f"❌ 예외 발생: {e}")

if __name__ == "__main__":
    asyncio.run(list_gemini_models())
