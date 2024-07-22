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

from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import InvalidArgumentException
from webdriver_manager.chrome import ChromeDriverManager
import logging
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import List
from pathlib import Path
from omniparse.web.utils import wrap_text

logger = logging.getLogger("selenium.webdriver.remote.remote_connection")
logger.setLevel(logging.WARNING)

logger_driver = logging.getLogger("selenium.webdriver.common.service")
logger_driver.setLevel(logging.WARNING)

urllib3_logger = logging.getLogger("urllib3.connectionpool")
urllib3_logger.setLevel(logging.WARNING)

# Disable http.client logging
http_client_logger = logging.getLogger("http.client")
http_client_logger.setLevel(logging.WARNING)

# Disable driver_finder and service logging
driver_finder_logger = logging.getLogger("selenium.webdriver.common.driver_finder")
driver_finder_logger.setLevel(logging.WARNING)


class CrawlerStrategy(ABC):
    @abstractmethod
    def crawl(self, url: str, **kwargs) -> str:
        pass

    @abstractmethod
    def take_screenshot(self, save_path: str):
        pass

    @abstractmethod
    def update_user_agent(self, user_agent: str):
        pass


class LocalSeleniumCrawlerStrategy(CrawlerStrategy):
    def __init__(self, use_cached_html=False, js_code=None, **kwargs):
        super().__init__()
        self.options = Options()
        self.options.headless = True
        if kwargs.get("user_agent"):
            self.options.add_argument("--user-agent=" + kwargs.get("user_agent"))
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--headless")
        # self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        # self.options.add_argument("--disable-extensions")
        # self.options.add_argument("--disable-infobars")
        # self.options.add_argument("--disable-logging")
        # self.options.add_argument("--disable-popup-blocking")
        # self.options.add_argument("--disable-translate")
        # self.options.add_argument("--disable-default-apps")
        # self.options.add_argument("--disable-background-networking")
        # self.options.add_argument("--disable-sync")
        # self.options.add_argument("--disable-features=NetworkService,NetworkServiceInProcess")
        # self.options.add_argument("--disable-browser-side-navigation")
        # self.options.add_argument("--dns-prefetch-disable")
        # self.options.add_argument("--disable-web-security")
        self.options.add_argument("--log-level=3")
        self.use_cached_html = use_cached_html
        self.use_cached_html = use_cached_html
        self.js_code = js_code
        self.verbose = kwargs.get("verbose", False)

        # chromedriver_autoinstaller.install()
        # import chromedriver_autoinstaller
        self.service = Service(ChromeDriverManager().install())
        self.service.log_path = "NUL"
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def update_user_agent(self, user_agent: str):
        self.options.add_argument(f"user-agent={user_agent}")
        self.driver.quit()
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def crawl(self, url: str) -> str:
        try:
            if self.verbose:
                print(f"[LOG] Crawling {url} using Web Crawler...")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "html"))
            )

            # Execute JS code if provided
            if self.js_code and type(self.js_code) == str:
                self.driver.execute_script(self.js_code)
                # Optionally, wait for some condition after executing the JS code
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState")
                    == "complete"
                )
            elif self.js_code and type(self.js_code) == list:
                for js in self.js_code:
                    self.driver.execute_script(js)
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: driver.execute_script(
                            "return document.readyState"
                        )
                        == "complete"
                    )

            html = self.driver.page_source
            if self.verbose:
                print(f"[LOG] ✅ Crawled {url} successfully!")

            return html
        except InvalidArgumentException:
            raise InvalidArgumentException(f"Invalid URL {url}")
        except Exception as e:
            raise Exception(f"Failed to crawl {url}: {str(e)}")

    def take_screenshot(self) -> str:
        try:
            # Get the dimensions of the page
            total_width = self.driver.execute_script("return document.body.scrollWidth")
            total_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            # Set the window size to the dimensions of the page
            self.driver.set_window_size(total_width, total_height)

            # Take screenshot
            screenshot = self.driver.get_screenshot_as_png()

            # Open the screenshot with PIL
            image = Image.open(BytesIO(screenshot))

            # Convert to JPEG and compress
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            if self.verbose:
                print(f"[LOG] 📸 Screenshot taken and converted to base64")

            return img_base64

        except Exception as e:
            error_message = f"Failed to take screenshot: {str(e)}"
            print(error_message)

            # Generate an image with black background
            img = Image.new("RGB", (800, 600), color="black")
            draw = ImageDraw.Draw(img)

            # Load a font
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except IOError:
                font = ImageFont.load_default(size=40)

            # Define text color and wrap the text
            text_color = (255, 255, 255)
            max_width = 780
            wrapped_text = wrap_text(draw, error_message, font, max_width)

            # Calculate text position
            text_position = (10, 10)

            # Draw the text on the image
            draw.text(text_position, wrapped_text, fill=text_color, font=font)

            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            return img_base64

    def quit(self):
        self.driver.quit()
