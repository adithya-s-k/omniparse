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

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup, Comment, element, Tag, NavigableString
import html2text
import json
import html
import re
import os
from html2text import HTML2Text
from .prompts import PROMPT_EXTRACT_BLOCKS
from .config import *
from pathlib import Path


class InvalidCSSSelectorError(Exception):
    pass


def get_home_folder():
    home_folder = os.path.join(Path.home(), ".omniparse")
    os.makedirs(home_folder, exist_ok=True)
    os.makedirs(f"{home_folder}/cache", exist_ok=True)
    os.makedirs(f"{home_folder}/models", exist_ok=True)
    return home_folder


def beautify_html(escaped_html):
    """
    Beautifies an escaped HTML string.

    Parameters:
    escaped_html (str): A string containing escaped HTML.

    Returns:
    str: A beautifully formatted HTML string.
    """
    # Unescape the HTML string
    unescaped_html = html.unescape(escaped_html)

    # Use BeautifulSoup to parse and prettify the HTML
    soup = BeautifulSoup(unescaped_html, "html.parser")
    pretty_html = soup.prettify()

    return pretty_html


def split_and_parse_json_objects(json_string):
    """
    Splits a JSON string which is a list of objects and tries to parse each object.

    Parameters:
    json_string (str): A string representation of a list of JSON objects, e.g., '[{...}, {...}, ...]'.

    Returns:
    tuple: A tuple containing two lists:
        - First list contains all successfully parsed JSON objects.
        - Second list contains the string representations of all segments that couldn't be parsed.
    """
    # Trim the leading '[' and trailing ']'
    if json_string.startswith("[") and json_string.endswith("]"):
        json_string = json_string[1:-1].strip()

    # Split the string into segments that look like individual JSON objects
    segments = []
    depth = 0
    start_index = 0

    for i, char in enumerate(json_string):
        if char == "{":
            if depth == 0:
                start_index = i
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                segments.append(json_string[start_index : i + 1])

    # Try parsing each segment
    parsed_objects = []
    unparsed_segments = []

    for segment in segments:
        try:
            obj = json.loads(segment)
            parsed_objects.append(obj)
        except json.JSONDecodeError:
            unparsed_segments.append(segment)

    return parsed_objects, unparsed_segments


def sanitize_html(html):
    # Replace all weird and special characters with an empty string
    sanitized_html = html
    # sanitized_html = re.sub(r'[^\w\s.,;:!?=\[\]{}()<>\/\\\-"]', '', html)

    # Escape all double and single quotes
    sanitized_html = sanitized_html.replace('"', '\\"').replace("'", "\\'")

    return sanitized_html


def escape_json_string(s):
    """
    Escapes characters in a string to be JSON safe.

    Parameters:
    s (str): The input string to be escaped.

    Returns:
    str: The escaped string, safe for JSON encoding.
    """
    # Replace problematic backslash first
    s = s.replace("\\", "\\\\")

    # Replace the double quote
    s = s.replace('"', '\\"')

    # Escape control characters
    s = s.replace("\b", "\\b")
    s = s.replace("\f", "\\f")
    s = s.replace("\n", "\\n")
    s = s.replace("\r", "\\r")
    s = s.replace("\t", "\\t")

    # Additional problematic characters
    # Unicode control characters
    s = re.sub(r"[\x00-\x1f\x7f-\x9f]", lambda x: "\\u{:04x}".format(ord(x.group())), s)

    return s


class CustomHTML2Text(HTML2Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ignore_links = True
        self.inside_pre = False
        self.inside_code = False

    def handle_tag(self, tag, attrs, start):
        if tag == "pre":
            if start:
                self.o("```\n")
                self.inside_pre = True
            else:
                self.o("\n```")
                self.inside_pre = False
        # elif tag == 'code' and not self.inside_pre:
        #     if start:
        #         if not self.inside_pre:
        #             self.o('`')
        #         self.inside_code = True
        #     else:
        #         if not self.inside_pre:
        #             self.o('`')
        #         self.inside_code = False

        super().handle_tag(tag, attrs, start)


def get_content_of_website(
    url, html, word_count_threshold=MIN_WORD_THRESHOLD, css_selector=None
):
    try:
        if not html:
            return None
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        # Get the content within the <body> tag
        body = soup.body

        # If css_selector is provided, extract content based on the selector
        if css_selector:
            selected_elements = body.select(css_selector)
            if not selected_elements:
                raise InvalidCSSSelectorError(
                    f"Invalid CSS selector , No elements found for CSS selector: {css_selector}"
                )
            div_tag = soup.new_tag("div")
            for el in selected_elements:
                div_tag.append(el)
            body = div_tag

        links = {"internal": [], "external": []}

        # Extract all internal and external links
        for a in body.find_all("a", href=True):
            href = a["href"]
            url_base = url.split("/")[2]
            if href.startswith("http") and url_base not in href:
                links["external"].append({"href": href, "text": a.get_text()})
            else:
                links["internal"].append({"href": href, "text": a.get_text()})

        # Remove script, style, and other tags that don't carry useful content from body
        for tag in body.find_all(["script", "style", "link", "meta", "noscript"]):
            tag.decompose()

        # Remove all attributes from remaining tags in body, except for img tags
        for tag in body.find_all():
            if tag.name != "img":
                tag.attrs = {}

        # Extract all img tgas inti [{src: '', alt: ''}]
        media = {"images": [], "videos": [], "audios": []}
        for img in body.find_all("img"):
            media["images"].append(
                {"src": img.get("src"), "alt": img.get("alt"), "type": "image"}
            )

        # Extract all video tags into [{src: '', alt: ''}]
        for video in body.find_all("video"):
            media["videos"].append(
                {"src": video.get("src"), "alt": video.get("alt"), "type": "video"}
            )

        # Extract all audio tags into [{src: '', alt: ''}]
        for audio in body.find_all("audio"):
            media["audios"].append(
                {"src": audio.get("src"), "alt": audio.get("alt"), "type": "audio"}
            )

        # Replace images with their alt text or remove them if no alt text is available
        for img in body.find_all("img"):
            alt_text = img.get("alt")
            if alt_text:
                img.replace_with(soup.new_string(alt_text))
            else:
                img.decompose()

        # Create a function that replace content of all"pre" tage with its inner text
        def replace_pre_tags_with_text(node):
            for child in node.find_all("pre"):
                # set child inner html to its text
                child.string = child.get_text()
            return node

        # Replace all "pre" tags with their inner text
        body = replace_pre_tags_with_text(body)

        # Recursively remove empty elements, their parent elements, and elements with word count below threshold
        def remove_empty_and_low_word_count_elements(node, word_count_threshold):
            for child in node.contents:
                if isinstance(child, element.Tag):
                    remove_empty_and_low_word_count_elements(
                        child, word_count_threshold
                    )
                    word_count = len(child.get_text(strip=True).split())
                    if (
                        len(child.contents) == 0 and not child.get_text(strip=True)
                    ) or word_count < word_count_threshold:
                        child.decompose()
            return node

        body = remove_empty_and_low_word_count_elements(body, word_count_threshold)

        def remove_small_text_tags(
            body: Tag, word_count_threshold: int = MIN_WORD_THRESHOLD
        ):
            # We'll use a list to collect all tags that don't meet the word count requirement
            tags_to_remove = []

            # Traverse all tags in the body
            for tag in body.find_all(True):  # True here means all tags
                # Check if the tag contains text and if it's not just whitespace
                if tag.string and tag.string.strip():
                    # Split the text by spaces and count the words
                    word_count = len(tag.string.strip().split())
                    # If the word count is less than the threshold, mark the tag for removal
                    if word_count < word_count_threshold:
                        tags_to_remove.append(tag)

            # Remove all marked tags from the tree
            for tag in tags_to_remove:
                tag.decompose()  # or tag.extract() to remove and get the element

            return body

        # Remove small text tags
        body = remove_small_text_tags(body, word_count_threshold)

        def is_empty_or_whitespace(tag: Tag):
            if isinstance(tag, NavigableString):
                return not tag.strip()
            # Check if the tag itself is empty or all its children are empty/whitespace
            if not tag.contents:
                return True
            return all(is_empty_or_whitespace(child) for child in tag.contents)

        def remove_empty_tags(body: Tag):
            # Continue processing until no more changes are made
            changes = True
            while changes:
                changes = False
                # Collect all tags that are empty or contain only whitespace
                empty_tags = [
                    tag for tag in body.find_all(True) if is_empty_or_whitespace(tag)
                ]
                for tag in empty_tags:
                    # If a tag is empty, decompose it
                    tag.decompose()
                    changes = True  # Mark that a change was made

            return body

        # Remove empty tags
        body = remove_empty_tags(body)

        # Flatten nested elements with only one child of the same type
        def flatten_nested_elements(node):
            for child in node.contents:
                if isinstance(child, element.Tag):
                    flatten_nested_elements(child)
                    if (
                        len(child.contents) == 1
                        and child.contents[0].name == child.name
                    ):
                        # print('Flattening:', child.name)
                        child_content = child.contents[0]
                        child.replace_with(child_content)

            return node

        body = flatten_nested_elements(body)

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove consecutive empty newlines and replace multiple spaces with a single space
        cleaned_html = str(body).replace("\n\n", "\n").replace("  ", " ")

        # Sanitize the cleaned HTML content
        cleaned_html = sanitize_html(cleaned_html)
        # sanitized_html = escape_json_string(cleaned_html)

        # Convert cleaned HTML to Markdown
        h = html2text.HTML2Text()
        h = CustomHTML2Text()
        h.ignore_links = True
        markdown = h.handle(cleaned_html)
        markdown = markdown.replace("    ```", "```")

        # Return the Markdown content
        return {
            "markdown": markdown,
            "cleaned_html": cleaned_html,
            "success": True,
            "media": media,
            "links": links,
        }

    except Exception as e:
        print("Error processing HTML content:", str(e))
        raise InvalidCSSSelectorError(f"Invalid CSS selector: {css_selector}") from e


def extract_metadata(html):
    metadata = {}

    if not html:
        return metadata

    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.find("title")
    metadata["title"] = title_tag.string if title_tag else None

    # Meta description
    description_tag = soup.find("meta", attrs={"name": "description"})
    metadata["description"] = description_tag["content"] if description_tag else None

    # Meta keywords
    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    metadata["keywords"] = keywords_tag["content"] if keywords_tag else None

    # Meta author
    author_tag = soup.find("meta", attrs={"name": "author"})
    metadata["author"] = author_tag["content"] if author_tag else None

    # Open Graph metadata
    og_tags = soup.find_all(
        "meta", attrs={"property": lambda value: value and value.startswith("og:")}
    )
    for tag in og_tags:
        property_name = tag["property"]
        metadata[property_name] = tag["content"]

    # Twitter Card metadata
    twitter_tags = soup.find_all(
        "meta", attrs={"name": lambda value: value and value.startswith("twitter:")}
    )
    for tag in twitter_tags:
        property_name = tag["name"]
        metadata[property_name] = tag["content"]

    return metadata


def extract_xml_tags(string):
    tags = re.findall(r"<(\w+)>", string)
    return list(set(tags))


def extract_xml_data(tags, string):
    data = {}

    for tag in tags:
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, string, re.DOTALL)
        if match:
            data[tag] = match.group(1).strip()
        else:
            data[tag] = ""

    return data


# Function to perform the completion with exponential backoff
def perform_completion_with_backoff(provider, prompt_with_variables, api_token):
    from litellm import completion
    from litellm.exceptions import RateLimitError

    max_attempts = 3
    base_delay = 2  # Base delay in seconds, you can adjust this based on your needs

    for attempt in range(max_attempts):
        try:
            response = completion(
                model=provider,
                messages=[{"role": "user", "content": prompt_with_variables}],
                temperature=0.01,
                api_key=api_token,
            )
            return response  # Return the successful response
        except RateLimitError as e:
            print("Rate limit error:", str(e))

            # Check if we have exhausted our max attempts
            if attempt < max_attempts - 1:
                # Calculate the delay and wait
                delay = base_delay * (2**attempt)  # Exponential backoff formula
                print(f"Waiting for {delay} seconds before retrying...")
                time.sleep(delay)
            else:
                # Return an error response after exhausting all retries
                return [
                    {
                        "index": 0,
                        "tags": ["error"],
                        "content": ["Rate limit error. Please try again later."],
                    }
                ]


def extract_blocks(url, html, provider=DEFAULT_PROVIDER, api_token=None):
    # api_token = os.getenv('GROQ_API_KEY', None) if not api_token else api_token
    api_token = PROVIDER_MODELS.get(provider, None) if not api_token else api_token

    variable_values = {
        "URL": url,
        "HTML": escape_json_string(sanitize_html(html)),
    }

    prompt_with_variables = PROMPT_EXTRACT_BLOCKS
    for variable in variable_values:
        prompt_with_variables = prompt_with_variables.replace(
            "{" + variable + "}", variable_values[variable]
        )

    response = perform_completion_with_backoff(
        provider, prompt_with_variables, api_token
    )

    try:
        blocks = extract_xml_data(["blocks"], response.choices[0].message.content)[
            "blocks"
        ]
        blocks = json.loads(blocks)
        ## Add error: False to the blocks
        for block in blocks:
            block["error"] = False
    except Exception as e:
        print("Error extracting blocks:", str(e))
        parsed, unparsed = split_and_parse_json_objects(
            response.choices[0].message.content
        )
        blocks = parsed
        # Append all unparsed segments as onr error block and content is list of unparsed segments
        if unparsed:
            blocks.append(
                {"index": 0, "error": True, "tags": ["error"], "content": unparsed}
            )
    return blocks


def extract_blocks_batch(batch_data, provider="groq/llama3-70b-8192", api_token=None):
    api_token = os.getenv("GROQ_API_KEY", None) if not api_token else api_token
    from litellm import batch_completion

    messages = []

    for url, html in batch_data:
        variable_values = {
            "URL": url,
            "HTML": html,
        }

        prompt_with_variables = PROMPT_EXTRACT_BLOCKS
        for variable in variable_values:
            prompt_with_variables = prompt_with_variables.replace(
                "{" + variable + "}", variable_values[variable]
            )

        messages.append([{"role": "user", "content": prompt_with_variables}])

    responses = batch_completion(model=provider, messages=messages, temperature=0.01)

    all_blocks = []
    for response in responses:
        try:
            blocks = extract_xml_data(["blocks"], response.choices[0].message.content)[
                "blocks"
            ]
            blocks = json.loads(blocks)

        except Exception as e:
            print("Error extracting blocks:", str(e))
            blocks = [
                {
                    "index": 0,
                    "tags": ["error"],
                    "content": [
                        "Error extracting blocks from the HTML content. Choose another provider/model or try again."
                    ],
                    "questions": [
                        "What went wrong during the block extraction process?"
                    ],
                }
            ]
        all_blocks.append(blocks)

    return sum(all_blocks, [])


def merge_chunks_based_on_token_threshold(chunks, token_threshold):
    """
    Merges small chunks into larger ones based on the total token threshold.

    :param chunks: List of text chunks to be merged based on token count.
    :param token_threshold: Max number of tokens for each merged chunk.
    :return: List of merged text chunks.
    """
    merged_sections = []
    current_chunk = []
    total_token_so_far = 0

    for chunk in chunks:
        chunk_token_count = (
            len(chunk.split()) * 1.3
        )  # Estimate token count with a factor
        if total_token_so_far + chunk_token_count < token_threshold:
            current_chunk.append(chunk)
            total_token_so_far += chunk_token_count
        else:
            if current_chunk:
                merged_sections.append("\n\n".join(current_chunk))
            current_chunk = [chunk]
            total_token_so_far = chunk_token_count

    # Add the last chunk if it exists
    if current_chunk:
        merged_sections.append("\n\n".join(current_chunk))

    return merged_sections


def process_sections(url: str, sections: list, provider: str, api_token: str) -> list:
    extracted_content = []
    if provider.startswith("groq/"):
        # Sequential processing with a delay
        for section in sections:
            extracted_content.extend(extract_blocks(url, section, provider, api_token))
            time.sleep(0.5)  # 500 ms delay between each processing
    else:
        # Parallel processing using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(extract_blocks, url, section, provider, api_token)
                for section in sections
            ]
            for future in as_completed(futures):
                extracted_content.extend(future.result())

    return extracted_content


def wrap_text(draw, text, font, max_width):
    # Wrap the text to fit within the specified width
    lines = []
    words = text.split()
    while words:
        line = ""
        while (
            words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width
        ):
            line += words.pop(0) + " "
        lines.append(line)
    return "\n".join(lines)


from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter, status, Form
import importlib


def import_strategy(module_name: str, class_name: str, *args, **kwargs):
    try:
        module = importlib.import_module(module_name)
        strategy_class = getattr(module, class_name)
        return strategy_class(*args, **kwargs)
    except ImportError:
        print("ImportError: Module not found.")
        raise HTTPException(status_code=400, detail=f"Module {module_name} not found.")
    except AttributeError:
        print("AttributeError: Class not found.")
        raise HTTPException(
            status_code=400, detail=f"Class {class_name} not found in {module_name}."
        )
