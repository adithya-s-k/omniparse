import base64
import os
import tempfile
from art import text2art
from omniparse.models import responseDocument


def encode_images(images, inputDocument: responseDocument):
    for i, (filename, image) in enumerate(images.items()):
        # Use only the basename of the parsed image name to prevent path
        # traversal via crafted filenames embedded in user-supplied documents
        # (e.g. an image named "../../etc/foo" could otherwise cause
        # arbitrary file write/delete). The original name is retained only
        # as metadata in the response document.
        safe_name = os.path.basename(filename) or f"image_{i}.png"
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, safe_name)
            # Save image as PNG to a sandboxed temporary location
            image.save(tmp_path, "PNG")
            # Read the saved image file as bytes
            with open(tmp_path, "rb") as f:
                image_bytes = f.read()
            # Convert image to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            inputDocument.add_image(image_name=safe_name, image_data=image_base64)


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
