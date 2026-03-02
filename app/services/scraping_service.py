# import logging
# from typing import Optional, Literal

# import requests
# from bs4 import BeautifulSoup

# from app.db.models.work import Work
from app.core.utils import get_work_full_url


# logger = logging.getLogger(__name__)


# class ScrapingService:
#     """
#     Service responsible for resolving full job URL
#     and extracting readable job text.
#     """

#     def scrape_work_description(self, work: Work, format: Literal["html", "plain"] = "plain") -> str:
#         work_full_url = get_work_full_url(work)

#         if work_full_url is None:
#             return None

#         html_text = self._scrape_url(work_full_url)

#         if not (html_text and len(html_text)):
#             return None
        
#         html_description = self._extract_content_jobstack(html_text)

#         if not (html_description and len(html_description)):
#             return None
        
#         return html_description if format == "html" else self._parse_html_jobstack(html_description)


#     def get_work_text(self, work: Work) -> str:
#         # return self._get_fake_text()

#         if work.Description and len(work.Description) > 100:
#             return self._parse_html(work.Description)
    
#         work_full_url = get_work_full_url(work)

#         if work_full_url:
#             scraped = self._scrape_url(work_full_url)
#             if scraped and len(scraped) > 300:
#                 return scraped

#         return work.Description or ""

#     def _scrape_url(self, url: str) -> Optional[str]:
#         try:
#             response = requests.get(
#                 url,
#                 timeout=10,
#                 headers={
#                     "User-Agent": "Mozilla/5.0 (compatible; CVMatcherBot/1.0)"
#                 },
#             )
#             response.raise_for_status()

#             return response.text

#         except Exception as e:
#             logger.warning(f"Scraping failed for URL {url}: {e}")
#             return None
        
#     def _extract_content_jobstack(self, html_text: str):
#         soup = BeautifulSoup(html_text, "html.parser")

#         # odstranění skriptů atd.
#         for tag in soup(["script", "style", "noscript"]):
#             tag.decompose()

#         # cílový div
#         content = soup.select_one("div.wysiwyg-content.pt-20")

#         return content
        
#     def _parse_html_jobstack(self, html_text: str) -> str:
#         try:
#             soup = BeautifulSoup(html_text, "html.parser")

#             # odstraníme script/style
#             for tag in soup(["script", "style", "noscript"]):
#                 tag.decompose()

#             # najdeme hlavní popis pozice
#             content = soup.find("div", class_="wysiwyg-content")

#             if not content:
#                 return None

#             text = content.get_text(separator="\n")

#             return ScrapingService.clean_text(text)

#         except Exception as e:
#             logger.warning(f"Parsing failed: {e}")
#             return None

#     def _parse_html(self, html_text: str) -> str:
#         try:
#             soup = BeautifulSoup(html_text, "html.parser")

#             for tag in soup(["script", "style", "noscript"]):
#                 tag.decompose()

#             text = soup.get_text(separator="\n")

#             return ScrapingService.clean_text(text)

#         except Exception as e:
#             logger.warning(f"Parsing failed: {e}")
#             return None

#     def _clean_text(self, text: str) -> str:
#         lines = [line.strip() for line in text.splitlines()]
#         lines = [line for line in lines if line]
#         return "\n".join(lines)

#     def _get_fake_text(self) -> str:
#         return """
#         Data Processing & Platform

#         Databricks

#         Spark

#         Unity Catalog

#         Data Engineering Concepts

#         ETL / ELT pipeline design

#         Data pipelines

#         Data transformation

#         Data cleaning

#         Data architecture

#         Performance optimization

#         Orchestration

#         Airflow

#         DBT

#         Cloud Platforms

#         AWS

#         Azure

#         Programming

#         Python

#         SQL

#         (optional: R, Scala, Matlab)

#         DevOps / Deployment

#         CI/CD

#         DevOps practices

#         Data Infrastructure

#         Cloud data solutions

#         Production data deployment

#         Analytical tools

#         Predictive models
#         """


import requests
import logging
from typing import Optional, Literal
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ScrapingService:
    """
    Service responsible for resolving full job URL
    and extracting readable job text.
    """

    def scrape_work_text(
        self,
        work,
        format: Literal["html", "plain"] = "plain"
    ) -> Optional[str]:

        work_full_url = get_work_full_url(work)
        if not work_full_url:
            return None

        raw_html = self._scrape_url(work_full_url)
        if not raw_html:
            return None

        content_div = self._extract_content_div(raw_html)
        if not content_div:
            return None

        if format == "html":
            return self._clean_html(content_div)

        return ScrapingService.html_to_text(content_div)

    def get_work_text(self, work) -> str:
        if work.Description and len(work.Description) > 100:
            return ScrapingService.clean_text(work.Description)

        work_full_url = get_work_full_url(work)
        if not work_full_url:
            return work.Description or ""

        raw_html = self._scrape_url(work_full_url)
        if not raw_html:
            return work.Description or ""

        content_div = self._extract_content_div(raw_html)
        if not content_div:
            return work.Description or ""

        return ScrapingService.html_to_text(content_div)

    # ------------------------
    # Internal helpers
    # ------------------------

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
            return response.text

        except Exception as e:
            logger.warning(f"Scraping failed for URL {url}: {e}")
            return None

    def _extract_content_div(self, html_text: str):
        """
        Extracts main job description div.
        """

        soup = BeautifulSoup(html_text, "html.parser")

        # remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # primary selector (current Jobstack structure)
        content = soup.select_one("div.wysiwyg-content.pt-20")

        if content:
            return content

        # fallback: find section by header
        header = soup.find(lambda tag: tag.name in ["h2", "h1"] and "Popis pozice" in tag.get_text())
        if header:
            return header.find_next("div")

        return None

    def _clean_html(self, element) -> str:
        """
        Removes all attributes from tags but keeps structure.
        """

        for tag in element.find_all(True):
            tag.attrs = {}

        return str(element)

    @staticmethod
    def html_to_text(element) -> str:
        """
        Converts extracted HTML block into clean text.
        """

        text = element.get_text(separator="\n")
        return ScrapingService.clean_text(text)

    @staticmethod
    def clean_text(text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)
    

    @staticmethod
    def strip_html(html: str) -> str:
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        # pryč se šumem
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # zachovat základní strukturu (odstavce/řádky)
        text = soup.get_text(separator="\n", strip=True)

        # zredukovat prázdné řádky
        lines = [ln.strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines)