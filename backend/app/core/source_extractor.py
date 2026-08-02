"""
소스 기반 메타데이터 생성을 위한 텍스트 추출 모듈

사용자가 제공한 URL 또는 파일(txt/md/pdf)에서 본문 텍스트만 추출해
AIMetadataGeneratorV2.generate_metadata_from_source()에 전달한다.
"""
import ipaddress
import logging
import socket
from typing import Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_SOURCE_TEXT_CHARS = 8000
REQUEST_TIMEOUT = 15.0


class SourceFetchError(Exception):
    """URL/파일에서 텍스트를 가져오지 못했을 때 발생 (사용자에게 보여줄 메시지 포함)"""
    pass


def _is_private_or_reserved(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return (
        ip.is_private or ip.is_loopback or ip.is_link_local
        or ip.is_reserved or ip.is_multicast or ip.is_unspecified
    )


def _assert_public_host(host: str) -> None:
    """host가 사설/예약 IP로 리졸브되면 차단 (SSRF 방지).

    리다이렉트로 우회될 수 있으므로 이 검증은 최초 요청뿐 아니라 각
    리다이렉트 홉마다 다시 수행해야 한다 (fetch_url_text에서 처리).

    주의(TOCTOU): 여기서 검증에 사용한 DNS 응답과 httpx가 실제 연결 시
    다시 조회하는 DNS 응답이 다를 수 있다 (짧은 TTL을 이용한 DNS
    rebinding 공격). 완전히 막으려면 여기서 확인한 IP를 그대로 pinning해
    httpx가 그 IP로 연결하도록 강제해야 하는데, 관리자 전용으로만 노출되는
    개인 NAS 환경이라는 위협 모델을 고려해 이 정도 검증으로 충분하다고
    판단하고 pinning은 하지 않았다. 더 엄격한 환경에서 재사용할 경우
    이 TOCTOU 윈도우를 반드시 막을 것.
    """
    try:
        addrinfo = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise SourceFetchError(f"호스트를 찾을 수 없습니다: {host}") from e

    for family, _, _, _, sockaddr in addrinfo:
        ip_str = sockaddr[0]
        if _is_private_or_reserved(ip_str):
            raise SourceFetchError("내부/사설 네트워크 주소로는 접근할 수 없습니다.")


async def fetch_url_text(url: str, max_redirects: int = 5) -> str:
    """URL에서 HTML을 받아 본문 텍스트만 추출 (SSRF 방지 적용).

    - http/https 스킴만 허용
    - 요청 전 호스트를 리졸브해 사설/예약 IP 차단
    - 리다이렉트를 자동으로 따라가지 않고 매 홉마다 재검증 (자동 추적 시
      공개 호스트가 169.254.169.254 등으로 302를 걸어 사전 검증을 우회할 수 있음)
    - Content-Length를 신뢰하지 않고 스트리밍하며 5MB 초과 시 중단
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    current_url = url

    for _ in range(max_redirects + 1):
        parsed = urlparse(current_url)
        if parsed.scheme not in ("http", "https"):
            raise SourceFetchError("http/https URL만 지원합니다.")
        if not parsed.hostname:
            raise SourceFetchError("올바르지 않은 URL입니다.")

        _assert_public_host(parsed.hostname)

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=False) as client:
            try:
                async with client.stream("GET", current_url, headers=headers) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("location")
                        if not location:
                            raise SourceFetchError("리다이렉트 응답에 Location 헤더가 없습니다.")
                        current_url = str(httpx.URL(current_url).join(location))
                        continue

                    if response.status_code != 200:
                        raise SourceFetchError(f"URL 요청 실패 (HTTP {response.status_code})")

                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type and "application/xhtml" not in content_type:
                        raise SourceFetchError(f"지원하지 않는 콘텐츠 타입입니다: {content_type or '알 수 없음'}")

                    chunks = []
                    total = 0
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if total > MAX_RESPONSE_BYTES:
                            raise SourceFetchError("응답 크기가 5MB를 초과합니다.")
                        chunks.append(chunk)

                    html = b"".join(chunks).decode(response.encoding or "utf-8", errors="ignore")
                    return _extract_text_from_html(html)
            except httpx.TimeoutException as e:
                raise SourceFetchError("URL 요청 시간이 초과되었습니다.") from e
            except httpx.HTTPError as e:
                raise SourceFetchError(f"URL 요청 중 오류가 발생했습니다: {e}") from e

    raise SourceFetchError("리다이렉트가 너무 많습니다.")


def _extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    return text[:MAX_SOURCE_TEXT_CHARS]


def extract_text_from_file(filename: str, content: bytes) -> str:
    """업로드된 파일(txt/md/pdf)에서 텍스트 추출.

    Args:
        filename: 원본 파일명 (확장자 판별용)
        content: 파일 바이트

    Returns:
        추출된 텍스트 (MAX_SOURCE_TEXT_CHARS로 트렁케이트)
    """
    if len(content) > MAX_RESPONSE_BYTES:
        raise SourceFetchError("파일 크기가 5MB를 초과합니다.")

    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext in ("txt", "md"):
        text = content.decode("utf-8", errors="ignore")
    elif ext == "pdf":
        text = _extract_text_from_pdf(content)
    else:
        raise SourceFetchError(f"지원하지 않는 파일 형식입니다: .{ext or '(확장자 없음)'}")

    return text[:MAX_SOURCE_TEXT_CHARS]


def _extract_text_from_pdf(content: bytes) -> str:
    from io import BytesIO
    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(content))
        pages_text = []
        for page in reader.pages:
            pages_text.append(page.extract_text() or "")
        return "\n".join(pages_text)
    except Exception as e:
        raise SourceFetchError(f"PDF 텍스트 추출에 실패했습니다: {e}") from e
