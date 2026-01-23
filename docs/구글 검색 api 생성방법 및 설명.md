아래 순서대로 하면 Google Custom Search JSON API 키 + 이미지 검색용 검색엔진(CSE) 을 10~15분 안에 발급받을 수 있습니다.
(실무에서 가장 많이 쓰는 방법 기준으로 정리했어요)

🔑 Google Custom Search API 키 발급 방법 (공식)
전체 구조 먼저 이해하기
Google 이미지 검색 API를 쓰려면 2가지가 필요합니다.

1️⃣ API Key
2️⃣ Custom Search Engine ID (cx)

👉 이 두 개가 있어야 이미지 검색이 됩니다.

1️⃣ Google Cloud Console에서 프로젝트 생성
접속
👉 https://console.cloud.google.com/

상단 프로젝트 선택 → 새 프로젝트

프로젝트 이름: 예) metadata-search

조직 없음 → OK

프로젝트 생성 후 해당 프로젝트 선택

2️⃣ Custom Search JSON API 활성화
좌측 메뉴 → API 및 서비스 → 라이브러리

검색창에

Custom Search JSON API
선택 후 [사용] 클릭

✅ 이 단계에서 “API를 쓸 수 있는 권한”이 열립니다.

3️⃣ API 키 생성
좌측 메뉴 → API 및 서비스 → 사용자 인증 정보

[+ 사용자 인증 정보 만들기]

API 키 선택

🎉 즉시 발급됨

예시:

AIzaSyDxxxxxxxxxxxxxxxxxxxx
🔐 보안 설정 (강력 권장)
API 키 제한 설정

HTTP referrer (웹앱)

또는 IP 주소 (서버)

API 제한

Custom Search JSON API 만 허용

4️⃣ Custom Search Engine (CSE) 생성
이건 API 키와 별도 단계입니다.

접속
👉 https://programmablesearchengine.google.com/

[검색엔진 만들기] 클릭

설정

검색할 사이트:

*
(전체 웹 검색 허용)

검색엔진 이름: 예) SoftwareMetadataSearch

만들기 클릭

5️⃣ 이미지 검색 허용 설정 (중요!)
생성된 검색엔진 클릭

설정 → 기본 설정

이미지 검색 → ON

저장

6️⃣ Search Engine ID (cx) 확인
CSE 설정 화면

검색엔진 ID

cx=xxxxxxxxxxxxxxxxx
이게 바로 cx 값입니다.

7️⃣ 실제 API 호출 예제
📸 이미지 검색 (로고/스크린샷)
요청 예시
GET https://www.googleapis.com/customsearch/v1
  ?key=API_KEY
  &cx=SEARCH_ENGINE_ID
  &q=SolidWorks 2022 official logo
  &searchType=image
🟢 Node.js 예제 (axios)
import axios from "axios";

const API_KEY = process.env.GOOGLE_API_KEY;
const CX = process.env.GOOGLE_CX;

async function searchImage(query) {
  const res = await axios.get(
    "https://www.googleapis.com/customsearch/v1",
    {
      params: {
        key: API_KEY,
        cx: CX,
        q: query,
        searchType: "image",
        num: 5
      }
    }
  );
  return res.data.items;
}

searchImage("SolidWorks 2022 official logo")
  .then(console.log);
💰 요금 & 제한 (꼭 알아야 함)
항목	내용
무료	하루 100회 검색
유료	$5 / 1,000회
이미지	검색 1회로 계산
속도	초당 제한 있음
👉 AI 메타데이터 생성 후 이미지 보조 수단으로 쓰면 무료 쿼리로도 충분한 경우가 많음

🧠 실전 추천 설정 (당신 프로젝트 기준)
검색 쿼리 생성은 AI에게 맡기기

official logo, software screenshot, UI

이미지 URL만 저장, 파일 다운로드는 선택

출처 URL 필드 필수 저장 (저작권 안전)

✅ 체크리스트 (완료되면 OK)
☑ Google Cloud 프로젝트 생성
☑ Custom Search JSON API 활성화
☑ API Key 발급
☑ Programmable Search Engine 생성
☑ 이미지 검색 ON
☑ cx 값 확보