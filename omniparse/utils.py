import base64
import tempfile
import os
from art import text2art
from omniparse.models import responseDocument


def encode_images(document_name, document, inputDocument: responseDocument):
    file_name = os.path.splitext(document_name)[0]
    for idx, image in enumerate(document.pictures):
        with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as tmp_file:
            filename = tmp_file.name
            image.get_image(document).save(filename, "PNG")
            with open(filename, "rb") as f:
                image_bytes = f.read()

            # Convert image to base64
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            inputDocument.add_image(
                image_name=f"{file_name}_image_{idx}", image_data=image_base64
            )


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
