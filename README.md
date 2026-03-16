# MyApp Store

<div align="center">

**Personal Software Library Manager for NAS**

[![Version](https://img.shields.io/badge/version-1.4.55-blue.svg)](https://github.com/zardkim/my-appstore/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/u/zardkim)

[🇺🇸 English](README.md) | [🇰🇷 한국어](README.ko.md)

</div>

---

## 📸 Screenshots

<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/01_home.jpg" alt="Home Dashboard"/><br/><sub>Home Dashboard</sub></td>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/02_store.jpg" alt="App Store"/><br/><sub>App Store</sub></td>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/03_product_detail.jpg" alt="Product Detail"/><br/><sub>Product Detail</sub></td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/04_product_detail2.jpg" alt="Product Detail (Features)"/><br/><sub>Detected List</sub></td>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/05_scan_list.jpg" alt="Detected List"/><br/><sub>Tips &amp; Tech</sub></td>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/06_tips_list.jpg" alt="Tips &amp; Tech"/><br/><sub>Tips &amp; Tech Detail</sub></td>
  </tr>
  <tr>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/07_settings_general.jpg" alt="Settings - General"/><br/><sub>Settings - Category</sub></td>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/08_settings_folder.jpg" alt="Settings - Folder"/><br/><sub>Settings - Data manager</sub></td>
    <td><img src="https://raw.githubusercontent.com/zardkim/my-appstore/main/screenshot/eng/09_settings_metadata.jpg" alt="Settings - Metadata"/><br/><sub>Settings - Metadata (AI)</sub></td>
  </tr>
</table>

---

## 🐳 Docker Installation

### 1. Download Files

```bash
mkdir myappstore && cd myappstore

wget https://raw.githubusercontent.com/zardkim/my-appstore/main/docker-compose.yml
wget https://raw.githubusercontent.com/zardkim/my-appstore/main/.env.example
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

### 3. Create Required Directories

```bash
mkdir -p db redis data/library
```

### 4. Start

```bash
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 5. Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5900 |
| Backend API | http://localhost:8110 |
| API Docs | http://localhost:8110/docs |

> On first access, an admin account setup wizard will run.

---

## ⚙️ Environment Variables (.env)

### Required

```bash
# Secret key (must change — generate with the command below)
# openssl rand -hex 32
SECRET_KEY=your-secret-key-change-this-in-production

# Database password
POSTGRES_PASSWORD=password
```

### Network

```bash
# Ports (default values recommended)
BACKEND_PORT=8110
FRONTEND_PORT=5900
POSTGRES_PORT=5433   # Avoids conflict with Synology's built-in PostgreSQL
REDIS_PORT=6380

# CORS (internal NAS: allow * / external domain: specify actual domain)
CORS_ORIGINS=*
```

### Access from Other Devices (Optional)

To access from other devices (PC, mobile) on the same network, set your NAS IP:

```bash
VITE_API_BASE_URL=http://192.168.0.100:8110/api
VITE_BACKEND_URL=http://192.168.0.100:8110
VITE_APP_URL=http://192.168.0.100:5900
```

> Not required if using a reverse proxy (Nginx, Synology, etc.)

---

## 🤖 AI API Key Setup

API keys are required to use AI-powered metadata generation (description, publisher, category).
Only **one** of OpenAI or Gemini is needed.

```bash
# OpenAI (GPT-4o-mini)
OPENAI_API_KEY=sk-...

# Google Gemini (Free tier available)
GEMINI_API_KEY=AI...
```

### Get API Keys

| Service | URL |
|---------|-----|
| OpenAI | https://platform.openai.com/api-keys |
| Google Gemini | https://aistudio.google.com/app/apikey |
| Google Custom Search (Image) | https://console.cloud.google.com (Custom Search API) |

> **Google Image Search**: Enable the Custom Search JSON API in Google Cloud Console, then create a Programmable Search Engine at https://programmablesearchengine.google.com and set `GOOGLE_API_KEY` + `GOOGLE_CSE_ID` in Settings → Metadata.

> API keys can be set in the `.env` file or entered directly in **Settings → Metadata** after logging in.

---

## 🔄 Update

```bash
docker-compose pull && docker-compose up -d
```

---

## 📦 Docker Images

- `zardkim/myappstore-backend:latest`
- `zardkim/myappstore-frontend:latest`

---

<div align="center">

Made by [zardkim](https://discord.gg/8amwMw2X) (.feat Claude)

</div>
