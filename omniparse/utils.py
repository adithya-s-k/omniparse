import base64
import os
import tempfile
from art import text2art
from omniparse.models import responseDocument


def encode_images(images, inputDocument: responseDocument):
    for i, (filename, image) in enumerate(images.items()):
        # Sanitize filename to prevent path traversal from embedded image names
        safe_filename = os.path.basename(filename)
        # Use a temporary file to avoid writing to arbitrary paths
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            # Save image as PNG to safe temporary path
            image.save(tmp_path, "PNG")
            # Read the saved image file as bytes
            with open(tmp_path, "rb") as f:
                image_bytes = f.read()
            # Convert image to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            inputDocument.add_image(image_name=safe_filename, image_data=image_base64)
        finally:
            # Remove the temporary image file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def print_omniparse_text_art(suffix=None):
    font = "nancyj"
    ascii_text = "  OmniParse"
    if suffix:
        ascii_text += f"  x  {suffix}"
    ascii_art = text2art(ascii_text, font=font)
    print("\n")
    print(ascii_art)
    print("""Created by Adithya S K : https://twitter.com/adithya_s_k""")
    print("\n")
    print("\n")
