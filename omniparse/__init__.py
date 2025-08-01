"""
Title: OmniPrase
Author: Adithya S Kolavi
Date: 2025-05-23

This code includes portions of code from the Docling repository.
Original repository: https://github.com/docling-project/docling

License: MIT
URL: https://github.com/docling-project/docling/blob/main/LICENSE

Description:
This section of the code was adapted from the Docling repository to enhance text pdf/word/ppt parsing.
All credits for the original implementation go to Docling.
"""

import torch
from typing import Any
from pydantic import BaseModel
from transformers import AutoProcessor, AutoModelForCausalLM
import whisper
from omniparse.utils import print_omniparse_text_art
from omniparse.web.web_crawler import WebCrawler
from docling.utils.model_downloader import download_models
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions


class SharedState(BaseModel):
    docling_converter: Any = None
    vision_model: Any = None
    vision_processor: Any = None
    whisper_model: Any = None
    crawler: Any = None


shared_state = SharedState()

IMAGE_RESOLUTION_SCALE = 2.0
pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True


def load_omnimodel(load_documents: bool, load_media: bool, load_web: bool):
    global shared_state
    print_omniparse_text_art()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if load_documents:
        print("[LOG] ✅ Loading OCR Model")
        download_models()
        shared_state.docling_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        print("[LOG] ✅ Loading Vision Model")
        # if device == "cuda":
        shared_state.vision_model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Florence-2-base", torch_dtype=torch.float32, trust_remote_code=True
        ).to(device)
        shared_state.vision_processor = AutoProcessor.from_pretrained(
            "microsoft/Florence-2-base", trust_remote_code=True
        )

    if load_media:
        print("[LOG] ✅ Loading Audio Model")
        shared_state.whisper_model = whisper.load_model("small")

    if load_web:
        print("[LOG] ✅ Loading Web Crawler")
        shared_state.crawler = WebCrawler(verbose=True)


def get_shared_state():
    return shared_state


def get_active_models():
    print(shared_state)
    # active_models = [key for key, value in shared_state.dict().items() if value is not None]
    # print(f"These are the active model : {active_models}")
    return shared_state
