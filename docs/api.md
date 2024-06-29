---
description: >-
  detailed description of the API endpoints, including their functionality and
  how to use them via curl requests.
---

# API

## Documents

**Parse Any Document**

Endpoint: `/parse_document` Method: POST

Parses PDF, PowerPoint, or Word documents.

Curl command:

```
curl -X POST -F "file=@/path/to/document" http://localhost:8000/parse_document
```

**Parse PDF**

Endpoint: `/parse_document/pdf` Method: POST

Parses PDF documents.

Curl command:

```
curl -X POST -F "file=@/path/to/document.pdf" http://localhost:8000/parse_document/pdf
```

**Parse PowerPoint**

Endpoint: `/parse_document/ppt` Method: POST

Parses PowerPoint presentations.

Curl command:

```
curl -X POST -F "file=@/path/to/presentation.ppt" http://localhost:8000/parse_document/ppt
```

**Parse Word Document**

Endpoint: `/parse_document/docs` Method: POST

Parses Word documents.

Curl command:

```
curl -X POST -F "file=@/path/to/document.docx" http://localhost:8000/parse_document/docs
```

## Image

**Parse Image**

Endpoint: `/parse_media/image` Method: POST

Parses image files (PNG, JPEG, JPG, TIFF, WEBP).

Curl command:

```
curl -X POST -F "file=@/path/to/image.jpg" http://localhost:8000/parse_image/image
```

**Process Image**

Endpoint: `/parse_media/process_image` Method: POST

Processes an image with a specific task.

Possible task inputs: `OCR | OCR with Region | Caption | Detailed Caption | More Detailed Caption | Object Detection | Dense Region Caption | Region Proposal`

Curl command:

```
curl -X POST -F "image=@/path/to/image.jpg" -F "task=Caption" http://localhost:8000/parse_image/process_image
```

Arguments:

* `image`: The image file
* `task`: The processing task (e.g., Caption, Object Detection)
* `prompt`: Optional prompt for certain tasks

## Media

**Parse Video**

Endpoint: `/parse_media/video` Method: POST

Parses video files (MP4, AVI, MOV, MKV).

Curl command:

```
curl -X POST -F "file=@/path/to/video.mp4" http://localhost:8000/parse_media/video
```

**Parse Audio**

Endpoint: `/parse_media/audio` Method: POST

Parses audio files (MP3, WAV, FLAC).

Curl command:

```
curl -X POST -F "file=@/path/to/audio.mp3" http://localhost:8000/parse_media/audio
```

## Website

**Parse Website**

Endpoint: `/parse_website` Method: POST

Parses a website given its URL.

Curl command:

```
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com"}' http://localhost:8000/parse_website
```

Arguments:

* `url`: The URL of the website to parse
