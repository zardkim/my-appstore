# MyApp Store 단계별 구현 가이드

## 📋 목차
- [Phase 0: 프로젝트 초기 설정](#phase-0-프로젝트-초기-설정)
- [Phase 1: MVP 개발](#phase-1-mvp-개발)
- [Phase 2: AI 메타데이터 엔진](#phase-2-ai-메타데이터-엔진)
- [Phase 3: 고급 기능 및 최적화](#phase-3-고급-기능-및-최적화)

---

## Phase 0: 프로젝트 초기 설정

### Step 0.1: 프로젝트 구조 생성

```
myappStore/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 앱 진입점
│   │   ├── config.py               # 환경 변수 및 설정
│   │   ├── database.py             # DB 연결 설정
│   │   ├── models/                 # SQLAlchemy 모델
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── version.py
│   │   │   ├── attachment.py
│   │   │   └── setting.py
│   │   ├── schemas/                # Pydantic 스키마
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   └── auth.py
│   │   ├── api/                    # API 라우터
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   ├── users.py
│   │   │   ├── scan.py
│   │   │   └── admin.py
│   │   ├── core/                   # 핵심 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── security.py         # 비밀번호 해싱, JWT
│   │   │   ├── scanner.py          # 파일 스캐너
│   │   │   ├── parser.py           # 파일명 파싱
│   │   │   ├── ai_metadata.py      # AI 메타데이터 생성
│   │   │   └── scheduler.py        # APScheduler 설정
│   │   └── dependencies.py         # FastAPI 의존성
│   ├── alembic/                    # DB 마이그레이션
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── layout/
│   │   │   ├── product/
│   │   │   └── admin/
│   │   ├── views/
│   │   │   ├── Home.vue
│   │   │   ├── Discover.vue
│   │   │   ├── ProductDetail.vue
│   │   │   ├── Login.vue
│   │   │   ├── Setup.vue
│   │   │   └── Admin.vue
│   │   ├── router/
│   │   ├── store/                  # Vuex 또는 Pinia
│   │   ├── api/                    # API 클라이언트
│   │   ├── utils/
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── data/                           # Docker 볼륨 마운트 포인트
│   ├── db/
│   └── icons/
├── docker-compose.yml
├── .gitignore
├── CLAUDE.md
└── README.md
```

**실행 작업:**
1. 위 폴더 구조를 생성
2. `.gitignore` 파일 작성 (Python, Node.js, Docker 관련)
3. `README.md` 작성 (프로젝트 소개, 실행 방법)

---

## Phase 1: MVP 개발

### Step 1.1: Backend 기본 환경 구축

#### 1.1.1 Dependencies 설치 파일 작성

**backend/requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

#### 1.1.2 Database 모델 정의

**backend/app/models/user.py:**
```python
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**backend/app/models/product.py:**
```python
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    vendor = Column(String)
    icon_url = Column(String)
    category = Column(String, index=True)
    folder_path = Column(String, unique=True, nullable=False)

    versions = relationship("Version", back_populates="product", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="product", cascade="all, delete-orphan")
```

**backend/app/models/version.py:**
```python
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    version_name = Column(String)
    file_name = Column(String, nullable=False)
    file_path = Column(String, unique=True, nullable=False)
    file_size = Column(BigInteger)
    release_date = Column(DateTime(timezone=True))

    product = relationship("Product", back_populates="versions")
```

#### 1.1.3 Database 연결 설정

**backend/app/database.py:**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**backend/app/config.py:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/myappstore"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
```

#### 1.1.4 FastAPI 메인 앱 작성

**backend/app/main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, products, users, admin
from app.database import engine, Base

# 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyApp Store API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "MyApp Store API"}
```

### Step 1.2: 인증 시스템 구현

#### 1.2.1 Security 유틸리티

**backend/app/core/security.py:**
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

#### 1.2.2 Auth API

**backend/app/api/auth.py:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/check-setup")
def check_setup(db: Session = Depends(get_db)):
    """최초 실행 여부 확인 (사용자 테이블이 비어있는지)"""
    user_count = db.query(User).count()
    return {"needs_setup": user_count == 0}
```

### Step 1.3: 파일 스캐너 구현

#### 1.3.1 파일 스캐너 코어

**backend/app/core/scanner.py:**
```python
import os
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.version import Version

class FileScanner:
    def __init__(self, db: Session):
        self.db = db

    def scan_directory(self, base_path: str) -> dict:
        """
        지정된 경로를 스캔하여 신규 프로그램과 버전을 발견
        """
        base_path = Path(base_path)
        if not base_path.exists():
            raise ValueError(f"Path does not exist: {base_path}")

        results = {
            "new_products": 0,
            "new_versions": 0,
            "errors": []
        }

        # 1단계: 폴더 = 프로그램, 내부 파일 = 버전
        for folder in base_path.iterdir():
            if not folder.is_dir():
                continue

            try:
                self._process_folder(folder, results)
            except Exception as e:
                results["errors"].append(f"Error processing {folder}: {str(e)}")

        return results

    def _process_folder(self, folder: Path, results: dict):
        """
        폴더를 처리하여 Product와 Version 생성/업데이트
        """
        folder_path_str = str(folder)

        # Product 조회 또는 생성
        product = self.db.query(Product).filter(
            Product.folder_path == folder_path_str
        ).first()

        if not product:
            # 새 프로그램 등록 (메타데이터는 나중에 AI로 채움)
            product = Product(
                title=folder.name,  # 초기에는 폴더명 사용
                folder_path=folder_path_str
            )
            self.db.add(product)
            self.db.flush()  # ID 생성
            results["new_products"] += 1

        # 폴더 내 파일들 스캔
        for file_path in folder.iterdir():
            if file_path.is_file():
                self._process_file(file_path, product, results)

        self.db.commit()

    def _process_file(self, file_path: Path, product: Product, results: dict):
        """
        파일을 Version으로 등록
        """
        file_path_str = str(file_path)

        # 이미 등록된 파일인지 확인
        existing = self.db.query(Version).filter(
            Version.file_path == file_path_str
        ).first()

        if existing:
            return

        # 새 버전 등록
        version = Version(
            product_id=product.id,
            file_name=file_path.name,
            file_path=file_path_str,
            file_size=file_path.stat().st_size,
            version_name=self._extract_version(file_path.name)
        )
        self.db.add(version)
        results["new_versions"] += 1

    @staticmethod
    def _extract_version(filename: str) -> str:
        """
        파일명에서 버전 정보 추출 (간단한 구현)
        Phase 2에서 고도화
        """
        import re
        # v1.0, 2024, v25.0 등 패턴 찾기
        version_patterns = [
            r'v?(\d+\.\d+\.\d+)',
            r'v?(\d+\.\d+)',
            r'(\d{4})',
        ]
        for pattern in version_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Unknown"
```

#### 1.3.2 Scan API

**backend/app/api/scan.py:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.scanner import FileScanner
from pydantic import BaseModel

router = APIRouter()

class ScanRequest(BaseModel):
    path: str

@router.post("/start")
def start_scan(request: ScanRequest, db: Session = Depends(get_db)):
    """
    수동 스캔 시작
    """
    scanner = FileScanner(db)
    try:
        results = scanner.scan_directory(request.path)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**main.py에 라우터 추가:**
```python
from app.api import scan
app.include_router(scan.router, prefix="/api/scan", tags=["scan"])
```

### Step 1.4: Docker 환경 구축

#### 1.4.1 Backend Dockerfile

**backend/Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY ./app ./app

# 포트 노출
EXPOSE 8110

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8110", "--reload"]
```

#### 1.4.2 Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: myapp-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: myappstore
    volumes:
      - ./data/db:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    container_name: myapp-backend
    volumes:
      - ./backend:/app
      - /volume1/Software:/mnt/software:ro  # NAS 경로 (실제 환경에 맞게 수정)
      - ./data/icons:/app/static/icons
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/myappstore
      - SECRET_KEY=your-secret-key-change-this
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8110:8110"
    depends_on:
      - db

  frontend:
    build: ./frontend
    container_name: myapp-frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5900:5900"
    depends_on:
      - backend
```

### Step 1.5: Frontend 기본 구조

#### 1.5.1 Vue 프로젝트 초기화

```bash
cd frontend
npm create vite@latest . -- --template vue
npm install
npm install vue-router@4 pinia axios tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### 1.5.2 API 클라이언트

**frontend/src/api/client.js:**
```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8110/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 토큰 자동 추가
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

**frontend/src/api/auth.js:**
```javascript
import apiClient from './client';

export const authApi = {
  login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  checkSetup() {
    return apiClient.get('/auth/check-setup');
  }
};
```

#### 1.5.3 간단한 로그인 페이지

**frontend/src/views/Login.vue:**
```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h1 class="text-2xl font-bold mb-6">MyApp Store</h1>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">Username</label>
          <input
            v-model="username"
            type="text"
            class="w-full px-3 py-2 border rounded-lg"
            required
          />
        </div>
        <div class="mb-6">
          <label class="block text-sm font-medium mb-2">Password</label>
          <input
            v-model="password"
            type="password"
            class="w-full px-3 py-2 border rounded-lg"
            required
          />
        </div>
        <button
          type="submit"
          class="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600"
        >
          Login
        </button>
      </form>
      <p v-if="error" class="text-red-500 mt-4">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../api/auth';

const router = useRouter();
const username = ref('');
const password = ref('');
const error = ref('');

const handleLogin = async () => {
  try {
    const response = await authApi.login(username.value, password.value);
    localStorage.setItem('access_token', response.data.access_token);
    router.push('/');
  } catch (err) {
    error.value = 'Login failed. Please check your credentials.';
  }
};
</script>
```

**Phase 1 완료 체크리스트:**
- [ ] Docker 환경 실행 확인 (`docker-compose up`)
- [ ] PostgreSQL 연결 확인
- [ ] Backend API 문서 확인 (`http://localhost:8110/docs`)
- [ ] 로그인 페이지 접속 확인 (`http://localhost:5900`)
- [ ] 파일 스캔 API 테스트 (`POST /api/scan/start`)

---

## Phase 2: AI 메타데이터 엔진

### Step 2.1: 파일명 파싱 알고리즘

**backend/app/core/parser.py:**
```python
import re
from typing import Dict, Optional

class FilenameParser:
    """
    파일명에서 소프트웨어 정보 추출
    """

    # 제거할 일반적인 키워드
    NOISE_WORDS = [
        'setup', 'installer', 'install', 'portable', 'full', 'final',
        'crack', 'keygen', 'patch', 'x64', 'x86', 'win', 'mac', 'linux',
        'multilingual', 'retail', 'incl', 'repack'
    ]

    @staticmethod
    def parse(filename: str, parent_folder: str = "") -> Dict[str, Optional[str]]:
        """
        파일명 또는 폴더명에서 정보 추출

        Returns:
            {
                'software_name': str,
                'version': str,
                'vendor': str (추정),
                'year': str
            }
        """
        # 확장자 제거
        name_without_ext = re.sub(r'\.[^.]+$', '', filename)

        # 특수문자를 공백으로 변환
        cleaned = re.sub(r'[._-]', ' ', name_without_ext)

        # 버전 정보 추출
        version = FilenameParser._extract_version(cleaned)

        # 연도 추출
        year = FilenameParser._extract_year(cleaned)

        # 소프트웨어 이름 추출 (버전, 연도 제거)
        software_name = FilenameParser._extract_software_name(
            cleaned, version, year
        )

        # 소프트웨어 이름이 너무 짧으면 부모 폴더명 사용
        if len(software_name) < 3 and parent_folder:
            software_name = parent_folder

        # 제조사 추정 (첫 단어가 대문자로 시작하는 경우)
        vendor = FilenameParser._extract_vendor(software_name)

        return {
            'software_name': software_name.strip(),
            'version': version,
            'vendor': vendor,
            'year': year
        }

    @staticmethod
    def _extract_version(text: str) -> Optional[str]:
        """버전 정보 추출"""
        patterns = [
            r'v?(\d+\.\d+\.\d+\.\d+)',  # 1.2.3.4
            r'v?(\d+\.\d+\.\d+)',        # 1.2.3
            r'v?(\d+\.\d+)',             # 1.2
            r'v(\d+)',                   # v1
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _extract_year(text: str) -> Optional[str]:
        """연도 추출 (2000-2099)"""
        match = re.search(r'\b(20\d{2})\b', text)
        return match.group(1) if match else None

    @staticmethod
    def _extract_software_name(text: str, version: str, year: str) -> str:
        """소프트웨어 이름 추출"""
        # 버전 정보 제거
        if version:
            text = re.sub(rf'v?{re.escape(version)}', '', text, flags=re.IGNORECASE)

        # 연도 제거
        if year:
            text = text.replace(year, '')

        # 노이즈 단어 제거
        words = text.split()
        filtered_words = [
            w for w in words
            if w.lower() not in FilenameParser.NOISE_WORDS
        ]

        return ' '.join(filtered_words[:4])  # 최대 4단어

    @staticmethod
    def _extract_vendor(software_name: str) -> Optional[str]:
        """제조사 추정 (첫 단어)"""
        words = software_name.split()
        if words and words[0][0].isupper():
            return words[0]
        return None
```

### Step 2.2: AI 메타데이터 생성 엔진

**backend/app/core/ai_metadata.py:**
```python
import json
from typing import Dict, Optional
import httpx
from app.config import settings
from app.core.parser import FilenameParser

class AIMetadataGenerator:
    """
    OpenAI API를 사용하여 소프트웨어 메타데이터 생성
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4o-mini"

    async def generate_metadata(
        self,
        filename: str,
        parent_folder: str = ""
    ) -> Dict:
        """
        파일명으로부터 메타데이터 생성

        Returns:
            {
                'title': str,
                'description': str,
                'vendor': str,
                'category': str,
                'icon_url': str
            }
        """
        # 1단계: 파일명 파싱
        parsed = FilenameParser.parse(filename, parent_folder)

        # 2단계: AI에게 질의
        metadata = await self._query_ai(parsed)

        return metadata

    async def _query_ai(self, parsed_info: Dict) -> Dict:
        """
        OpenAI API 호출
        """
        if not self.api_key:
            # API 키가 없으면 파싱 정보만 반환
            return self._fallback_metadata(parsed_info)

        software_name = parsed_info['software_name']
        version = parsed_info.get('version', '')

        prompt = f"""
다음 소프트웨어에 대한 정보를 JSON 형식으로 제공해주세요:

소프트웨어: {software_name}
버전: {version}

다음 정보를 포함해주세요:
1. title: 정확한 소프트웨어 이름
2. description: 50자 이내의 간단한 설명
3. vendor: 공식 제조사/개발사 이름
4. category: 카테고리 (Graphics, Office, Development, Utility, Media, OS, Security 중 하나)
5. icon_url: 공식 아이콘 이미지 URL (찾을 수 없으면 빈 문자열)

응답은 반드시 JSON 형식으로만 작성하고, 다른 텍스트는 포함하지 마세요.
"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a software information expert."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']

                    # JSON 파싱
                    metadata = json.loads(content)
                    return metadata
                else:
                    return self._fallback_metadata(parsed_info)

        except Exception as e:
            print(f"AI API Error: {e}")
            return self._fallback_metadata(parsed_info)

    def _fallback_metadata(self, parsed_info: Dict) -> Dict:
        """
        AI 호출 실패 시 파싱 정보로 대체
        """
        return {
            'title': parsed_info['software_name'],
            'description': f"{parsed_info['software_name']} software",
            'vendor': parsed_info.get('vendor', 'Unknown'),
            'category': 'Utility',
            'icon_url': ''
        }
```

### Step 2.3: 스캐너에 메타데이터 생성 통합

**backend/app/core/scanner.py 수정:**
```python
from app.core.ai_metadata import AIMetadataGenerator

class FileScanner:
    def __init__(self, db: Session, use_ai: bool = True):
        self.db = db
        self.use_ai = use_ai
        self.ai_generator = AIMetadataGenerator() if use_ai else None

    async def scan_directory_async(self, base_path: str) -> dict:
        """
        비동기 스캔 (AI 호출 포함)
        """
        # ... 기존 코드 ...

        for folder in base_path.iterdir():
            if not folder.is_dir():
                continue

            try:
                await self._process_folder_async(folder, results)
            except Exception as e:
                results["errors"].append(f"Error processing {folder}: {str(e)}")

        return results

    async def _process_folder_async(self, folder: Path, results: dict):
        """
        폴더 처리 (AI 메타데이터 생성 포함)
        """
        folder_path_str = str(folder)

        # Product 조회
        product = self.db.query(Product).filter(
            Product.folder_path == folder_path_str
        ).first()

        is_new_product = False
        if not product:
            # AI로 메타데이터 생성
            if self.use_ai and self.ai_generator:
                metadata = await self.ai_generator.generate_metadata(
                    folder.name,
                    parent_folder=""
                )
            else:
                metadata = {
                    'title': folder.name,
                    'description': '',
                    'vendor': '',
                    'category': 'Utility',
                    'icon_url': ''
                }

            product = Product(
                title=metadata['title'],
                description=metadata['description'],
                vendor=metadata['vendor'],
                category=metadata['category'],
                icon_url=metadata['icon_url'],
                folder_path=folder_path_str
            )
            self.db.add(product)
            self.db.flush()
            is_new_product = True
            results["new_products"] += 1

        # 파일 스캔
        for file_path in folder.iterdir():
            if file_path.is_file():
                self._process_file(file_path, product, results)

        self.db.commit()
```

### Step 2.4: API 엔드포인트 수정

**backend/app/api/scan.py 수정:**
```python
@router.post("/start")
async def start_scan(request: ScanRequest, db: Session = Depends(get_db)):
    """
    비동기 스캔 시작 (AI 메타데이터 포함)
    """
    scanner = FileScanner(db, use_ai=True)
    try:
        results = await scanner.scan_directory_async(request.path)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Step 2.5: 아이콘 다운로드 및 캐싱

**backend/app/core/icon_cache.py:**
```python
import httpx
from pathlib import Path
from typing import Optional
import hashlib

class IconCache:
    """
    아이콘 이미지 다운로드 및 로컬 캐싱
    """

    def __init__(self, cache_dir: str = "/app/static/icons"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def download_and_cache(self, url: str, product_id: int) -> Optional[str]:
        """
        URL에서 아이콘 다운로드 후 로컬에 저장

        Returns:
            로컬 파일 경로 (예: /static/icons/1.png)
        """
        if not url:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)

                if response.status_code == 200:
                    # 파일 확장자 추출
                    ext = self._get_extension(url, response.headers.get('content-type', ''))

                    # 파일명 생성 (product_id 기반)
                    filename = f"{product_id}{ext}"
                    file_path = self.cache_dir / filename

                    # 파일 저장
                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    return f"/static/icons/{filename}"

        except Exception as e:
            print(f"Icon download error: {e}")

        return None

    @staticmethod
    def _get_extension(url: str, content_type: str) -> str:
        """파일 확장자 결정"""
        if 'png' in content_type:
            return '.png'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'svg' in content_type:
            return '.svg'
        elif url.endswith('.png'):
            return '.png'
        elif url.endswith('.jpg') or url.endswith('.jpeg'):
            return '.jpg'
        else:
            return '.png'  # 기본값
```

**Phase 2 완료 체크리스트:**
- [ ] 파일명 파싱 유닛 테스트 작성 및 통과
- [ ] AI API 연동 테스트 (실제 OpenAI API 키 필요)
- [ ] 메타데이터가 자동으로 생성되는지 확인
- [ ] 아이콘 이미지가 다운로드되고 캐싱되는지 확인
- [ ] Fallback 로직 테스트 (API 키 없을 때)

---

## Phase 3: 고급 기능 및 최적화

### Step 3.1: 자동 스캔 스케줄러

**backend/app/core/scheduler.py:**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.core.scanner import FileScanner
from app.database import SessionLocal

class ScanScheduler:
    """
    주기적 자동 스캔 스케줄러
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scan_paths = []  # 설정에서 로드

    def start(self, cron_expression: str = "0 2 * * *"):
        """
        스케줄러 시작
        기본값: 매일 새벽 2시
        """
        self.scheduler.add_job(
            self._run_scan,
            CronTrigger.from_crontab(cron_expression),
            id='auto_scan',
            replace_existing=True
        )
        self.scheduler.start()

    async def _run_scan(self):
        """
        스케줄된 스캔 실행
        """
        db = SessionLocal()
        try:
            # 설정된 모든 경로 스캔
            for path in self.scan_paths:
                scanner = FileScanner(db, use_ai=True)
                results = await scanner.scan_directory_async(path)
                print(f"Scheduled scan completed: {results}")
        finally:
            db.close()

    def stop(self):
        """스케줄러 중지"""
        self.scheduler.shutdown()

# 전역 스케줄러 인스턴스
scan_scheduler = ScanScheduler()
```

**main.py에 스케줄러 추가:**
```python
from app.core.scheduler import scan_scheduler

@app.on_event("startup")
async def startup_event():
    # 스케줄러 시작 (설정에서 경로와 cron 표현식 로드 필요)
    # scan_scheduler.start()
    pass

@app.on_event("shutdown")
async def shutdown_event():
    scan_scheduler.stop()
```

### Step 3.2: 대시보드 UI

**frontend/src/views/Home.vue:**
```vue
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 통계 카드 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-gray-500 text-sm">Total Programs</h3>
        <p class="text-3xl font-bold">{{ stats.total_products }}</p>
      </div>
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-gray-500 text-sm">Total Files</h3>
        <p class="text-3xl font-bold">{{ stats.total_versions }}</p>
      </div>
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-gray-500 text-sm">Last Scan</h3>
        <p class="text-lg">{{ stats.last_scan }}</p>
      </div>
    </div>

    <!-- 최근 추가된 앱 (Netflix 스타일) -->
    <section class="mb-8">
      <h2 class="text-2xl font-bold mb-4">Recently Added</h2>
      <div class="overflow-x-auto">
        <div class="flex space-x-4 pb-4">
          <ProductCard
            v-for="product in recentProducts"
            :key="product.id"
            :product="product"
            class="flex-shrink-0 w-48"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ProductCard from '../components/product/ProductCard.vue';
import { productsApi } from '../api/products';

const stats = ref({
  total_products: 0,
  total_versions: 0,
  last_scan: 'Never'
});

const recentProducts = ref([]);

onMounted(async () => {
  // API 호출하여 데이터 로드
  const response = await productsApi.getRecent();
  recentProducts.value = response.data;
});
</script>
```

### Step 3.3: 상세 페이지 탭 구조

**frontend/src/views/ProductDetail.vue:**
```vue
<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 헤더 -->
    <div class="bg-white rounded-lg shadow p-8 mb-6">
      <div class="flex items-start space-x-6">
        <img
          :src="product.icon_url || '/default-icon.png'"
          class="w-32 h-32 rounded-lg"
        />
        <div class="flex-1">
          <h1 class="text-3xl font-bold mb-2">{{ product.title }}</h1>
          <p class="text-gray-600 mb-2">{{ product.vendor }}</p>
          <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
            {{ product.category }}
          </span>
        </div>
      </div>
    </div>

    <!-- 탭 -->
    <div class="bg-white rounded-lg shadow">
      <div class="border-b">
        <nav class="flex space-x-8 px-8">
          <button
            @click="activeTab = 'info'"
            :class="tabClass('info')"
          >
            정보
          </button>
          <button
            @click="activeTab = 'versions'"
            :class="tabClass('versions')"
          >
            버전
          </button>
          <button
            @click="activeTab = 'resources'"
            :class="tabClass('resources')"
          >
            자료실
          </button>
        </nav>
      </div>

      <div class="p-8">
        <!-- 정보 탭 -->
        <div v-if="activeTab === 'info'">
          <h3 class="text-lg font-semibold mb-4">설명</h3>
          <p class="text-gray-700">{{ product.description }}</p>
        </div>

        <!-- 버전 탭 -->
        <div v-if="activeTab === 'versions'">
          <h3 class="text-lg font-semibold mb-4">다운로드 가능한 버전</h3>
          <div class="space-y-3">
            <div
              v-for="version in product.versions"
              :key="version.id"
              class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
            >
              <div>
                <p class="font-medium">{{ version.file_name }}</p>
                <p class="text-sm text-gray-500">
                  Version {{ version.version_name }} • {{ formatSize(version.file_size) }}
                </p>
              </div>
              <button
                @click="download(version.id)"
                class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                Download
              </button>
            </div>
          </div>
        </div>

        <!-- 자료실 탭 -->
        <div v-if="activeTab === 'resources'">
          <h3 class="text-lg font-semibold mb-4">추가 자료</h3>
          <p class="text-gray-500">No additional resources available.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { productsApi } from '../api/products';

const route = useRoute();
const product = ref({});
const activeTab = ref('info');

const tabClass = (tab) => {
  return activeTab.value === tab
    ? 'py-4 border-b-2 border-blue-500 text-blue-600 font-medium'
    : 'py-4 text-gray-500 hover:text-gray-700';
};

const formatSize = (bytes) => {
  if (bytes >= 1073741824) return (bytes / 1073741824).toFixed(2) + ' GB';
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(2) + ' MB';
  return (bytes / 1024).toFixed(2) + ' KB';
};

const download = async (versionId) => {
  // 다운로드 API 호출
  window.open(`http://localhost:8110/api/download/${versionId}`, '_blank');
};

onMounted(async () => {
  const response = await productsApi.getById(route.params.id);
  product.value = response.data;
});
</script>
```

### Step 3.4: 다운로드 API (X-Accel-Redirect)

**backend/app/api/download.py:**
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.version import Version
import os

router = APIRouter()

@router.get("/{version_id}")
def download_file(version_id: int, db: Session = Depends(get_db)):
    """
    파일 다운로드 (Nginx X-Accel-Redirect 사용)
    """
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="File not found")

    # 파일 존재 확인
    if not os.path.exists(version.file_path):
        raise HTTPException(status_code=404, detail="Physical file not found")

    # Nginx X-Accel-Redirect 헤더 사용
    # Nginx 설정에서 /protected/ 경로를 내부 경로로 매핑 필요
    internal_path = version.file_path.replace('/mnt/software', '/protected')

    return Response(
        headers={
            'X-Accel-Redirect': internal_path,
            'Content-Disposition': f'attachment; filename="{version.file_name}"'
        }
    )
```

**Phase 3 완료 체크리스트:**
- [ ] 자동 스캔 스케줄러 동작 확인
- [ ] 대시보드에 통계 표시 확인
- [ ] 제품 상세 페이지 탭 전환 동작 확인
- [ ] 다운로드 기능 테스트
- [ ] 모바일 반응형 디자인 확인

---

## 테스트 및 배포

### 테스트 체크리스트

#### 기능 테스트
- [ ] 최초 실행 시 Setup 페이지로 리다이렉트
- [ ] 관리자 계정 생성 및 로그인
- [ ] 파일 스캔 (신규 프로그램 등록)
- [ ] 파일 스캔 (기존 프로그램에 버전 추가)
- [ ] AI 메타데이터 생성 (OpenAI API 연동)
- [ ] 아이콘 다운로드 및 캐싱
- [ ] 제품 목록 조회
- [ ] 제품 상세 정보 조회
- [ ] 파일 다운로드
- [ ] 자동 스캔 스케줄러

#### 성능 테스트
- [ ] 1000개 파일 스캔 시간 측정
- [ ] 대용량 파일(5GB+) 다운로드 속도
- [ ] 동시 사용자 10명 접속 테스트

#### 보안 테스트
- [ ] 비로그인 상태에서 다운로드 차단
- [ ] SQL Injection 방어
- [ ] XSS 방어
- [ ] JWT 토큰 만료 처리

### 배포 가이드

#### 1. 환경 변수 설정

```bash
# .env 파일 생성
cp backend/.env.example backend/.env

# 필수 값 입력
SECRET_KEY=<랜덤 문자열>
OPENAI_API_KEY=<OpenAI API 키>
```

#### 2. Docker Compose 실행

```bash
# 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

#### 3. 데이터 백업

```bash
# PostgreSQL 백업
docker exec myapp-db pg_dump -U postgres myappstore > backup.sql

# 아이콘 백업
tar -czf icons_backup.tar.gz data/icons/
```

---

## 다음 단계 (선택적 기능)

### 추가 개발 아이디어

1. **검색 기능 고도화**
   - Elasticsearch 연동
   - 전문 검색 (Full-text search)
   - 자동완성

2. **사용자 기능**
   - 즐겨찾기
   - 다운로드 히스토리
   - 리뷰 및 별점

3. **관리 기능**
   - 메타데이터 수동 편집
   - 중복 파일 탐지
   - 용량 분석 대시보드

4. **알림 기능**
   - 신규 소프트웨어 추가 알림
   - 업데이트 알림
   - Webhook 연동

5. **다국어 지원**
   - i18n 설정
   - 한국어/영어 전환

---

## 문제 해결 (Troubleshooting)

### 자주 발생하는 문제

#### 1. Docker 컨테이너가 시작되지 않음
```bash
# 로그 확인
docker-compose logs backend

# 포트 충돌 확인
lsof -i :8110
lsof -i :5900
```

#### 2. DB 마이그레이션 오류
```bash
# 컨테이너 접속
docker exec -it myapp-backend bash

# 수동 마이그레이션
alembic upgrade head
```

#### 3. AI API 호출 실패
- OpenAI API 키 확인
- 네트워크 연결 확인
- API 사용량 제한 확인

#### 4. 파일 스캔 실패
- 경로 접근 권한 확인
- Docker 볼륨 마운트 확인
- NAS 네트워크 연결 확인

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Vue.js 공식 문서](https://vuejs.org/)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [OpenAI API 문서](https://platform.openai.com/docs/)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
