"""
Tests for the data_scraper module.
Validates seed loading, deduplication, categorization, and HTML parsing.
"""
import json
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import data_scraper


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_INTERNSHALA_HTML = """
<html><body>
<div class="individual_internship">
  <a class="job-title-href" href="/internship/detail/software-dev-intern-at-acme-12345">Software Development</a>
  <p class="company-name">Acme Corp<div class="actively-hiring-badge">Actively hiring</div></p>
  <a class="location_link" href="#">Pune</a>
  <span class="stipend">₹ 10,000 /month</span>
</div>
<div class="individual_internship">
  <a class="job-title-href" href="/internship/detail/data-science-intern-56789">Data Science</a>
  <p class="company-name">DataCo</p>
  <a class="location_link" href="#">Mumbai</a>
  <span class="stipend">₹ 15,000 - 20,000 /month</span>
</div>
</body></html>
"""

SAMPLE_MAHADBT_HTML = """
<html><body>
<a onclick="ShowDs('1')">Government of India Post-Matric Scholarship</a>
<a onclick="ShowDs('2')">Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Scholarship</a>
<a onclick="ShowDs('3')">Dr. Panjabrao Deshmukh Vastigruh Nirvah Bhatta Yojana</a>
<a onclick="ShowDs('4')">Farmer Krishi Subsidy Scheme</a>
</body></html>
"""


# ---------------------------------------------------------------------------
# Category auto-detection
# ---------------------------------------------------------------------------

class TestAutoCategorizeFn:
    def test_sc_st_keywords(self):
        assert data_scraper._auto_categorize("SC ST OBC students scholarship") == "Caste"

    def test_gender_keywords(self):
        assert data_scraper._auto_categorize("Female women girls scholarship") == "Gender"

    def test_disability_keywords(self):
        assert data_scraper._auto_categorize("Disabled pwd divyang students") == "Disability"

    def test_merit_keywords(self):
        assert data_scraper._auto_categorize("Merit topper rank scholarship") == "Merit"

    def test_income_keywords(self):
        assert data_scraper._auto_categorize("EWS economically weaker BPL") == "Income"

    def test_default_merit(self):
        assert data_scraper._auto_categorize("Engineering program 2026") == "Merit"


# ---------------------------------------------------------------------------
# Seed loading
# ---------------------------------------------------------------------------

class TestSeedLoading:
    def test_load_seed_scholarships(self):
        result = data_scraper._load_seed_scholarships()
        assert isinstance(result, list)
        assert len(result) >= 20  # We have 25 seed entries
        for item in result:
            assert "name" in item
            assert "category" in item
            assert "eligibility" in item
            assert "amount" in item
            assert "provider" in item

    def test_seed_has_real_data(self):
        result = data_scraper._load_seed_scholarships()
        names = [s["name"] for s in result]
        # Check a few known scholarships are present
        assert any("LPUNEST" in n for n in names)
        assert any("Vigyan Jyoti" in n for n in names)
        assert any("DRDO" in n for n in names)


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

class TestDeduplication:
    def test_dedupe_scholarships_removes_duplicates(self):
        items = [
            {"name": "Test Scholarship 2026", "matchPct": 70},
            {"name": "Test Scholarship 2026", "matchPct": 80},
            {"name": "Different Scholarship", "matchPct": 65},
        ]
        result = data_scraper._dedupe_scholarships(items)
        assert len(result) == 2
        assert all("id" in s for s in result)

    def test_dedupe_internships_removes_duplicates(self):
        items = [
            {"title": "Software Dev", "company": "Acme"},
            {"title": "Software Dev", "company": "Acme"},
            {"title": "Data Science", "company": "Other"},
        ]
        result = data_scraper._dedupe_internships(items)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_dedupe_assigns_sequential_ids(self):
        items = [
            {"name": f"Scholarship {i}", "matchPct": 70}
            for i in range(10)
        ]
        result = data_scraper._dedupe_scholarships(items)
        ids = [s["id"] for s in result]
        assert ids == list(range(1, 11))


# ---------------------------------------------------------------------------
# Internshala HTML parsing
# ---------------------------------------------------------------------------

class TestInternshalaParser:
    @pytest.mark.asyncio
    async def test_scrape_internshala_parses_cards(self):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_INTERNSHALA_HTML
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("data_scraper.asyncio.sleep", new_callable=AsyncMock):
            result = await data_scraper._scrape_internshala(mock_client)

        assert len(result) >= 2
        titles = [r["title"] for r in result]
        assert "Software Development" in titles
        assert "Data Science" in titles

        # Check company name doesn't include "Actively hiring"
        acme_entry = [r for r in result if r["title"] == "Software Development"][0]
        assert "Actively hiring" not in acme_entry["company"]
        assert acme_entry["company"] == "Acme Corp"
        assert "10,000" in acme_entry["stipend"]
        assert acme_entry["link"].endswith("software-dev-intern-at-acme-12345")


# ---------------------------------------------------------------------------
# MahaDBT HTML parsing
# ---------------------------------------------------------------------------

class TestMahaDBTParser:
    @pytest.mark.asyncio
    async def test_scrape_mahadbt_parses_schemes(self):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_MAHADBT_HTML
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("data_scraper.asyncio.sleep", new_callable=AsyncMock):
            result = await data_scraper._scrape_mahadbt(mock_client)

        # Should get 3 (farmer scheme filtered out)
        assert len(result) == 3
        names = [r["name"] for r in result]
        assert "Government of India Post-Matric Scholarship" in names
        # Farmer scheme should be filtered
        assert not any("Farmer" in n for n in names)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

class TestCacheHelpers:
    def test_save_and_load_json(self, tmp_path):
        test_file = tmp_path / "test.json"
        test_data = [{"key": "value", "num": 42}]
        data_scraper._save_json(test_file, test_data)
        loaded = data_scraper._load_json(test_file)
        assert loaded == test_data

    def test_load_nonexistent_returns_none(self, tmp_path):
        result = data_scraper._load_json(tmp_path / "missing.json")
        assert result is None

    def test_cache_is_fresh_for_new_file(self, tmp_path):
        test_file = tmp_path / "fresh.json"
        test_file.write_text("[]")
        assert data_scraper._cache_is_fresh(test_file) is True

    def test_cache_is_not_fresh_for_missing_file(self, tmp_path):
        assert data_scraper._cache_is_fresh(tmp_path / "nope.json") is False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class TestPublicAPI:
    def test_get_cached_scholarships_returns_list(self):
        result = data_scraper.get_cached_scholarships()
        assert isinstance(result, list)
        # After the scraper run we should have data
        if result:
            assert "name" in result[0]
            assert "id" in result[0]

    def test_get_cached_internships_returns_list(self):
        result = data_scraper.get_cached_internships()
        assert isinstance(result, list)
        if result:
            assert "title" in result[0]
            assert "id" in result[0]

    def test_get_scrape_status(self):
        result = data_scraper.get_scrape_status()
        assert isinstance(result, dict)
