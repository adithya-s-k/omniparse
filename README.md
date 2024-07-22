# OmniParse

![OmniParse](https://raw.githubusercontent.com/adithya-s-k/omniparse/main/docs/assets/hero_image.png)
[![GitHub Stars](https://img.shields.io/github/stars/adithya-s-k/omniparse?style=social)](https://github.com/adithya-s-k/omniparse/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/adithya-s-k/omniparse?style=social)](https://github.com/adithya-s-k/omniparse/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/adithya-s-k/omniparse)](https://github.com/adithya-s-k/omniparse/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/adithya-s-k/omniparse)](https://github.com/adithya-s-k/omniparse/pulls)
[![License](https://img.shields.io/github/license/adithya-s-k/omniparse)](https://github.com/adithya-s-k/omniparse/blob/main/LICENSE)


> [!IMPORTANT]
>
>OmniParse is a platform that ingests and parses any unstructured data into structured, actionable data optimized for GenAI (LLM) applications. Whether you are working with documents, tables, images, videos, audio files, or web pages, OmniParse prepares your data to be clean, structured, and ready for AI applications such as RAG, fine-tuning, and more

## Try it out
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adithya-s-k/omniparse/blob/main/examples/OmniParse_GoogleColab.ipynb)

## Intro
https://github.com/adithya-s-k/omniparse/assets/27956426/457d8b5b-9573-44da-8bcf-616000651a13

## Features
✅ Completely local, no external APIs  \
✅ Fits in a T4 GPU \
✅ Supports ~20 file types  \
✅ Convert documents, multimedia, and web pages to high-quality structured markdown  \
✅ Table extraction, image extraction/captioning, audio/video transcription, web page crawling  \
✅ Easily deployable using Docker and Skypilot  \
✅ Colab friendly  \
✅ Interative UI powered by Gradio  

### Why OmniParse ?
It's challenging to process data as it comes in different shapes and sizes. OmniParse aims to be an ingestion/parsing platform where you can ingest any type of data, such as documents, images, audio, video, and web content, and get the most structured and actionable output that is GenAI (LLM) friendly.

## Installation
> [!IMPORTANT] 
> The server only works on Linux-based systems. This is due to certain dependencies and system-specific configurations that are not compatible with Windows or macOS.

```bash
git clone https://github.com/adithya-s-k/omniparse
cd omniparse
```

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
# or
pip install -r pyproject.toml
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

- `--documents`: Load in all the models that help you parse and ingest documents (Surya OCR series of models and Florence-2).
- `--media`: Load in Whisper model to transcribe audio and video files.
- `--web`: Set up selenium crawler.

Download Models:
If you want to download the models before starting the server

```bash
python download.py --documents --media --web
```

- `--documents`: Load in all the models that help you parse and ingest documents (Surya OCR series of models and Florence-2).
- `--media`: Load in Whisper model to transcribe audio and video files.
- `--web`: Set up selenium crawler.

## Supported Data Types

| Type      | Supported Extensions                                |
|-----------|-----------------------------------------------------|
| Documents | .doc, .docx, .pdf, .ppt, .pptx                      |
| Images    | .png, .jpg, .jpeg, .tiff, .bmp, .heic               |
| Video     | .mp4, .mkv, .avi, .mov                              |
| Audio     | .mp3, .wav, .aac                                    |
| Web       | dynamic webpages, http://<anything>.com             |


<details>
<summary><h2>API Endpoints</h></summary>

> Client library compatible with Langchain, llamaindex, and haystack integrations coming soon.

- [API Endpoints](#api-endpoints)
  - [Document Parsing](#document-parsing)
    - [Parse Any Document](#parse-any-document)
    - [Parse PDF](#parse-pdf)
    - [Parse PowerPoint](#parse-powerpoint)
    - [Parse Word Document](#parse-word-document)
  - [Media Parsing](#media-parsing)
    - [Parse Any Media](#parse-any-media)
    - [Parse Image](#parse-image)
    - [Process Image](#process-image)
    - [Parse Video](#parse-video)
    - [Parse Audio](#parse-audio)
  - [Website Parsing](#website-parsing)
    - [Parse Website](#parse-website)

### Document Parsing

#### Parse Any Document

Endpoint: `/parse_document`
Method: POST

Parses PDF, PowerPoint, or Word documents.

Curl command:
```
curl -X POST -F "file=@/path/to/document" http://localhost:8000/parse_document
```

#### Parse PDF

Endpoint: `/parse_document/pdf`
Method: POST

Parses PDF documents.

Curl command:
```
curl -X POST -F "file=@/path/to/document.pdf" http://localhost:8000/parse_document/pdf
```

#### Parse PowerPoint

Endpoint: `/parse_document/ppt`
Method: POST

Parses PowerPoint presentations.

Curl command:
```
curl -X POST -F "file=@/path/to/presentation.ppt" http://localhost:8000/parse_document/ppt
```

#### Parse Word Document

Endpoint: `/parse_document/docs`
Method: POST

Parses Word documents.

Curl command:
```
curl -X POST -F "file=@/path/to/document.docx" http://localhost:8000/parse_document/docs
```

### Media Parsing

<!-- #### Parse Any Media

Endpoint: `/parse_media`
Method: POST

Parses images, videos, or audio files.

Curl command:
```
curl -X POST -F "file=@/path/to/media_file" http://localhost:8000/parse_media
``` -->

#### Parse Image

Endpoint: `/parse_image/image`
Method: POST

Parses image files (PNG, JPEG, JPG, TIFF, WEBP).

Curl command:
```
curl -X POST -F "file=@/path/to/image.jpg" http://localhost:8000/parse_media/image
```

#### Process Image

Endpoint: `/parse_image/process_image`
Method: POST

Processes an image with a specific task.

Possible task inputs:
`OCR | OCR with Region | Caption | Detailed Caption | More Detailed Caption | Object Detection | Dense Region Caption | Region Proposal`

Curl command:
```
curl -X POST -F "image=@/path/to/image.jpg" -F "task=Caption" -F "prompt=Optional prompt" http://localhost:8000/parse_media/process_image
```

Arguments:
- `image`: The image file
- `task`: The processing task (e.g., Caption, Object Detection)
- `prompt`: Optional prompt for certain tasks

#### Parse Video

Endpoint: `/parse_media/video`
Method: POST

Parses video files (MP4, AVI, MOV, MKV).

Curl command:
```
curl -X POST -F "file=@/path/to/video.mp4" http://localhost:8000/parse_media/video
```

#### Parse Audio

Endpoint: `/parse_media/audio`
Method: POST

Parses audio files (MP3, WAV, FLAC).

Curl command:
```
curl -X POST -F "file=@/path/to/audio.mp3" http://localhost:8000/parse_media/audio
```

### Website Parsing

#### Parse Website

Endpoint: `/parse_website/parse`
Method: POST

Parses a website given its URL.

Curl command:
```
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com"}' http://localhost:8000/parse_website
```
Arguments:
- `url`: The URL of the website to parse

</details>


## Coming Soon/ RoadMap
🦙 LlamaIndex | Langchain | Haystack integrations coming soon
📚 Batch processing data
⭐ Dynamic chunking and structured data extraction based on specified Schema  
🛠️ One magic API: just feed in your file prompt what you want, and we will take care of the rest  
🔧 Dynamic model selection and support for external APIs  
📄 Batch processing for handling multiple files at once  
📦 New open-source model to replace Surya OCR and Marker  

**Final goal**: replace all the different models currently being used with a single MultiModel Model to parse any type of data and get the data you need.


## Limitations
There is a need for a GPU with 8~10 GB minimum VRAM as we are using deep learning models.
\

Document Parsing Limitations
\
- [Marker](https://github.com/VikParuchuri/marker) which is the underlying PDF parser will not convert 100% of equations to LaTeX because it has to detect and then convert them.
- It is good at parsing english but might struggle for languages such as Chinese
- Tables are not always formatted 100% correctly; text can be in the wrong column.
- Whitespace and indentations are not always respected.
- Not all lines/spans will be joined properly.
- This works best on digital PDFs that won't require a lot of OCR. It's optimized for speed, and limited OCR is used to fix errors.
- To fit all the models in the GPU, we are using the smallest variants, which might not offer the best-in-class performance.

## License
OmniParse is licensed under the GPL-3.0 license. See `LICENSE` for more information.
The project uses Marker under the hood, which has a commercial license that needs to be followed. Here are the details:

### Commercial Usage
Marker and Surya OCR Models are designed to be as widely accessible as possible while still funding development and training costs. Research and personal usage are always allowed, but there are some restrictions on commercial usage.
The weights for the models are licensed under cc-by-nc-sa-4.0. However, this restriction is waived for any organization with less than $5M USD in gross revenue in the most recent 12-month period AND less than $5M in lifetime VC/angel funding raised. To remove the GPL license requirements (dual-license) and/or use the weights commercially over the revenue limit, check out the options provided.
Please refer to [Marker](https://github.com/VikParuchuri/marker) for more Information about the License of the Model weights

## Acknowledgements

This project builds upon the remarkable [Marker](https://github.com/VikParuchuri/marker) project created by [Vik Paruchuri](https://twitter.com/VikParuchuri). We express our gratitude for the inspiration and foundation provided by this project. Special thanks to [Surya-OCR](https://github.com/VikParuchuri/surya) and [Texify](https://github.com/VikParuchuri/texify) for the OCR models extensively used in this project, and to [Crawl4AI](https://github.com/unclecode/crawl4ai) for their contributions.

Models being used:
- Surya OCR, Detect, Layout, Order, and Texify
- Florence-2 base
- Whisper Small

Thank you to the authors for their contributions to these models.

---

## Contact
<p align="center">
  <a href="https://adithyask.com">
    <img src="https://api.star-history.com/svg?repos=adithya-s-k/omniparse&type=Date" alt="Star History Chart">
  </a>
</p>
For any inquiries, please contact us at adithyaskolavi@gmail.com


<!-- 
Install the client:

```bash
pip install omniparse_client
```

Example usage:

```python
from omniparse_client import OmniParse

# Initialize the parser
parser = OmniParse(
    base_url="http://localhost:8000",
    api_key="op-...",  # get the API key from dev.omniparse.com
    verbose=True,
    language="en"
)

# Parse a document
document = parser.load_data('path/to/document.pdf')

# Convert to markdown
parser.save_to_markdown(document)
```
 -->
