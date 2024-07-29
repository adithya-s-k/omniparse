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

import os
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"
from omniparse.web.models import UrlModel
from omniparse.web.utils import (
    get_content_of_website,
    extract_metadata,
    InvalidCSSSelectorError,
)
from omniparse.web.crawler_strategy import CrawlerStrategy, LocalSeleniumCrawlerStrategy
from typing import List
from concurrent.futures import ThreadPoolExecutor
from omniparse.web.config import DEFAULT_PROVIDER, MIN_WORD_THRESHOLD
from omniparse.models import responseDocument


class WebCrawler:
    def __init__(
        self,
        crawler_strategy: CrawlerStrategy = None,
        always_by_pass_cache: bool = True,
        verbose: bool = False,
    ):
        self.crawler_strategy = crawler_strategy or LocalSeleniumCrawlerStrategy(
            verbose=verbose
        )
        self.always_by_pass_cache = always_by_pass_cache
        self.ready = False

    def warmup(self):
        print("[LOG]   Warming up the WebCrawler")
        result = self.run(
            url="https://adithyask.com",
            word_count_threshold=5,
            bypass_cache=True,
            verbose=False,
        )
        print(result)
        self.ready = True
        print("[LOG]  WebCrawler is ready to crawl")

    def fetch_page(
        self,
        url_model: UrlModel,
        provider: str = DEFAULT_PROVIDER,
        api_token: str = None,
        extract_blocks_flag: bool = True,
        word_count_threshold=MIN_WORD_THRESHOLD,
        css_selector: str = None,
        screenshot: bool = False,
        use_cached_html: bool = False,
        **kwargs,
    ) -> responseDocument:
        return self.run(
            url_model.url,
            word_count_threshold,
            bypass_cache=url_model.forced,
            css_selector=css_selector,
            screenshot=screenshot,
            **kwargs,
        )
        pass

    def fetch_pages(
        self,
        url_models: List[UrlModel],
        provider: str = DEFAULT_PROVIDER,
        api_token: str = None,
        extract_blocks_flag: bool = True,
        word_count_threshold=MIN_WORD_THRESHOLD,
        use_cached_html: bool = False,
        css_selector: str = None,
        screenshot: bool = False,
        **kwargs,
    ) -> List[responseDocument]:
        def fetch_page_wrapper(url_model, *args, **kwargs):
            return self.fetch_page(url_model, *args, **kwargs)

        with ThreadPoolExecutor() as executor:
            results = list(
                executor.map(
                    fetch_page_wrapper,
                    url_models,
                    [provider] * len(url_models),
                    [api_token] * len(url_models),
                    [extract_blocks_flag] * len(url_models),
                    [word_count_threshold] * len(url_models),
                    [css_selector] * len(url_models),
                    [screenshot] * len(url_models),
                    [use_cached_html] * len(url_models),
                    *[kwargs] * len(url_models),
                )
            )

        return results

    def run(
        self,
        url: str,
        word_count_threshold=MIN_WORD_THRESHOLD,
        bypass_cache: bool = False,
        css_selector: str = None,
        screenshot: bool = False,
        user_agent: str = None,
        verbose=True,
        **kwargs,
    ) -> responseDocument:
        extracted_content = None
        cached = None
        if word_count_threshold < MIN_WORD_THRESHOLD:
            word_count_threshold = MIN_WORD_THRESHOLD

        else:
            if user_agent:
                self.crawler_strategy.update_user_agent(user_agent)
            html = self.crawler_strategy.crawl(url)
            if screenshot:
                screenshot = self.crawler_strategy.take_screenshot()

        processed_html = self.process_html(
            url,
            html,
            extracted_content,
            word_count_threshold,
            css_selector,
            screenshot,
            verbose,
            bool(cached),
            **kwargs,
        )

        crawl_result = responseDocument(
            text=processed_html["markdown"], metadata=processed_html
        )
        crawl_result.add_image("screenshot", image_data=processed_html["screenshot"])
        return crawl_result

    def process_html(
        self,
        url: str,
        html: str,
        extracted_content: str,
        word_count_threshold: int,
        css_selector: str,
        screenshot: bool,
        verbose: bool,
        is_cached: bool,
        **kwargs,
    ):
        t = time.time()
        # Extract content from HTML
        try:
            result = get_content_of_website(
                url, html, word_count_threshold, css_selector=css_selector
            )
            metadata = extract_metadata(html)
            if result is None:
                raise ValueError(f"Failed to extract content from the website: {url}")
        except InvalidCSSSelectorError as e:
            raise ValueError(str(e))

        cleaned_html = result.get("cleaned_html", "")
        markdown = result.get("markdown", "")
        media = result.get("media", [])
        links = result.get("links", [])

        if verbose:
            print(
                f"[LOG]  Crawling done for {url}, success: True, time taken: {time.time() - t} seconds"
            )

        screenshot = None if not screenshot else screenshot

        return {
            "url": url,
            "html": html,
            "cleaned_html": cleaned_html,
            "markdown": markdown,
            "media": media,
            "links": links,
            "metadata": metadata,
            "screenshot": screenshot,
            "extracted_content": extracted_content,
            "success": True,
            "error_message": "",
        }
