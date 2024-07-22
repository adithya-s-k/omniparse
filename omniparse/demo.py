"""
Title: OmniPrase
Author: Adithya S Kolavi
Date: 2024-07-02
"""

import os
import base64
import mimetypes
import httpx
from PIL import Image
from io import BytesIO
import gradio as gr
# from omniparse.documents import parse_pdf

single_task_list = ["Caption", "Detailed Caption", "More Detailed Caption", "OCR", "OCR with Region"]
# single_task_list = [
#     'Caption', 'Detailed Caption', 'More Detailed Caption',
#     'OCR', 'OCR with Region',
#     'Object Detection',
#     'Dense Region Caption', 'Region Proposal', 'Caption to Phrase Grounding',
#     'Referring Expression Segmentation', 'Region to Segmentation',
#     'Open Vocabulary Detection', 'Region to Category', 'Region to Description',
# ]

header_markdown = """

#

## Problem Statement
It's challenging to process data as it comes in different shapes and sizes. OmniParse aims to be an ingestion/parsing platform where you can ingest any type of data, such as documents, images, audio, video, and web content, and get the most structured and actionable output that is GenAI (LLM) friendly.

<table style="width:100%">
  <thead>
    <tr>
      <th>Features</th>
      <th>Upcoming Features</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>✅ Completely local, no external APIs</td>
      <td>🔜 Batch processing files</td>
    </tr>
    <tr>
      <td>✅ Semantic Chunking</td>
      <td>🔜 Web crawl and search</td>
    </tr>
    <tr>
      <td>✅ Supports ~20 file types</td>
      <td>🔜 Structured output extraction</td>
    </tr>
    <tr>
      <td>✅ Convert documents, multimedia, and web pages to high-quality structured markdown</td>
      <td>🔜 LlamaIndex, Langchain integration</td>
    </tr>
    <tr>
      <td>✅ Table extraction, image extraction/captioning, audio/video transcription, web page crawling</td>
      <td>🔜 Hosted ultra scalable API as a service</td>
    </tr>
    <tr>
      <td>✅ Easily deployable using Docker and Skypilot</td>
      <td>🔜 LLM formatting</td>
    </tr>
  </tbody>
</table>

## Installation
> Note: The server only works on Linux-based systems. This is due to certain dependencies and system-specific configurations that are not compatible with Windows or macOS.Please use Docker image provided below to run omniparse

```bash
git clone https://github.com/adithya-s-k/omniparse
cd omniparse
```

---

Create a Virtual Environment:

```bash
conda create --name omniparse-venv python=3.10
conda activate omniparse-venv
```

Install Dependencies:

```bash
poetry install
# or
pip install -e .
```

### 🛳️ Docker

To use OmniParse with Docker, execute the following commands:

1. Pull the OmniParse API Docker image from Docker Hub:
2. Run the Docker container, exposing port 8000:
 👉🏼[Docker Image](https://hub.docker.com/r/savatar101/omniparse)
```bash
docker pull savatar101/omniparse:0.1
# if you are running on a gpu 
docker run --gpus all -p 8000:8000 savatar101/omniparse:0.1
# else
docker run -p 8000:8000 savatar101/omniparse:0.1
```

Alternatively, if you prefer to build the Docker image locally:
Then, run the Docker container as follows:

```bash
docker build -t omniparse .
# if you are running on a gpu
docker run --gpus all -p 8000:8000 omniparse
# else
docker run -p 8000:8000 omniparse

```



## Usage

Run the Server:

```bash
python server.py --host 0.0.0.0 --port 8000 --documents --media --web
```
&nbsp;  
- `--documents`: Load in all the models that help you parse and ingest documents (Surya OCR series of models and Florence-2).
- `--media`: Load in Whisper model to transcribe audio and video files.
- `--web`: Set up selenium crawler.

## Supported Data Types

| Type         | Supported Extensions                                |
|--------------|-----------------------------------------------------|
| Documents    | .doc, .docx, .pdf, .ppt, .pptx                      |
| Images       | .png, .jpg, .jpeg, .tiff, .bmp, .heic               |
| Media(Video) | .mp4, .mkv, .avi, .mov                              |
| Media(Audio) | .mp3, .wav, .aac                                    |
| Web          | dynamic webpages, http://<anything>.com             |

### Support
If you've found this project valuable, your ⭐ star on [Github](https://github.com/adithya-s-k/omniparse) would mean a lot!

<p align="left">
  <a href="https://github.com/adithya-s-k/omniparse">
    <img src="https://api.star-history.com/svg?repos=adithya-s-k/omniparse&type=Date" alt="Star History Chart" width="500px">
  </a>
</p>

### Contact
Encountering difficulties or errors? Please raise an issue on [GitHub](https://github.com/adithya-s-k/omniparse/issues).
"""


def decode_base64_to_pil(base64_str):
    return Image.open(BytesIO(base64.b64decode(base64_str)))


parse_document_docs = {
    "curl": """curl -X POST -F "file=@/path/to/document" http://localhost:8000/parse_document""",
    "python": """
    coming soon⌛
    """,
    "javascript": """
    coming soon⌛
    """,
}

TIMEOUT = 300  


def parse_document(input_file_path, parameters, request: gr.Request):
    # Validate file extension
    allowed_extensions = [".pdf", ".ppt", ".pptx", ".doc", ".docx"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")
    try:
        host_url = request.headers.get("host")

        post_url = f"http://{host_url}/parse_document"
        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found

        with open(input_file_path, "rb") as f:
            files = {"file": (input_file_path, f, mime_type)}
            response = httpx.post(post_url, files=files, headers={"accept": "application/json"}, timeout=TIMEOUT)

        document_response = response.json()

        images = document_response.get("images", [])

        # Decode each base64-encoded image to a PIL image
        pil_images = [decode_base64_to_pil(image_dict["image"]) for image_dict in images]

        return (
            str(document_response["text"]),
            gr.Gallery(value=pil_images, visible=True),
            str(document_response["text"]),
            gr.JSON(value=document_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")


process_image_docs = {
    "curl": """curl -X POST -F "image=@/path/to/image.jpg" -F "task=Caption" http://localhost:8000/parse_image/process_image""",
    "python": """
    coming soon⌛
    """,
    "javascript": """
    coming soon⌛
    """,
}


def process_image(input_file_path, parameters, request: gr.Request):
    print(parameters)
    # Validate file extension
    allowed_image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_image_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")

    try:
        host_url = request.headers.get("host")

        # URL for image parsing
        post_url = f"http://{host_url}/parse_image/process_image"

        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found
        with open(input_file_path, "rb") as f:
            # Prepare the files payload
            files = {"image": (input_file_path, f, mime_type)}

            # Prepare the data payload
            data = {"task": parameters}

            # Send the POST request
            response = httpx.post(
                post_url, files=files, data=data, headers={"accept": "application/json"}, timeout=TIMEOUT
            )

        image_process_response = response.json()

        images = image_process_response.get("images", [])
        # Decode each base64-encoded image to a PIL image
        pil_images = [decode_base64_to_pil(image_dict["image"]) for image_dict in images]

        # Decode the image if present in the response
        # images = document_response.get('image', {})
        # pil_images = [decode_base64_to_pil(base64_str) for base64_str in images.values()]

        return (
            gr.update(value=image_process_response["text"]),
            gr.Gallery(value=pil_images, visible=(len(images) != 0)),
            gr.JSON(value=image_process_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")


parse_image_docs = {
    "curl": """curl -X POST -F "file=@/path/to/image.jpg" http://localhost:8000/parse_image/image""",
    "python": """
    coming soon⌛
    """,
    "javascript": """
    coming soon⌛
    """,
}


def parse_image(input_file_path, parameters, request: gr.Request):
    # Validate file extension
    allowed_image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_image_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")

    try:
        host_url = request.headers.get("host")

        # URL for image parsing
        post_url = f"http://{host_url}/parse_image/image"

        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found

        with open(input_file_path, "rb") as f:
            files = {"file": (input_file_path, f, mime_type)}
            response = httpx.post(post_url, files=files, headers={"accept": "application/json"}, timeout=TIMEOUT)

        document_response = response.json()

        # Decode the image if present in the response
        images = document_response.get("images", [])

        # Decode each base64-encoded image to a PIL image
        pil_images = [decode_base64_to_pil(image_dict["image"]) for image_dict in images]

        return (
            gr.update(value=document_response["text"]),
            gr.Gallery(value=pil_images, visible=True),
            gr.update(value=document_response["text"]),
            gr.update(value=document_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")


parse_media_docs = {
    "curl": """
    curl -X POST -F "file=@/path/to/video.mp4" http://localhost:8000/parse_media/video
    
    curl -X POST -F "file=@/path/to/audio.mp3" http://localhost:8000/parse_media/audio""",
    "python": """
    coming soon⌛
    """,
    "javascript": """
    coming soon⌛
    """,
}


def parse_media(input_file_path, parameters, request: gr.Request):
    allowed_audio_extensions = [".mp3", ".wav", ".aac"]
    allowed_video_extensions = [".mp4", ".mkv", ".mov", ".avi"]
    allowed_extensions = allowed_audio_extensions + allowed_video_extensions
    file_extension = os.path.splitext(input_file_path)[1].strip().lower()
    if file_extension not in allowed_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")

    try:
        host_url = request.headers.get("host")

        # Determine the correct URL based on the file type
        if file_extension in allowed_audio_extensions:
            post_url = f"http://{host_url}/parse_media/audio"
        else:
            post_url = f"http://{host_url}/parse_media/video"

        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found

        with open(input_file_path, "rb") as f:
            files = {"file": (input_file_path, f, mime_type)}
            response = httpx.post(post_url, files=files, headers={"accept": "application/json"}, timeout=TIMEOUT)

        media_response = response.json()
        # print(media_response["text"])
        # # Handle images if present in the response
        # images = document_response.get('images', {})
        # pil_images = [decode_base64_to_pil(base64_str) for base64_str in images.values()]

        return (
            gr.update(value=str(media_response["text"])),
            gr.update(visible=False),
            gr.update(value=str(media_response["text"])),
            gr.update(value=media_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")


parse_website_docs = {
    "curl": """curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com"}' http://localhost:8000/parse_website""",
    "python": """
    coming soon⌛
    """,
    "javascript": """
    coming soon⌛
    """,
}


def parse_website(url, request: gr.Request):
    try:
        host_url = request.headers.get("host")

        # Make a POST request to the external URL
        post_url = f"http://{host_url}/parse_website/parse?url={url}"
        post_response = httpx.post(post_url, headers={"accept": "application/json"}, timeout=TIMEOUT)

        # Validate response
        post_response.raise_for_status()
        website_response = post_response.json()

        # Extract necessary data from the response
        result = website_response.get("metadata", {})
        markdown = website_response.get("text", "")
        html = result.get("cleaned_html", "")
        base64_image = result.get("screenshot", "")

        screenshot = [decode_base64_to_pil(base64_image)] if base64_image else []

        images = website_response.get("images", [])

        # Decode each base64-encoded image to a PIL image
        pil_images = [decode_base64_to_pil(image_dict["image"]) for image_dict in images]

        return (
            gr.update(value=markdown, visible=True),
            gr.update(value=html, visible=True),
            gr.update(value=pil_images, visible=bool(screenshot)),
            gr.JSON(value=website_response, visible=True),
        )

    except httpx.RequestError as e:
        raise gr.Error(f"HTTP error occurred: {e}")


demo_ui = gr.Blocks(theme=gr.themes.Monochrome(radius_size=gr.themes.sizes.radius_none))

with demo_ui:
    gr.Markdown(
        "<img src='https://raw.githubusercontent.com/adithya-s-k/omniparse/main/docs/assets/omniparse_logo.png' width='500px'>"
    )
    gr.Markdown(
        "📄 [Documentation](https://docs.cognitivelab.in/) | ✅ [Follow](https://x.com/adithya_s_k) | 🐈‍⬛ [Github](https://github.com/adithya-s-k/omniparse) | ⭐ [Give a Star](https://github.com/adithya-s-k/omniparse)"
    )
    with gr.Tabs():
        with gr.TabItem("Documents"):
            with gr.Row():
                with gr.Column(scale=80):
                    document_file = gr.File(
                        label="Upload Document",
                        type="filepath",
                        file_count="single",
                        interactive=True,
                        file_types=[".pdf", ".ppt", ".doc", ".pptx", ".docx"],
                    )
                    with gr.Accordion("Parameters", visible=True):
                        document_parameter = gr.Dropdown(
                            ["Fixed Size Chunking", "Regex Chunking", "Semantic Chunking"], label="Chunking Stratergy"
                        )
                        if document_parameter == "Fixed Size Chunking":
                            document_chunk_size = gr.Number(minimum=250, maximum=10000, step=100, show_label=False)
                            document_overlap_size = gr.Number(minimum=250, maximum=1000, step=100, show_label=False)
                    document_button = gr.Button("Parse Document")
                with gr.Column(scale=200):
                    with gr.Accordion("Markdown"):
                        document_markdown = gr.Markdown()
                    with gr.Accordion("Extracted Images"):
                        document_images = gr.Gallery(visible=False)
                    with gr.Accordion("Chunks", visible=False):
                        document_chunks = gr.Markdown()
            with gr.Accordion("JSON Output"):
                document_json = gr.JSON(label="Output JSON", visible=False)
            with gr.Accordion("Use API", open=True):
                gr.Code(language="shell", value=parse_document_docs["curl"], lines=1, label="Curl")
                gr.Code(language="python", value="Coming Soon⌛", lines=1, label="python")
                gr.Code(language="javascript", value="Coming Soon⌛", lines=1, label="Javascript")
        with gr.TabItem("Images"):
            with gr.Tabs():
                with gr.TabItem("Process"):
                    with gr.Row():
                        with gr.Column(scale=80):
                            image_process_file = gr.File(
                                label="Upload Image",
                                type="filepath",
                                file_count="single",
                                interactive=True,
                                file_types=[".jpg", ".jpeg", ".png"],
                            )
                            image_process_parameter = gr.Dropdown(
                                choices=single_task_list, label="Task Prompt", value="Caption", interactive=True
                            )
                            image_process_button = gr.Button("Process Image")
                        with gr.Column(scale=200):
                            image_process_output_text = gr.Textbox(label="Output Text")
                            image_process_output_image = gr.Gallery(label="Output Image ⌛", interactive=False)
                    with gr.Accordion("JSON Output"):
                        image_process_json = gr.JSON(label="Output JSON", visible=False)
                    with gr.Accordion("Use API", open=True):
                        gr.Code(language="shell", value=process_image_docs["curl"], lines=1, label="Curl")
                        gr.Code(language="python", value="Coming Soon⌛", lines=1, label="python")
                        gr.Code(language="javascript", value="Coming Soon⌛", lines=1, label="Javascript")
                with gr.TabItem("Parse"):
                    with gr.Row():
                        with gr.Column(scale=80):
                            image_parse_file = gr.File(
                                label="Upload Image", type="filepath", file_count="single", interactive=True
                            )
                            with gr.Accordion("Parameters", visible=False):
                                image_parse_parameter = gr.CheckboxGroup(["chunk document"], show_label=False)
                            image_parse_button = gr.Button("Parse Image")
                        with gr.Column(scale=200):
                            with gr.Accordion("Markdown"):
                                image_parse_markdown = gr.Markdown()
                            with gr.Accordion("Extracted Images"):
                                image_parse_images = gr.Gallery(visible=False)
                            with gr.Accordion("Chunks", visible=False):
                                image_parse_chunks = gr.Markdown()
                    with gr.Accordion("JSON Output"):
                        image_parse_json = gr.JSON(label="Output JSON", visible=False)
                    with gr.Accordion("Use API", open=True):
                        gr.Code(language="shell", value=parse_image_docs["curl"], lines=1, label="Curl")
                        gr.Code(language="python", value="Coming Soon⌛", lines=1, label="python")
                        gr.Code(language="javascript", value="Coming Soon⌛", lines=1, label="Javascript")
        with gr.TabItem("Media"):
            with gr.Row():
                with gr.Column(scale=80):
                    media_file = gr.File(
                        label="Upload Media",
                        type="filepath",
                        file_count="single",
                        interactive=True,
                        file_types=[".mp4", ".mkv", ".mov", ".avi", ".mp3", ".wav", ".aac"],
                    )
                    with gr.Accordion("Parameters", visible=False):
                        media_parameter = gr.CheckboxGroup(["chunk document"], show_label=False)
                    media_button = gr.Button("Parse Media")
                with gr.Column(scale=200):
                    with gr.Accordion("Markdown"):
                        media_markdown = gr.Markdown("")
                        media_images = gr.Gallery(visible=False)
                    with gr.Accordion("Chunks", visible=False):
                        media_chunks = gr.Markdown("")
            with gr.Accordion("JSON Output"):
                media_json = gr.JSON(label="Output JSON", visible=False)
            with gr.Accordion("Use API", open=True):
                gr.Code(language="shell", value=parse_media_docs["curl"], lines=1, label="Curl")
                gr.Code(language="python", value="Coming Soon⌛", lines=1, label="python")
                gr.Code(language="javascript", value="Coming Soon⌛", lines=1, label="Javascript")
        with gr.TabItem("Web"):
            with gr.Tabs():
                with gr.TabItem("Parse"):
                    with gr.Row():
                        with gr.Column(scale=90):
                            crawl_url = gr.Textbox(
                                interactive=True, placeholder="https://adithyask.com ....", show_label=False
                            )
                        with gr.Column(scale=10):
                            crawl_button = gr.Button("➡️ Parse Website")
                    with gr.Accordion("Markdown"):
                        crawl_markdown = gr.Markdown()
                    with gr.Accordion("HTML"):
                        crawl_html = gr.HTML()
                    with gr.Accordion("Screen Shots"):
                        crawl_image = gr.Gallery()
                    with gr.Accordion("JSON Output"):
                        crawl_json = gr.JSON(label="Output JSON", visible=False)
                    with gr.Accordion("Use API", open=True):
                        gr.Code(language="shell", value=parse_website_docs["curl"], lines=1, label="Curl")
                        gr.Code(language="python", value="Coming Soon⌛", lines=1, label="python")
                        gr.Code(language="javascript", value="Coming Soon⌛", lines=1, label="Javascript")
                with gr.TabItem("Crawl ⌛", interactive=False):
                    gr.Markdown("Enter query to search:")
                    gr.Textbox(label="Search Query", interactive=False, value="Coming Soon ⌛")
                with gr.TabItem("Search ⌛", interactive=False):
                    gr.Markdown("Enter query to search:")
                    gr.Textbox(label="Search Query", interactive=False, value="Coming Soon ⌛")
        gr.Markdown(header_markdown)

    document_button.click(
        fn=parse_document,
        inputs=[document_file, document_parameter],
        outputs=[document_markdown, document_images, document_chunks, document_json],
    )
    image_parse_button.click(
        fn=parse_image,
        inputs=[image_parse_file, image_parse_parameter],
        outputs=[image_parse_markdown, image_parse_images, image_parse_chunks, image_parse_json],
    )
    image_process_button.click(
        fn=process_image,
        inputs=[image_process_file, image_process_parameter],
        outputs=[image_process_output_text, image_process_output_image, image_process_json],
    )
    media_button.click(
        fn=parse_media,
        inputs=[media_file, media_parameter],
        outputs=[media_markdown, media_images, media_chunks, media_json],
    )
    crawl_button.click(
        fn=parse_website, inputs=[crawl_url], outputs=[crawl_markdown, crawl_html, crawl_image, crawl_json]
    )


# # local processing
# def process_document(input_file, parameters):
#     print(parameters)
#     response = parse_pdf(input_file , model_state)
#     images = response["images"]
#     pil_images = [decode_base64_to_pil(base64_str) for base64_str in images.values()]
#     return str(response["markdown"]) , gr.Gallery(value=pil_images , visible=True)
