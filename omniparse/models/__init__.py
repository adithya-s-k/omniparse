import base64
from io import BytesIO
from PIL import Image as PILImage
from typing import Callable, List, Dict, Any, Union
from fastapi import HTTPException
from pydantic import BaseModel, Field


class responseImage(BaseModel):
    image: str = ""
    image_name: str = ""
    image_info: Union[Dict[str, Any], None] = Field(default_factory=dict)


class responseDocument(BaseModel):
    text: str = ""
    images: List[responseImage] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunks: List[str] = Field(default_factory=list)

    def add_image(
        self,
        image_name: str,
        image_data: Union[str, PILImage.Image],
        image_info: Union[Dict[str, Any], None] = {},
    ):
        if isinstance(image_data, str):
            # If image_data is base64 encoded, decode it
            try:
                image_bytes = base64.b64decode(image_data)
                pil_image = PILImage.open(BytesIO(image_bytes))
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Failed to decode base64 image: {str(e)}"
                )
        elif isinstance(image_data, PILImage.Image):
            # If image_data is already a PIL.Image instance, use it directly
            pil_image = image_data
        else:
            raise ValueError(
                "Unsupported image_data type. Should be either string (file path), PIL.Image instance, or base64 encoded string."
            )

        new_image = responseImage(
            image=self.encode_image_to_base64(pil_image),
            image_name=image_name,
            image_info=image_info,
        )
        self.images.append(new_image)

    def encode_image_to_base64(self, image: PILImage.Image) -> str:
        # Convert PIL image to base64 string
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_base64

    def image_processor(self, image_processor: Callable[[str], str]):
        for img in self.image:
            if not img.image_info.get("caption"):  # Only generate caption if it's empty
                img.image_info["caption"] = image_processor(img.image_name)

    def chunk_text(self, chunker: Callable[[str], List[str]]):
        self.chunks = chunker(self.text)
