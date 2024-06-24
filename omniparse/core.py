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