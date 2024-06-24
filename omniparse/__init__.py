import torch
from typing import Optional , Any
from pydantic import BaseModel
from transformers import AutoProcessor, AutoModelForCausalLM
import whisper
from omniparse.utils import print_omniparse_text_art
from omniparse.web.web_crawler import WebCrawler
from omniparse.documents.models import load_all_models

import os
from typing import Optional, Dict, Any
import base64
from fastapi.responses import JSONResponse

class Document:
    def __init__(self):
        self.text: str = ""
        self.images: Dict[str, Dict[str, Optional[str]]] = {}
        self.metadata: Dict[str, Any] = {}

    def add_text(self, text: str):
        """Add text to the document."""
        self.text += text

    def add_image(self, imagename: str, image_data: bytes, caption: Optional[str] = None):
        """Add an image to the document."""
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        self.images[imagename] = {"base64": encoded_image, "caption": caption}

    def add_metadata(self, key: str, value: Any):
        """Add metadata to the document."""
        self.metadata[key] = value

    def to_json_response(self):
        """Convert the document to a JSON response compatible with FastAPI."""
        return JSONResponse(content={
            "text": self.text,
            "images": self.images,
            "metadata": self.metadata
        })

    def __str__(self):
        """Return the document text when printed."""
        return self.text

    def save(self, output_dir: str):
        """Save the document text and images to the specified directory."""
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the text to a .md file
        text_file_path = os.path.join(output_dir, "document.md")
        with open(text_file_path, "w") as text_file:
            text_file.write(self.text)

        # Save each image
        for imagename, imagedata in self.images.items():
            image_path = os.path.join(output_dir, imagename)
            with open(image_path, "wb") as image_file:
                image_file.write(base64.b64decode(imagedata["base64"]))

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
        shared_state.vision_model = AutoModelForCausalLM.from_pretrained('microsoft/Florence-2-base', trust_remote_code=True).to(device)
        shared_state.vision_processor = AutoProcessor.from_pretrained('microsoft/Florence-2-base', trust_remote_code=True)
    
    if load_media:
        print("[LOG] ✅ Loading Audio Model")
        shared_state.whisper_model = whisper.load_model("small")
    
    if load_web:
        print("[LOG] ✅ Loading Web Crawler")
        shared_state.crawler = WebCrawler(verbose=True)

def get_shared_state():
    return shared_state