import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.db.models.work import Work


logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Service responsible for resolving full job URL
    and extracting readable job text.
    """

    PROVIDER_URLS = {
        "StartupJobs": "https://www.startupjobs.cz",
        "CoolJobs": "https://www.cooljobs.eu/cz/",
        "JobStackIT": "https://www.jobstack.it",
        "Titans": "https://join.titans.eu/cs/",
        "JobsCZ": "https://www.jobs.cz/",
    }

    def get_work_text(self, work: Work) -> str:
        # return self._get_fake_text()

        if work.Description and len(work.Description) > 100:
            return self._parse_html(work.Description)
    
        full_url = self._build_full_url(work)

        if full_url:
            scraped = self._scrape_url(full_url)
            if scraped and len(scraped) > 300:
                return scraped

        return work.Description or ""

    def _build_full_url(self, work: Work) -> Optional[str]:
        base = self.PROVIDER_URLS.get(work.Provider)

        if not base:
            return None

        if not work.Url:
            return None

        return f"{base}{work.Url}"

    def _scrape_url(self, url: str) -> Optional[str]:
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; CVMatcherBot/1.0)"
                },
            )
            response.raise_for_status()

            return self._parse_html(response.text)

        except Exception as e:
            logger.warning(f"Scraping failed for URL {url}: {e}")
            return None

    def _parse_html(self, html_text: str) -> str:
        try:
            soup = BeautifulSoup(html_text, "html.parser")

            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            text = soup.get_text(separator="\n")

            return self._clean_text(text)

        except Exception as e:
            logger.warning(f"Parsing failed: {e}")
            return None

    def _clean_text(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)

    def _get_fake_text(self) -> str:
        return """
        Data Processing & Platform

        Databricks

        Spark

        Unity Catalog

        Data Engineering Concepts

        ETL / ELT pipeline design

        Data pipelines

        Data transformation

        Data cleaning

        Data architecture

        Performance optimization

        Orchestration

        Airflow

        DBT

        Cloud Platforms

        AWS

        Azure

        Programming

        Python

        SQL

        (optional: R, Scala, Matlab)

        DevOps / Deployment

        CI/CD

        DevOps practices

        Data Infrastructure

        Cloud data solutions

        Production data deployment

        Analytical tools

        Predictive models
        """