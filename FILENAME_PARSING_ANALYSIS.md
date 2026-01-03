# 파일명 파싱 규칙 개선 분석

## 실제 파일명 패턴 분석 (tree_out1.txt 기반)

### 1. 구분자 사용 패턴
- **언더스코어(_)**: `Wallpaper_Engine_v1.4.173_RePack_by_xetrin.zip`
- **점(.)**: `Microsoft.Office.2016-2021x64.v2021.10.iso`
- **공백**: `Acronis True Image 2019 Build 14110`
- **하이픈(-)**: `Microsoft Office 2016-2021 LTSC`
- **혼합**: `EaseUS_Todo_Backup_13.5.0_Build_20210129_Enterprise_Technician_WinPE_x64_Downloadly.ir.rar`

### 2. 제거해야 할 노이즈 키워드

#### 릴리즈 그룹/사이트
- `RePack by xetrin`, `RePack by KpoJIuK`
- `[SadeemPC]`, `Downloadly.ir`, `TryRooM`
- `KoreaC rack`, `yaschir`

#### Build/버전 관련
- `Build 14110`, `Build_20210129`, `Build 20230206`
- `SP1`, `SP2`, `R2`
- `LTSC`, `VLSC`, `Vol`, `VL`

#### 에디션/타입
- `Multilingual`, `WinPE`, `Retail`, `OEM`
- `Trial`, `Extras`, `Addon`, `Addons`
- `Custom`, `Embedded`, `Delta`
- `x64`, `x86`, `ia64`, `x32x64`

#### 크랙/인증 관련
- `Crack`, `Patch`, `Keygen`, `Serial`
- `Activation`, `Activator`, `Activated`
- `Registered`, `Licensed`

#### 한글 노이즈
- `한국어판`, `설치법`, `인증방법`
- `스크린샷`, `포터블`

### 3. 유지해야 할 에디션 키워드
- `Professional Plus` (하나의 에디션)
- `Enterprise`, `Technician`, `Server Plus`
- `Premium`, `Ultimate`, `Advanced`
- `Standard`, `Home`, `Business`

### 4. 버전 패턴
- 단순: `v2.1`, `10.51`, `15.8`
- 복잡: `16.0.11929.20376`, `v23.3.1.14110`
- 연도: `2019`, `2016-2021`
- Build: `Build 14110`, `6688`

### 5. 날짜 패턴 (제거 필요)
- `20140826055959` (yyyyMMddHHmmss)
- `2021-01-01` (yyyy-MM-dd)
- `2015.0915` (yyyy.MMdd)

### 6. 특수 패턴
- 괄호 안 내용: `(2021.10)`, `(W10 11)`, `(Portable)`
- 대괄호 안 내용: `[SadeemPC]`, `[23.3.1.14110]`
- `by` 키워드: `RePack by KpoJIuK`

## 개선 방안

### 1. NOISE_WORDS 확장
- 릴리즈 그룹명, 웹사이트명 추가
- Build, 날짜 형식 관련 키워드 추가
- 한글 노이즈 워드 추가

### 2. 릴리즈 그룹 패턴 제거
```python
# 패턴: by xxx, [xxx]
text = re.sub(r'\bby\s+\w+', '', text, flags=re.IGNORECASE)
text = re.sub(r'\[.*?\]', '', text)
```

### 3. Build 번호 처리
```python
# Build 키워드 및 뒤따르는 숫자 제거
text = re.sub(r'\bbuild[_\s]*\d+', '', text, flags=re.IGNORECASE)
```

### 4. 날짜 형식 제거
```python
# yyyyMMddHHmmss 형식
text = re.sub(r'\b\d{14}\b', '', text)
# yyyy-MM-dd 형식
text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '', text)
# yyyy.MMdd 형식
text = re.sub(r'\b\d{4}\.\d{4}\b', '', text)
```

### 5. 에디션 키워드 확장
- `Professional Plus`, `Enterprise`, `Technician`
- `Server`, `Advanced`, `Volume`

### 6. 괄호 처리 개선
- 괄호 안 노이즈 제거
- 단, 버전 정보는 유지

## 예상 개선 효과

**개선 전:**
- `Wallpaper_Engine_v1.4.173_RePack_by_xetrin.zip`
- 파싱 결과: `Wallpaper Engine v1.4.173 RePack by xetrin`

**개선 후:**
- 파싱 결과: `Wallpaper Engine`
- 버전: `1.4.173`
- 릴리즈 그룹 제거 완료

**개선 전:**
- `Microsoft Office 2016-2021 LTSC Professional Plus Standard + Visio + Project 16.0.14527.20226 (2021.10) (W10 11) RePack by KpoJIuK`
- 파싱 결과: 너무 김

**개선 후:**
- 파싱 결과: `Microsoft Office Professional Plus`
- 버전: `2016-2021`
- 노이즈 제거 완료
