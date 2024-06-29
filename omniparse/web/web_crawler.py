import os, time
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from pathlib import Path

from omniparse.web.models import UrlModel, CrawlResult
from omniparse.web.utils import *
from omniparse.web.chunking_strategy import *
from omniparse.web.extraction_strategy import *
from omniparse.web.crawler_strategy import *
from typing import List
from concurrent.futures import ThreadPoolExecutor
from omniparse.web.config import *


class WebCrawler:
    def __init__(
        self,
        # db_path: str = None,
        crawler_strategy: CrawlerStrategy = None,
        always_by_pass_cache: bool = True,
        verbose: bool = False,
    ):
        # self.db_path = db_path
        self.crawler_strategy = crawler_strategy or LocalSeleniumCrawlerStrategy(verbose=verbose)
        self.always_by_pass_cache = always_by_pass_cache
        self.ready = False
        
    def warmup(self):
        print("[LOG]   Warming up the WebCrawler")
        result = self.run(
            url='https://adithyask.com',
            word_count_threshold=5,
            extraction_strategy= NoExtractionStrategy(),
            bypass_cache=True,
            verbose = False
        )
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
        extraction_strategy: ExtractionStrategy = None,
        chunking_strategy: ChunkingStrategy = RegexChunking(),
        **kwargs,
    ) -> CrawlResult:
        return self.run(
            url_model.url,
            word_count_threshold,
            extraction_strategy or NoExtractionStrategy(),
            chunking_strategy,
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
        extraction_strategy: ExtractionStrategy = None,
        chunking_strategy: ChunkingStrategy = RegexChunking(),
        **kwargs,
    ) -> List[CrawlResult]:
        extraction_strategy = extraction_strategy or NoExtractionStrategy()
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
                    [extraction_strategy] * len(url_models),
                    [chunking_strategy] * len(url_models),
                    *[kwargs] * len(url_models),
                )
            )

        return results

    def run(
            self,
            url: str,
            word_count_threshold=MIN_WORD_THRESHOLD,
            extraction_strategy: ExtractionStrategy = None,
            chunking_strategy: ChunkingStrategy = RegexChunking(),
            bypass_cache: bool = False,
            css_selector: str = None,
            screenshot: bool = False,
            user_agent: str = None,
            verbose=True,
            **kwargs,
        ) -> CrawlResult:
            extracted_content = None
            cached=None
            extraction_strategy = extraction_strategy or NoExtractionStrategy()
            extraction_strategy.verbose = verbose
            if not isinstance(extraction_strategy, ExtractionStrategy):
                raise ValueError("Unsupported extraction strategy")
            if not isinstance(chunking_strategy, ChunkingStrategy):
                raise ValueError("Unsupported chunking strategy")
            
            if word_count_threshold < MIN_WORD_THRESHOLD:
                word_count_threshold = MIN_WORD_THRESHOLD
            
            else:
                if user_agent:
                    self.crawler_strategy.update_user_agent(user_agent)
                html = self.crawler_strategy.crawl(url)
                if screenshot:
                    screenshot = self.crawler_strategy.take_screenshot()
            
            return self.process_html(url, html, extracted_content, word_count_threshold, extraction_strategy, chunking_strategy, css_selector, screenshot, verbose, bool(cached), **kwargs)

    def process_html(
            self,
            url: str,
            html: str,
            extracted_content: str,
            word_count_threshold: int,
            extraction_strategy: ExtractionStrategy,
            chunking_strategy: ChunkingStrategy,
            css_selector: str,
            screenshot: bool,
            verbose: bool,
            is_cached: bool,
            **kwargs,
        ) -> CrawlResult:
            t = time.time()
            # Extract content from HTML
            try:
                result = get_content_of_website(url, html, word_count_threshold, css_selector=css_selector)
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
                print(f"[LOG]  Crawling done for {url}, success: True, time taken: {time.time() - t} seconds")
                        
            if extracted_content is None:
                if verbose:
                    print(f"[LOG]  Extracting semantic blocks for {url}, Strategy: {extraction_strategy.name}")

                sections = chunking_strategy.chunk(markdown)
                extracted_content = extraction_strategy.run(url, sections)
                extracted_content = json.dumps(extracted_content)

                if verbose:
                    print(f"[LOG]  Extraction done for {url}, time taken: {time.time() - t} seconds.")
                
            screenshot = None if not screenshot else screenshot          

            return CrawlResult(
                url=url,
                html=html,
                cleaned_html=cleaned_html,
                markdown=markdown,
                media=media,
                links=links,
                metadata=metadata,
                screenshot=screenshot,
                extracted_content=extracted_content,
                success=True,
                error_message="",
            )