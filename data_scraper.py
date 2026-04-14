"""
PCCOE OneBridge — Real Data Scraper Module
Scrapes scholarships from Buddy4Study/MahaDBT and internships from Internshala.
All data cached as local JSON files. Zero paid APIs.
"""

import asyncio
import json
import os
import re
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "scraped_data"
CACHE_DIR.mkdir(exist_ok=True)

SCHOLARSHIP_CACHE = CACHE_DIR / "scholarships.json"
INTERNSHIP_CACHE = CACHE_DIR / "internships.json"
STATUS_FILE = CACHE_DIR / "scrape_status.json"
SEED_SCHOLARSHIPS = CACHE_DIR / "seed_scholarships.json"
SEED_INTERNSHIPS = CACHE_DIR / "seed_internships.json"

CACHE_MAX_AGE_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "24"))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pick_ua() -> str:
    import random
    return random.choice(USER_AGENTS)


def _cache_is_fresh(path: Path) -> bool:
    if not path.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age < timedelta(hours=CACHE_MAX_AGE_HOURS)


def _save_json(path: Path, data):
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_json(path: Path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _update_status(section: str, count: int, error: str = None):
    status = _load_json(STATUS_FILE) or {}
    status[section] = {
        "last_scraped": datetime.now().isoformat(),
        "count": count,
        "error": error,
    }
    _save_json(STATUS_FILE, status)


# ---------------------------------------------------------------------------
# Category auto-detection from eligibility text
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Caste": ["sc ", "st ", "obc", "vjnt", "sbc", "nt ", "scheduled caste",
              "scheduled tribe", "backward class", "minority", "minorities"],
    "Income": ["income", "ebc", "economically", "ews", "bpl", "below poverty",
               "financial", "need-based", "means"],
    "Gender": ["female", "women", "girl", "woman", "kanya", "pragati", "wings4her"],
    "Disability": ["disability", "disabled", "pwd", "divyang", "saksham",
                   "differently abled", "handicap"],
    "Merit": ["merit", "topper", "cgpa", "percentile", "rank", "academic excellence",
              "talent"],
}


def _auto_categorize(text: str) -> str:
    text_lower = text.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in text_lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Merit"


# ---------------------------------------------------------------------------
# Buddy4Study Scraper
# ---------------------------------------------------------------------------

async def _scrape_buddy4study(client: httpx.AsyncClient) -> list[dict]:
    """Scrape scholarship listings from Buddy4Study."""
    urls = [
        "https://www.buddy4study.com/scholarships/class-12-passed",
        "https://www.buddy4study.com/scholarships/engineering",
        "https://www.buddy4study.com/scholarships/maharashtra",
    ]
    all_scholarships = []
    seen_names = set()

    for url in urls:
        try:
            await asyncio.sleep(2)  # rate limit
            resp = await client.get(url, follow_redirects=True, timeout=20.0)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Buddy4Study renders scholarship cards as <a> blocks with structured text
            # Each card contains: title, deadline, award, eligibility
            cards = soup.select("a[href*='/scholarship/'], a[href*='/page/']")

            for card in cards:
                text = card.get_text(" ", strip=True)
                href = card.get("href", "")
                if not href or len(text) < 20:
                    continue

                # Skip non-scholarship links
                if any(skip in href for skip in ["/article/", "/blog/", "/about", "/contact", "/terms"]):
                    continue

                # Extract title (usually the first strong/heading text or the link text itself)
                title_el = card.select_one("strong, h3, h4, b, .scholarship_name, .scholarship-name")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    # Try to extract from full text — title is usually ALL CAPS portion
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    title = lines[0] if lines else text[:80]

                # Normalize title
                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) < 5 or title.lower() in seen_names:
                    continue
                seen_names.add(title.lower())

                # Extract deadline
                deadline_match = re.search(
                    r'(?:Deadline[:\s]*)?(\d{1,2}[\s-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s-]\d{4})',
                    text, re.IGNORECASE
                )
                if not deadline_match:
                    deadline_match = re.search(r'(\d{1,2}-\w{3}-\d{4})', text)
                deadline = deadline_match.group(1) if deadline_match else ""

                # Try to parse deadline into ISO format
                deadline_iso = ""
                if deadline:
                    for fmt in ["%d-%b-%Y", "%d %b %Y", "%d %B %Y", "%d-%B-%Y"]:
                        try:
                            deadline_iso = datetime.strptime(deadline.strip(), fmt).strftime("%Y-%m-%d")
                            break
                        except ValueError:
                            continue

                # Extract award amount
                award_match = re.search(
                    r'(?:Award|Amount|Scholarship)[:\s]*((?:₹|INR|Rs\.?|EUR|€|\$|GBP|£)[\s\d,.\-]+(?:lakh|L|per\s*(?:year|annum|month))?[^A-Z]*?)(?:Eligibility|Last|$)',
                    text, re.IGNORECASE
                )
                amount = award_match.group(1).strip() if award_match else ""
                if not amount:
                    # Simpler pattern for INR amounts
                    amount_match2 = re.search(r'((?:₹|INR\s?)[\d,]+(?:\s*(?:per|/)\s*(?:year|annum|month))?)', text, re.IGNORECASE)
                    amount = amount_match2.group(1).strip() if amount_match2 else ""

                # Extract eligibility
                elig_match = re.search(r'Eligibility[:\s]*(.+?)(?:Last Updated|$)', text, re.IGNORECASE)
                eligibility = elig_match.group(1).strip() if elig_match else ""
                eligibility = eligibility[:200]  # truncate

                # Build full URL
                if href.startswith("/"):
                    href = "https://www.buddy4study.com" + href
                elif not href.startswith("http"):
                    href = "https://www.buddy4study.com/" + href

                if title and (amount or eligibility or deadline_iso):
                    all_scholarships.append({
                        "name": title,
                        "category": _auto_categorize(f"{title} {eligibility}"),
                        "eligibility": eligibility or "Check portal for details",
                        "amount": amount or "Variable",
                        "deadline": deadline_iso or "Rolling",
                        "matchPct": 70,  # default; will be adjusted
                        "provider": "Buddy4Study",
                        "link": href,
                    })

            logger.info(f"Buddy4Study: scraped {len(all_scholarships)} from {url}")

        except Exception as e:
            logger.warning(f"Buddy4Study scrape failed for {url}: {e}")
            continue

    return all_scholarships


# ---------------------------------------------------------------------------
# MahaDBT Scraper
# ---------------------------------------------------------------------------

async def _scrape_mahadbt(client: httpx.AsyncClient) -> list[dict]:
    """Scrape Maharashtra scholarship scheme names from MahaDBT."""
    schemes = []
    try:
        await asyncio.sleep(2)
        resp = await client.get(
            "https://mahadbt.maharashtra.gov.in/",
            follow_redirects=True, timeout=20.0
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # MahaDBT lists schemes as JS-driven links with text like:
        # "Government of India Post-Matric Scholarship", etc.
        scheme_links = soup.select("a[onclick*='ShowDs'], a[href*='ShowDs']")

        for link in scheme_links:
            name = link.get_text(strip=True)
            if not name or len(name) < 10:
                continue
            # Skip non-scholarship items (agriculture, farmer, etc.)
            skip_terms = ["farmer", "krishi", "cotton", "soybean", "sugarcane",
                          "horticulture", "irrigation", "mechanization", "rainfed",
                          "pension", "labour", "apprenticeship", "nsmny"]
            if any(term in name.lower() for term in skip_terms):
                continue

            schemes.append({
                "name": name,
                "category": _auto_categorize(name),
                "eligibility": "Maharashtra domicile. Apply via MahaDBT portal.",
                "amount": "As per scheme norms",
                "deadline": "Rolling",
                "matchPct": 65,
                "provider": "MahaDBT",
                "link": "https://mahadbt.maharashtra.gov.in/",
            })

        logger.info(f"MahaDBT: scraped {len(schemes)} schemes")

    except Exception as e:
        logger.warning(f"MahaDBT scrape failed: {e}")

    return schemes


# ---------------------------------------------------------------------------
# Internshala Scraper
# ---------------------------------------------------------------------------

async def _scrape_internshala(client: httpx.AsyncClient) -> list[dict]:
    """Scrape engineering internship listings from Internshala."""
    urls = [
        "https://internshala.com/internships/engineering-internship",
        "https://internshala.com/internships/internship-in-pune",
    ]
    all_internships = []
    seen_titles = set()

    for url in urls:
        try:
            await asyncio.sleep(2)
            resp = await client.get(url, follow_redirects=True, timeout=20.0)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            cards = soup.select(".individual_internship")
            if not cards:
                cards = soup.select(".internship_meta")

            for card in cards:
                # Title — Internshala uses <a class="job-title-href">
                title_el = card.select_one(".job-title-href, h3, .profile, a[href*='/internship/detail/']")
                title = title_el.get_text(strip=True) if title_el else ""

                if not title:
                    if card.name == "a":
                        title = card.get_text(strip=True)[:80]
                    else:
                        continue

                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) < 3 or title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())

                # Company — <p class="company-name"> (may contain "Actively hiring" badge text)
                company_el = card.select_one(".company-name, .company_name, .link_display_like_text")
                company = ""
                if company_el:
                    # Remove "Actively hiring" badge text that leaks in
                    badge = company_el.select_one(".actively-hiring-badge")
                    if badge:
                        badge.decompose()
                    company = company_el.get_text(strip=True)

                # Stipend
                stipend_el = card.select_one(".stipend, [class*='stipend']")
                stipend = stipend_el.get_text(strip=True) if stipend_el else ""
                if not stipend:
                    text = card.get_text(" ", strip=True)
                    stipend_match = re.search(r'(₹[\s\d,]+(?:\s*[-–/]\s*[\d,]+)?\s*/\s*month)', text, re.IGNORECASE)
                    stipend = stipend_match.group(1) if stipend_match else ""

                # Location
                location_el = card.select_one(".location_link, [class*='location']")
                location = location_el.get_text(strip=True) if location_el else ""

                # Duration
                text = card.get_text(" ", strip=True)
                duration_match = re.search(r'(\d+)\s*(?:Months?|weeks?)', text, re.IGNORECASE)
                duration = duration_match.group(0) if duration_match else ""

                # Link
                link = ""
                link_el = card.select_one("a[href*='/internship/detail/']") or (card if card.name == "a" else None)
                if link_el:
                    href = link_el.get("href", "")
                    if href.startswith("/"):
                        link = "https://internshala.com" + href
                    elif href.startswith("http"):
                        link = href

                # Description from skills/key details
                skills_els = card.select(".job_skill, .round_tabs, .skill_tag, span[class*='round']")
                skills = ", ".join(s.get_text(strip=True) for s in skills_els[:5]) if skills_els else ""

                if title and len(title) > 3:
                    desc_parts = []
                    if location:
                        desc_parts.append(f"Location: {location}")
                    if duration:
                        desc_parts.append(f"Duration: {duration}")
                    if skills:
                        desc_parts.append(f"Skills: {skills}")

                    all_internships.append({
                        "title": title,
                        "company": company or "—",
                        "listing_type": "internship",
                        "branch": "Engineering",
                        "year": "All Years",
                        "stipend": stipend or "Check listing",
                        "deadline": "",
                        "description": ". ".join(desc_parts) if desc_parts else "See full listing on Internshala.",
                        "source": "Internshala",
                        "link": link,
                    })

            logger.info(f"Internshala: scraped {len(all_internships)} from {url}")

        except Exception as e:
            logger.warning(f"Internshala scrape failed for {url}: {e}")
            continue

    return all_internships



def _load_seed_scholarships() -> list[dict]:
    """Load curated seed scholarships from JSON file, including status field."""
    raw = _load_json(SEED_SCHOLARSHIPS) or []
    out = []
    for item in raw:
        out.append({
            "name": item.get("name", ""),
            "category": item.get("category") or _auto_categorize(f"{item.get('name','')} {item.get('eligibility','')}") ,
            "eligibility": item.get("eligibility", "Check portal for details"),
            "amount": item.get("amount", "Variable"),
            "deadline": item.get("deadline", "Rolling"),
            "status": item.get("status", "open"),
            "matchPct": 70,
            "provider": item.get("provider") or item.get("source", "Buddy4Study"),
            "link": item.get("link", ""),
        })
    logger.info(f"Loaded {len(out)} seed scholarships")
    return out

def _load_seed_internships() -> list[dict]:
    """Load curated seed internships from JSON file, including status field."""
    raw = _load_json(SEED_INTERNSHIPS) or []
    out = []
    for item in raw:
        out.append({
            "title": item.get("title", ""),
            "provider": item.get("provider", ""),
            "category": item.get("category", ""),
            "eligibility": item.get("eligibility", "Check portal for details"),
            "stipend": item.get("stipend", "Variable"),
            "deadline": item.get("deadline", "Rolling"),
            "status": item.get("status", "open"),
            "link": item.get("link", ""),
        })
    logger.info(f"Loaded {len(out)} seed internships")
    return out


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def _dedupe_scholarships(items: list[dict]) -> list[dict]:
    seen = {}
    for item in items:
        key = re.sub(r'[^a-z0-9]', '', item["name"].lower())[:40]
        if key not in seen:
            seen[key] = item
    result = list(seen.values())
    # Assign sequential IDs
    for i, s in enumerate(result, 1):
        s["id"] = i
    # Vary matchPct slightly for visual interest
    import random
    for s in result:
        base = s.get("matchPct", 70)
        s["matchPct"] = max(30, min(98, base + random.randint(-10, 15)))
    return result


def _dedupe_internships(items: list[dict]) -> list[dict]:
    seen = {}
    for item in items:
        key = re.sub(r'[^a-z0-9]', '', f"{item['title']}{item['company']}".lower())[:50]
        if key not in seen:
            seen[key] = item
    result = list(seen.values())
    for i, s in enumerate(result, 1):
        s["id"] = i
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def scrape_all(force: bool = False) -> dict:
    """
    Main entry point. Scrapes scholarships and internships, saving to cache.
    Returns summary dict with counts.
    Skips if cache is fresh unless force=True.
    """
    results = {"scholarships": 0, "internships": 0, "errors": []}

    async with httpx.AsyncClient(
        headers={"User-Agent": _pick_ua(), "Accept-Language": "en-IN,en;q=0.9"},
        follow_redirects=True,
        timeout=30.0,
    ) as client:


        # --- Scholarships ---
        if force or not _cache_is_fresh(SCHOLARSHIP_CACHE):
            try:
                buddy = await _scrape_buddy4study(client)
                mahadbt = await _scrape_mahadbt(client)
                seed = _load_seed_scholarships()
                all_schol = _dedupe_scholarships(seed + buddy + mahadbt)
                _save_json(SCHOLARSHIP_CACHE, all_schol)
                _update_status("scholarships", len(all_schol))
                results["scholarships"] = len(all_schol)
                logger.info(f"Scholarships scraped: {len(all_schol)}")
            except Exception as e:
                msg = f"Scholarship scrape failed: {e}"
                logger.error(msg)
                results["errors"].append(msg)
                _update_status("scholarships", 0, str(e))
        else:
            cached = _load_json(SCHOLARSHIP_CACHE)
            results["scholarships"] = len(cached) if cached else 0
            logger.info("Scholarships: cache is fresh, skipping scrape")

        # --- Internships ---
        if force or not _cache_is_fresh(INTERNSHIP_CACHE):
            try:
                internships = await _scrape_internshala(client)
                seed_intern = _load_seed_internships()
                all_intern = _dedupe_internships(seed_intern + internships)
                _save_json(INTERNSHIP_CACHE, all_intern)
                _update_status("internships", len(all_intern))
                results["internships"] = len(all_intern)
                logger.info(f"Internships scraped: {len(all_intern)}")
            except Exception as e:
                msg = f"Internship scrape failed: {e}"
                logger.error(msg)
                results["errors"].append(msg)
                _update_status("internships", 0, str(e))
        else:
            cached = _load_json(INTERNSHIP_CACHE)
            results["internships"] = len(cached) if cached else 0
            logger.info("Internships: cache is fresh, skipping scrape")

    return results


def get_cached_scholarships() -> list[dict]:
    """Return cached scholarships list, or empty list if none."""
    return _load_json(SCHOLARSHIP_CACHE) or []


def get_cached_internships() -> list[dict]:
    """Return cached internships list, or empty list if none."""
    return _load_json(INTERNSHIP_CACHE) or []


def get_scrape_status() -> dict:
    """Return scrape timestamps and counts."""
    return _load_json(STATUS_FILE) or {}


# ---------------------------------------------------------------------------
# CLI entry point for standalone execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print("Starting OneBridge Data Scraper...")
    result = asyncio.run(scrape_all(force=True))
    print(f"\nScrape complete:")
    print(f"  Scholarships: {result['scholarships']}")
    print(f"  Internships:  {result['internships']}")
    if result["errors"]:
        print(f"  Errors: {', '.join(result['errors'])}")
    print(f"\nCached files in: {CACHE_DIR}")
