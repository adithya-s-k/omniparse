---
description: >-
  detailed description of the API endpoints, including their functionality and
  how to use them via curl requests.
---

# API

***

## **Document Parsing Endpoints**

These endpoints are used to parse various document formats, such as PDF, PPT, DOC, and DOCX.

### **Parse PDF**

* **Endpoint:** `/parse_document/pdf`
* **Method:** `POST`
* **Description:** Parses a PDF file and extracts text, images, and metadata.
* **Parameters:**
  * `file`: PDF file to be uploaded.
* **Response:** JSON containing parsed markdown text, metadata, and images.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_document/pdf" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.pdf"
```

### **Parse PPT**

* **Endpoint:** `/parse_document/ppt`
* **Method:** `POST`
* **Description:** Parses a PPT file by converting it to PDF, then extracts text, images, and metadata.
* **Parameters:**
  * `file`: PPT file to be uploaded.
* **Response:** JSON containing parsed markdown text, metadata, and images.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_document/ppt" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.ppt"
```

### **Parse DOC**

* **Endpoint:** `/parse_document/docs`
* **Method:** `POST`
* **Description:** Parses a DOC or DOCX file by converting it to PDF, then extracts text, images, and metadata.
* **Parameters:**
  * `file`: DOC or DOCX file to be uploaded.
* **Response:** JSON containing parsed markdown text, metadata, and images.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_document/docs" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.docx"
```

### **Parse Document (Generic)**

* **Endpoint:** `/parse_document`
* **Method:** `POST`
* **Description:** Parses a document file (PDF, PPT, DOC, DOCX) by converting it to PDF if necessary, then extracts text, images, and metadata.
* **Parameters:**
  * `file`: Document file to be uploaded.
* **Response:** JSON containing parsed markdown text, metadata, and images.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_document" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.docx"
```

***

## **Media Parsing Endpoints**

These endpoints are used to parse various media formats, such as images, videos, and audio files.

### **Parse Image**

* **Endpoint:** `/parse_media/image`
* **Method:** `POST`
* **Description:** Parses an image file by converting it to PDF, then extracts text, images, and metadata.
* **Parameters:**
  * `file`: Image file to be uploaded.
* **Response:** JSON containing parsed markdown text, metadata, and images.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_media/image" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/image.jpg"
```

### **Parse Video**

* **Endpoint:** `/parse_media/video`
* **Method:** `POST`
* **Description:** Parses a video file by extracting audio and transcribing it.
* **Parameters:**
  * `file`: Video file to be uploaded.
* **Response:** JSON containing the transcribed text.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_media/video" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/video.mp4"
```

### **Parse Audio**

* **Endpoint:** `/parse_media/audio`
* **Method:** `POST`
* **Description:** Parses an audio file by transcribing it.
* **Parameters:**
  * `file`: Audio file to be uploaded.
* **Response:** JSON containing the transcribed text.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_media/audio" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/audio.mp3"
```

### **Parse Media (Generic)**

* **Endpoint:** `/parse_media`
* **Method:** `POST`
* **Description:** Parses a media file (image, video, or audio) by converting to PDF if necessary or transcribing if audio.
* **Parameters:**
  * `file`: Media file to be uploaded.
* **Response:** JSON containing parsed markdown text or transcribed text, metadata, and images.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_media" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.mp4"
```

***

## **Website Parsing Endpoint**

This endpoint is used to parse the content of a website.

### **Parse Website**

* **Endpoint:** `/parse_website`
* **Method:** `POST`
* **Description:** Parses a website URL to extract text content and other relevant data.
* **Parameters:**
  * `url`: The URL of the website to be parsed.
* **Response:** JSON containing the parsed website content.

**Curl Request:**

```sh
curl -X POST "http://localhost:8000/parse_website" -H "accept: application/json" -H "Content-Type: application/json" -d '{"url": "https://www.example.com"}'
```

***
