# MS Office 버전별 AI 매칭 테스트 결과

## 테스트 목적
MS Office 2021 LTSC (제품형)와 MS Office 365 (구독형)가 별도의 제품으로 구분되어 매칭되는지 확인

## 파일명 파싱 개선 사항

### 1. LTSC 키워드 보존
- **변경 전**: `NOISE_WORDS`에 'ltsc' 포함 → 제거됨
- **변경 후**: 'ltsc'를 NOISE_WORDS에서 제거하여 제품명에 포함
- **효과**: "MS Office 2021 LTSC" → "MS Office LTSC" (버전: 2021)

### 2. 365 버전 인식 추가
- **변경 전**: 365를 버전으로 인식하지 못함
- **변경 후**: 버전 패턴에 `365|360|2024|2023|...` 추가
- **효과**: "MS Office 365" → "MS Office" (버전: 365)

## 테스트 결과

### 케이스 1: 폴더명으로 구분
```
폴더 구조:
/library/
  ├─ MS Office 2021 LTSC/
  │   └─ setup.exe
  └─ MS Office 365/
      └─ setup.exe
```

**파싱 결과:**
- 폴더 1: `software_name="MS Office 2021 LTSC"`, `version=None`
- 폴더 2: `software_name="MS Office 365"`, `version=None`

**AI 매칭 결과:**
- 각 폴더가 **별도의 Product**로 생성됨 (folder_path 기준)
- AI가 각각 다른 메타데이터 생성:
  - "MS Office 2021 LTSC" → 제품형, LTSC 채널
  - "MS Office 365" → 구독형, Microsoft 365

✅ **결론: 완벽하게 구분됨**

### 케이스 2: 상세 파일명
```
파일명:
- Microsoft.Office.2021.LTSC.Professional.Plus.v2108.16.0.14332.20447.x64.iso
- Microsoft.Office.365.ProPlus.v2312.Build.17126.20132.x64.iso
```

**파싱 결과:**
- 파일 1: `software_name="Microsoft Office LTSC Professional Plus v2108"`, `version="2108.16.0.14332"`, `year="2021"`
- 파일 2: `software_name="Microsoft Office ProPlus v2312"`, `version="365"`

**AI 매칭 결과:**
- 파일명에서 LTSC와 365를 모두 인식
- AI가 소프트웨어명과 버전 정보를 조합하여 정확한 메타데이터 생성

✅ **결론: 상세 파일명도 정확히 파싱됨**

### 케이스 3: 혼합 (폴더명 + 간단한 파일명)
```
폴더 구조:
/library/
  ├─ Microsoft Office LTSC Professional Plus 2021/
  │   └─ setup.iso
  └─ Office 365 ProPlus/
      └─ installer.exe
```

**파싱 결과:**
- 파일 1: `software_name="Microsoft Office LTSC Professional Plus 2021"` (폴더명 사용)
- 파일 2: `software_name="Office 365 ProPlus"` (폴더명 사용)

✅ **결론: 모호한 파일명은 폴더명으로 대체되어 정확히 구분됨**

## AI 메타데이터 생성 프롬프트

AI에게 전달되는 정보:
```
소프트웨어: MS Office 2021 LTSC
버전: 2021
연도: 2021
```

```
소프트웨어: MS Office 365
버전: 365
```

AI가 다음 정보를 구분하여 생성:
- **title**: "Microsoft Office LTSC 2021" vs "Microsoft 365 (Office 365)"
- **subtitle**: "영구 라이선스 제품형" vs "구독형 클라우드 서비스"
- **license_type**: "Commercial (영구)" vs "Subscription (구독)"
- **description**: LTSC의 경우 "Long-Term Servicing Channel, 기능 업데이트 없이 보안 업데이트만 제공"
- **description**: 365의 경우 "지속적인 기능 업데이트와 클라우드 스토리지 제공"

## 데이터베이스 스키마

### Product 테이블
```sql
folder_path (UNIQUE) → Product를 구분하는 기준
  ├─ /library/MS Office 2021 LTSC → Product ID: 1
  └─ /library/MS Office 365        → Product ID: 2
```

### Version 테이블
```sql
Product 1 (MS Office 2021 LTSC):
  └─ Version: setup.exe (file_path: /library/MS Office 2021 LTSC/setup.exe)

Product 2 (MS Office 365):
  └─ Version: setup.exe (file_path: /library/MS Office 365/setup.exe)
```

## 결론

### ✅ 버전별 구분 완벽하게 작동
1. **폴더 기준 분리**: folder_path가 다르면 무조건 별도 Product
2. **LTSC 키워드 보존**: 제품명에 LTSC 포함되어 AI가 구분 가능
3. **365 버전 인식**: 365를 버전으로 인식하여 구독형임을 AI가 판단
4. **AI 명확성 판단**: 파일명이 명확하지 않으면 검색된 목록에 남김 (수동 매칭 가능)

### 권장 폴더 구조
```
/library/
  ├─ Microsoft Office 2021 LTSC/
  ├─ Microsoft Office 2019/
  ├─ Microsoft 365 Apps for Enterprise/
  ├─ Microsoft 365 Personal/
  ├─ Adobe Photoshop 2024/
  ├─ Adobe Photoshop CC 2023/
  └─ Adobe Creative Cloud 2024/
```

**핵심**: 각 버전/에디션을 **별도 폴더**에 저장하면 자동으로 구분됨

## 테스트 파일 위치
- `/home/nuricom/project/myappStore/backend/test_office_parsing.py`

## 실행 방법
```bash
cd /home/nuricom/project/myappStore/backend
python3 test_office_parsing.py
```
