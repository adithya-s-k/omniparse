"""
Title: OmniParse
Author: Adithya S K
Date: 2024-07-02

This code includes portions of code from the crawl4ai repository by unclecode, licensed under the Apache 2.0 License.
Original repository: https://github.com/unclecode/crawl4ai

Original Author: unclecode

License: Apache 2.0 License
URL: https://github.com/unclecode/crawl4ai/blob/main/LICENSE
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional


class UrlModel(BaseModel):
    url: HttpUrl
    forced: bool = False


class CrawlResult(BaseModel):
    url: str
    html: str
    success: bool
    cleaned_html: Optional[str] = None
    media: Dict[str, List[Dict]] = {}
    links: Dict[str, List[Dict]] = {}
    screenshot: Optional[str] = None
    markdown: Optional[str] = None
    extracted_content: Optional[str] = None
    metadata: Optional[dict] = None
    error_message: Optional[str] = None
