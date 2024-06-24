import base64
import os
from art import text2art

def encode_images(images):
    image_data = {}
    for i, (filename, image) in enumerate(images.items()):
        # print(f"Processing image {filename}")
        
        # Save image as PNG
        image.save(filename, "PNG")

        # Read the saved image file as bytes
        with open(filename, "rb") as f:
            image_bytes = f.read()

        # Convert image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        image_data[f'{filename}'] = image_base64

        # Remove the temporary image file
        os.remove(filename)
    return image_data


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