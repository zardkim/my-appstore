# Google Custom Search API Debugging Guide

This guide will help you diagnose and fix issues with Google image search in MyApp Store.

## Problem: "검색 결과가 없습니다" (No search results)

If you're seeing this message when searching for images, follow these steps:

---

## Step 1: Verify Backend is Running

Check if the backend is running:
```bash
docker-compose ps
```

You should see `backend` with status `Up`. If not, start it:
```bash
docker-compose up -d backend
```

---

## Step 2: Run Diagnostic Script

Run the automated diagnostic script:
```bash
cd /home/nuricom/project/myappStore
./test_google_api.sh
```

This script will:
1. Check if backend is running
2. Verify config.json has Google API settings
3. Test Google API connectivity directly
4. Show detailed error messages if any

---

## Step 3: Verify API Configuration

### Check Settings Page

1. Open MyApp Store in browser: http://localhost:5900
2. Go to **Settings** → **Metadata** section
3. Scroll down to **Google Custom Search API 설정**
4. Verify both fields are filled:
   - **Google Custom Search API 키**: Should start with `AIzaSy...`
   - **Programmable Search Engine ID**: Should be a long alphanumeric string

### If Settings Are Empty

1. Get your Google API credentials:
   - API Key: https://console.cloud.google.com/apis/credentials
   - Search Engine ID: https://programmablesearchengine.google.com/

2. Follow the setup guide in the Settings page (green box)

3. Click **적용** button to save

4. Verify `backend/data/config/config.json` contains:
```json
{
  "metadata": {
    "googleApiKey": "AIzaSy...",
    "googleSearchEngineId": "..."
  }
}
```

---

## Step 4: Test in Frontend

### Using MetadataTestDialog

1. Go to **Admin** page
2. Open **메타데이터 테스트** section
3. Enter a software name (e.g., "Adobe Photoshop")
4. Click the green **이미지 검색** button (NOT "메타데이터 생성")
5. Click **로고 검색** or **스크린샷 검색**

### Expected Behavior

**Success**:
- You should see image thumbnails in a grid
- Select images and click **선택한 이미지 저장**

**Failure - API Not Configured**:
- Red error message: "Google Custom Search API가 설정되지 않았습니다..."
- **Fix**: Go to Settings and configure API (see Step 3)

**Failure - No Results**:
- Message: "검색 결과가 없습니다. 다른 검색어를 시도해보세요."
- **Possible causes**:
  1. Search query too specific (version numbers are automatically removed)
  2. Software name not well-known
  3. Try different search query

**Failure - API Error**:
- Red error message with technical details
- **Common errors**:

  **403 Forbidden - Quota Exceeded**:
  - You've used all 100 free queries for today
  - Check quota: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
  - Wait until tomorrow or upgrade to paid plan

  **403 Forbidden - Permission Denied**:
  - API Key is invalid or doesn't have permissions
  - Verify Custom Search API is enabled in Google Cloud Console
  - Check API Key restrictions (IP, referrer, etc.)

  **400 Bad Request**:
  - Search Engine ID is incorrect
  - Verify Search Engine ID at: https://programmablesearchengine.google.com/

---

## Step 5: Check Backend Logs

If the frontend shows an error, check backend terminal logs for details:

```bash
docker-compose logs -f backend
```

Look for these log patterns:

### Successful Search
```
[Images API] Logo search request received
[Images API] Query: 'Adobe Photoshop'
[Images API] Limit: 10
[Images API] Calling searcher.search_logo()...
[Google Search] Query: 'Adobe Photoshop logo'
[Google Search] API Key: AIzaSyABCDE...XYZ
[Google Search] Search Engine ID: 0123456789abcdef:ghijklmn
[Google Search] Filters: {'imgType': 'clipart', 'imgSize': 'medium', 'safe': 'active'}
[Google Search] Response status: 200
[Google Search] Found 10 results
[Images API] Search completed, found 10 results
```

### API Not Configured
```
[Images API] Logo search request received
[Images API] Query: 'Adobe Photoshop'
[Images API] ERROR: Google Custom Search API가 설정되지 않았습니다...
```

### API Error (403)
```
[Google Search] Response status: 403
[Google Search] ERROR 403: Quota exceeded or permission denied
[Google Search] Response: {"error": {"code": 403, "message": "..."}}
```

### API Error (400)
```
[Google Search] Response status: 400
[Google Search] ERROR 400: Invalid request
[Google Search] Response: {"error": {"code": 400, "message": "..."}}
```

---

## Step 6: Test Google API Directly

Run the Python test script independently:

```bash
cd /home/nuricom/project/myappStore/backend
python3 test_google_api_connectivity.py
```

This will:
- Load your config.json
- Show masked API Key and Search Engine ID
- Make direct API calls to Google
- Show detailed success/error messages

---

## Common Issues and Solutions

### Issue 1: "검색 결과가 없습니다" (No results found)

**Cause**: Google API is working, but query returns no results

**Solutions**:
1. Try a different, more common software name
2. Remove extra details from search query (version numbers are auto-removed)
3. Test with well-known software: "Adobe Photoshop", "Microsoft Word", "Google Chrome"

---

### Issue 2: Red Error Message with "Google API가 설정되지 않았거나..."

**Cause**: API credentials not saved in config.json

**Solutions**:
1. Go to Settings → Metadata
2. Re-enter Google API Key and Search Engine ID
3. Click **적용** button
4. Verify `backend/data/config/config.json` was updated
5. Restart backend if needed: `docker-compose restart backend`

---

### Issue 3: 403 Quota Exceeded

**Cause**: You've used all 100 free searches for today

**Solutions**:
1. Wait until tomorrow (quota resets at midnight Pacific Time)
2. Check usage: https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas
3. Upgrade to paid plan (first 100/day free, then $5 per 1000 queries)

---

### Issue 4: 403 Permission Denied (but quota not exceeded)

**Cause**: API Key restrictions or Custom Search API not enabled

**Solutions**:
1. Go to: https://console.cloud.google.com/apis/library/customsearch.googleapis.com
2. Click "Enable" if not already enabled
3. Check API Key restrictions:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click your API Key
   - Under "API restrictions", ensure "Custom Search API" is allowed
   - Under "Application restrictions", ensure your IP/domain is allowed

---

### Issue 5: 400 Bad Request

**Cause**: Invalid Search Engine ID or malformed query

**Solutions**:
1. Verify Search Engine ID at: https://programmablesearchengine.google.com/
2. Copy the exact Search Engine ID (cx parameter)
3. Re-enter in Settings and click **적용**

---

## Testing Checklist

- [ ] Backend is running (`docker-compose ps`)
- [ ] Settings → Metadata has Google API Key filled in
- [ ] Settings → Metadata has Search Engine ID filled in
- [ ] Clicked **적용** button to save settings
- [ ] `backend/data/config/config.json` contains googleApiKey and googleSearchEngineId
- [ ] Ran `./test_google_api.sh` successfully
- [ ] Backend logs show `[Google Search] Response status: 200`
- [ ] Frontend image search shows image results
- [ ] Can select and save images successfully

---

## Still Having Issues?

1. **Check Browser Console** (F12 → Console tab):
   - Look for network errors
   - Check API response data

2. **Check Browser Network Tab** (F12 → Network tab):
   - Find `/api/images/search-logo` request
   - Check response status and body

3. **Check Backend Terminal**:
   - Look for `[Google Search]` and `[Images API]` logs
   - Note any error messages or stack traces

4. **Verify Google Cloud Console**:
   - Custom Search API is enabled
   - API Key is valid and has no restrictions
   - Quota is not exceeded
   - Billing is enabled (required for API access)

5. **Test with curl** (manual API call):
```bash
API_KEY="your_api_key_here"
CX="your_search_engine_id_here"
curl "https://www.googleapis.com/customsearch/v1?key=${API_KEY}&cx=${CX}&q=Adobe+Photoshop+logo&searchType=image&imgType=clipart&num=5"
```

If curl returns results but frontend doesn't work, the issue is with your MyApp Store configuration.

If curl also fails, the issue is with your Google API credentials or quota.

---

## Need More Help?

Provide the following information when asking for help:

1. Output of `./test_google_api.sh`
2. Backend terminal logs (especially `[Google Search]` lines)
3. Browser console errors (F12 → Console)
4. Screenshot of Settings → Metadata → Google API section
5. Screenshot of error message in frontend
