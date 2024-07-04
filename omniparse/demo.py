"""
Title: OmniPrase
Author: Adithya S Kolavi
Date: 2024-07-02
"""

import os
import base64
import mimetypes
import requests
from PIL import Image
from io import BytesIO
import gradio as gr
# from omniparse.documents import parse_pdf

single_task_list = [
    'Caption', 'Detailed Caption', 'More Detailed Caption', 
    'OCR', 'OCR with Region'
]
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
