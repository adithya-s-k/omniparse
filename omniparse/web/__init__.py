import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from omniparse.web.utils import import_strategy

async def parse_url(url: str , model_state) -> dict:
    try:
        logging.debug("[LOG] Loading extraction and chunking strategies...")
        
        # Hardcoded parameters (adjust as needed)
        include_raw_html = False
        bypass_cache = True
        word_count_threshold = 5
        css_selector = None
        screenshot = True
        user_agent = None
        verbose = True
        
        # Use ThreadPoolExecutor to run the synchronous WebCrawler in async manner
        logging.debug("[LOG] Running the WebCrawler...")
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(
                executor, 
                model_state.crawler.run,
                str(url),
                word_count_threshold,
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