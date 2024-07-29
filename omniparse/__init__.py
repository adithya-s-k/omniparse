"""
Title: OmniPrase
Author: Adithya S Kolavi
Date: 2024-07-02

This code includes portions of code from the marker repository by VikParuchuri.
Original repository: https://github.com/VikParuchuri/marker

Original Author: VikParuchuri
Original Date: 2024-01-15

License: GNU General Public License (GPL) Version 3
URL: https://github.com/VikParuchuri/marker/blob/master/LICENSE

Description:
This section of the code was adapted from the marker repository to load all the OCR, layout and reading order detection models.
All credits for the original implementation go to VikParuchuri.
"""

import torch
from typing import Any
from pydantic import BaseModel
from transformers import AutoProcessor, AutoModelForCausalLM
import whisper
from omniparse.utils import print_omniparse_text_art
from omniparse.web.web_crawler import WebCrawler
from marker.models import load_all_models
# from omniparse.documents.models import load_all_models


class SharedState(BaseModel):
    model_list: Any = None
    vision_model: Any = None
    vision_processor: Any = None
    whisper_model: Any = None
    crawler: Any = None


shared_state = SharedState()


def load_omnimodel(load_documents: bool, load_media: bool, load_web: bool):
    global shared_state
    print_omniparse_text_art()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if load_documents:
        print("[LOG] ✅ Loading OCR Model")
        shared_state.model_list = load_all_models()
        print("[LOG] ✅ Loading Vision Model")
        # if device == "cuda":
        shared_state.vision_model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Florence-2-base", trust_remote_code=True
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
