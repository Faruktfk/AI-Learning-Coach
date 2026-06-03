import re
from typing import Any, Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag

import json
import time
import hashlib
from pathlib import Path
from urllib.parse import urlencode


DROP_SECTION_TITLES = {
    # English
    "references",
    "reference",
    "sources",
    "notes",
    "footnotes",
    "citations",
    "bibliography",
    "further reading",
    "external links",
    "see also",
    "related pages",
    "links",

    # German
    "einzelnachweise",
    "nachweise",
    "referenzen",
    "quellen",
    "belege",
    "anmerkungen",
    "fußnoten",
    "fussnoten",
    "literatur",
    "weiterführende literatur",
    "weiterfuehrende literatur",
    "weblinks",
    "web-links",
    "externe links",
    "siehe auch",
    "verwandte themen",
    "verwandte artikel",
    "links",

    # Common variants
    "quellen und einzelnachweise",
    "literatur und quellen",
    "einzelnachweise und anmerkungen",
    "anmerkungen und einzelnachweise",
    "webseiten",
    "webseite",
    "internetquellen",
    "onlinequellen",
}

DROP_SELECTORS = [
    "style",
    "script",
    "noscript",

    # Wikipedia UI / metadata
    ".mw-editsection",
    ".mw-empty-elt",
    ".shortdescription",
    ".hatnote",
    ".navigation-not-searchable",

    # References / citations
    "sup.reference",
    "span.reference",
    ".reflist",
    ".mw-references-wrap",

    # Boxes/tables that are usually bad for plain learning chunks
    "table.infobox",
    "table.navbox",
    "table.sidebar",
    "table.metadata",
    "table.ambox",
    "table.vertical-navbox",

    # Media and layout
    ".thumb",
    ".gallery",
    ".mw-gallery",
    ".toc",
]


session = requests.Session()
session.headers.update(
    {
        # Wikimedia asks API users to set an informative User-Agent with contact info.
        # Replace this with your real project/contact later.
        "User-Agent": "AdaptiveWikiTutor/0.1 (contact@example.com)"
    }
)



CACHE_DIR = Path(".wiki_cache")
CACHE_DIR.mkdir(exist_ok=True)

REQUEST_DELAY_SECONDS = 1.0
MAX_RETRIES = 5



_last_request_time = 0.0

def get_wiki_api_url(language: str = "en") -> str:
    return f"https://{language}.wikipedia.org/w/api.php"

def cache_key(url: str, params: Dict[str, Any]) -> str:
    """
    Creates a stable cache filename from URL + params.
    """
    encoded = urlencode(sorted(params.items()), doseq=True)
    raw = f"{url}?{encoded}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_from_cache(key: str) -> Optional[Dict[str, Any]]:
    path = CACHE_DIR / f"{key}.json"

    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_to_cache(key: str, data: Dict[str, Any]) -> None:
    path = CACHE_DIR / f"{key}.json"

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def throttle_requests() -> None:
    """
    Ensures we do not send requests too quickly.
    Very useful while developing in notebooks.
    """
    global _last_request_time

    now = time.time()
    elapsed = now - _last_request_time

    if elapsed < REQUEST_DELAY_SECONDS:
        time.sleep(REQUEST_DELAY_SECONDS - elapsed)

    _last_request_time = time.time()


def safe_get(url: str, params: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
    key = cache_key(url, params)

    if use_cache:
        cached = load_from_cache(key)
        if cached is not None:
            return cached

    for attempt in range(MAX_RETRIES):
        throttle_requests()

        response = session.get(url, params=params, timeout=20)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")

            if retry_after is not None and retry_after.isdigit():
                sleep_seconds = int(retry_after)
            else:
                sleep_seconds = 2 ** attempt

            print(f"Rate limited by Wikipedia. Waiting {sleep_seconds} seconds...")
            time.sleep(sleep_seconds)
            continue

        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            raise RuntimeError(
                f"Expected JSON but got {content_type}:\n{response.text[:300]}"
            )

        data = response.json()

        if use_cache:
            save_to_cache(key, data)

        return data

    raise RuntimeError("Wikipedia API rate limit still active after several retries.")

def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def normalize_section_title(title: str) -> str:
    title = normalize_whitespace(title)
    title = re.sub(r"\[edit\]", "", title, flags=re.IGNORECASE)
    return title.strip()


def is_dropped_section_title(title: str) -> bool:
    normalized = title.lower().strip()
    return normalized in DROP_SECTION_TITLES


def search_first_article_title(query: str, lang: str = "en") -> str:
    data = safe_get(
        get_wiki_api_url(lang),
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 1,
            "format": "json",
            "formatversion": 2,
        },
    )

    results = data.get("query", {}).get("search", [])

    if not results:
        raise ValueError(f"No Wikipedia article found for query: {query!r}")

    return results[0]["title"]


def fetch_article_html(title: str, lang: str = "en") -> tuple[str, str]:
    data = safe_get(
        get_wiki_api_url(lang),
        params={
            "action": "parse",
            "page": title,
            "prop": "text",
            "redirects": 1,
            "format": "json",
            "formatversion": 2,
        },
    )

    parsed = data.get("parse")
    if not parsed:
        raise RuntimeError(f"Could not parse page: {title!r}")

    final_title = parsed.get("title", title)
    html = parsed.get("text", "")

    if not html:
        raise RuntimeError(f"Empty article HTML for page: {title!r}")

    return final_title, html


def remove_unwanted_html(soup: BeautifulSoup) -> None:
    for selector in DROP_SELECTORS:
        for element in soup.select(selector):
            element.decompose()


def extract_heading_info(element: Tag) -> Optional[Tuple[int, str]]:
    """
    Returns:
        (heading_level, heading_title)

    Example:
        <h2>History</h2> -> (2, "History")
        <h3>Formation</h3> -> (3, "Formation")

    Also supports newer MediaWiki structure:
        <div class="mw-heading mw-heading2"><h2>History</h2></div>
    """
    if element.name in {"h2", "h3", "h4", "h5", "h6"}:
        level = int(element.name[1])
        title = normalize_section_title(element.get_text(" ", strip=True))
        return level, title

    classes = element.get("class", [])

    if element.name == "div" and any(str(c).startswith("mw-heading") for c in classes):
        heading = element.find(["h2", "h3", "h4", "h5", "h6"], recursive=False)

        if heading:
            level = int(heading.name[1])
            title = normalize_section_title(heading.get_text(" ", strip=True))
            return level, title

    return None


def element_to_text(element: Tag) -> str:
    """
    Converts useful article elements to plain text.
    We keep paragraphs and lists, but ignore most layout elements.
    """
    if element.name in {"p", "ul", "ol", "dl", "blockquote"}:
        return normalize_whitespace(element.get_text(" ", strip=True))

    return ""


def flush_section(
    sections: list[dict[str, str]],
    title: str,
    content_parts: list[str],
    min_words: int,
) -> None:
    content = normalize_whitespace("\n\n".join(part for part in content_parts if part.strip()))

    if not content:
        return

    if is_dropped_section_title(title):
        return

    # Avoid chunks that are only tiny link lists or empty fragments.
    if word_count(content) < min_words:
        return

    sections.append(
        {
            "title": title,
            "content": content,
        }
    )


def html_to_sections(html: str, min_words: int = 40) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    remove_unwanted_html(soup)

    root = soup.select_one("div.mw-parser-output")
    if root is None:
        root = soup

    sections = []

    current_title = "Introduction"
    current_parts = []
    currently_dropping_section = False

    for child in root.children:
        if not isinstance(child, Tag):
            continue

        heading_info = extract_heading_info(child)

        if heading_info is not None:
            heading_level, heading_title = heading_info

            # h2 starts a new main section/chunk
            if heading_level == 2:
                flush_section(
                    sections=sections,
                    title=current_title,
                    content_parts=current_parts,
                    min_words=min_words,
                )

                current_title = heading_title
                current_parts = []
                currently_dropping_section = is_dropped_section_title(current_title)
                continue

            # h3/h4/h5/h6 stay inside the current h2 section
            if heading_level > 2:
                if not currently_dropping_section:
                    current_parts.append(f"\n{heading_title}\n")
                continue

        if currently_dropping_section:
            continue

        text = element_to_text(child)
        if text:
            current_parts.append(text)

    flush_section(
        sections=sections,
        title=current_title,
        content_parts=current_parts,
        min_words=min_words,
    )

    return sections


def get_wikipedia_article(query: str, min_words: int = 40, lang: str = "en") -> dict[str, Any]:
    title = search_first_article_title(query, lang=lang)
    final_title, html = fetch_article_html(title, lang=lang)
    sections = html_to_sections(html, min_words=min_words)

    if not sections:
        raise RuntimeError(f"No usable sections extracted from article: {final_title!r}")

    return {
        "title": final_title,
        "sections": sections,
    }


