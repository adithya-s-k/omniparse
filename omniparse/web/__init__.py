from .web_crawler import WebCrawler

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from omniparse.web.utils import import_strategy

async def parse_url(url: str , model_state) -> dict:
    try:
        logging.debug("[LOG] Loading extraction and chunking strategies...")
        
        # Hardcoded parameters (adjust as needed)
        include_raw_html = False
        bypass_cache = False
        extract_blocks = True
        word_count_threshold = 5
        extraction_strategy = "NoExtractionStrategy"
        extraction_strategy_args = {"verbose": True}
        chunking_strategy = "RegexChunking"
        chunking_strategy_args = {"verbose": True}
        css_selector = None
        screenshot = True
        user_agent = None
        verbose = True
        
        extraction_strategy = import_strategy("omniparse.web.extraction_strategy", extraction_strategy, **extraction_strategy_args)
        chunking_strategy = import_strategy("omniparse.web.chunking_strategy", chunking_strategy, **chunking_strategy_args)

        # Use ThreadPoolExecutor to run the synchronous WebCrawler in async manner
        logging.debug("[LOG] Running the WebCrawler...")
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(
                executor, 
                model_state.crawler.run,
                str(url),
                word_count_threshold,
                extraction_strategy,
                chunking_strategy,
                bypass_cache,
                css_selector,
                screenshot,
                user_agent,
                verbose
            )
            result = await future

        # if include_raw_html is False, remove the raw HTML content from the results
        if not include_raw_html:
            result.html = None

        return {"message": "Website parsed successfully", "result": result.model_dump()}

    except Exception as e:
        logging.error(f"[ERROR] Error parsing webpage: {str(e)}")
        return {"message": "Error in parsing webpage", "error": str(e)}