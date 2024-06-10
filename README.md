# OmniParse
API to Convert anything to markdown

> [!IMPORTANT]
>
> OmniParse is a comprehensive parsing tool designed to convert any document, media, or website into markdown. Whether you're dealing with documents, tables, images, videos, audio files, or web pages, OmniParse ensures your data is parsed and cleaned to a high standard before it is passed to any downstream LLM use case, such as advanced RAG.

## Features

✅ Supports 15+ file types \
✅ Convert Documents, Multimedia, Web pages to high-quality structured markdown \
✅ Table Extraction, Image Extraction/Captioning, Audio Transcription, Web page Crawling \
✅ Easily Deployable using Docker and Skypilot \
✅ CPU/GPU compatible \
✅ Batch processing for handling multiple files at once \
✅ Comprehensive logging and error handling for robust performance \

## Supported File Types

| Type       | Supported Extensions                    |
|------------|-----------------------------------------|
| Documents  | .doc, .docx, .epub, .odt, .pdf, .ppt, .pptx |

<!-- 
| Type      | Supported Extensions                                |
|-----------|-----------------------------------------------------|
| Plaintext | .eml, .html, .md, .msg, .rst, .rtf, .txt, .xml      |
| Documents | .doc, .docx, .epub, .odt, .pdf, .ppt, .pptx         |
| Table     | .csv, .xlsx                                         |
| Images    | .png, .jpg, .jpeg, .tiff, .bmp, .heic               |
| Video     | .mp4, .mkv, .avi, .mov                              |
| Audio     | .mp3, .wav, .aac                                    |
| Web       | dynamic webpages, http://<anything>.com             |
| Crawl     | dynamic webpages, http://<anything>.com            |
-->

## Installation

To install OmniParse, you can use `pip`:

```bash
git clone https://github.com/adithya-s-k/omniparse
cd omniparse
```

Create a Virtual Environment:

```bash
conda create omniparse-venv python=3.10
conda activate omniparse-venv
```

Install Dependencies:

```bash
poetry install
# or
pip install -e .
```

## Usage

Run the Server:

```bash
python server.py
```

Install the client:

```bash
pip install omniparse_client
```

Example usage:

```python
from omniparse_client import OmniParse

# Initialize the parser
parser = OmniParse(
    base_url="http://localhost:8000" 
    api_key="op-...", # get the api key from dev.omniparse.com
    verbose=True,
    language="en" )

# Parse a document
document = parser.load_data('path/to/document.pdf')

# Convert to markdown
parser.save_to_markdown(document)
```



## License

OmniParse is licensed under the Apache License. See `LICENSE` for more information.

## Acknowledgement

[Surya-OCR](https://github.com/VikParuchuri/surya),[Texify](https://github.com/VikParuchuri/texify) - Big thanks to VikParuchuri for creating awesome open-source OCR models which have been extensively used in this project

## Contact

For any inquiries, please contact us at adithyaskolavi@gmail.com