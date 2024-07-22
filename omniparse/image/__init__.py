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
This section of the code was adapted from the marker repository to enhance text image parsing.
All credits for the original implementation go to VikParuchuri.
"""

"""
Title: OmniPrase
Author: Adithya S Kolavi
Date: 2024-07-02

This code includes portions of code from the Florence-2 repository by gokaygokay.
Original repository: https://huggingface.co/spaces/gokaygokay/Florence-2

Original Author: gokaygokay
Original Date: 2024-06-30

URL: https://huggingface.co/spaces/gokaygokay/Florence-2
"""


# Media parsing endpoints
import io
import os
import tempfile
import img2pdf
from PIL import Image

# from omniparse.document.parse import parse_single_image
from marker.convert import convert_single_pdf
from omniparse.image.process import process_image_task
from omniparse.utils import encode_images
from omniparse.models import responseDocument


def parse_image(input_data, model_state) -> dict:
    temp_files = []

    try:
        if isinstance(input_data, bytes):
            image = Image.open(io.BytesIO(input_data))
        elif isinstance(input_data, str) and os.path.isfile(input_data):
            image = Image.open(input_data)
        else:
            raise ValueError(
                "Invalid input data format. Expected image bytes or image file path."
            )

        accepted_formats = {"PNG", "JPEG", "JPG", "TIFF", "WEBP"}
        if image.format not in accepted_formats:
            raise ValueError(
                f"Unsupported image format '{image.format}'. Accepted formats are: {', '.join(accepted_formats)}"
            )

        # Convert RGBA to RGB if necessary
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Create a temporary file for the image
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".jpg"
        ) as temp_image_file:
            image.save(temp_image_file.name)
            temp_files.append(temp_image_file.name)

            # Convert image to PDF
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf"
            ) as temp_pdf_file:
                pdf_bytes = img2pdf.convert(temp_image_file.name)

                # Write PDF bytes to the temporary file
                temp_pdf_file.write(pdf_bytes)
                temp_pdf_path = temp_pdf_file.name
                temp_files.append(temp_pdf_path)

        # Parse the PDF file
        full_text, images, out_meta = convert_single_pdf(
            temp_pdf_path, model_state.model_list
        )

        parse_image_result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(images, parse_image_result)

        return parse_image_result

    finally:
        # Clean up the temporary files
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)


def process_image(input_data, task, model_state) -> responseDocument:
    try:
        temp_files = []

        if isinstance(input_data, bytes):
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(input_data)
                temp_file.flush()
                temp_file_path = temp_file.name
                temp_files.append(temp_file_path)

        elif isinstance(input_data, str) and os.path.isfile(input_data):
            temp_file_path = input_data
            temp_files.append(temp_file_path)

        else:
            raise ValueError(
                "Invalid input data format. Expected image bytes or image file path."
            )

        # Open the saved image using PIL
        image_data = Image.open(temp_file_path).convert("RGB")

        # Process the image using your function (e.g., process_image)
        image_process_results: responseDocument = process_image_task(
            image_data, task, model_state
        )

        return image_process_results

    finally:
        # Clean up the temporary files
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)
