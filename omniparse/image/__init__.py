# Media parsing endpoints
import io
import os
import tempfile
import img2pdf
from PIL import Image
# from omniparse.document.parse import parse_single_image
from omniparse.documents.parse import parse_single_pdf
from omniparse.image.process import pre_process_image
from omniparse.utils import encode_images

def parse_image(input_data, model_state) -> dict:
    temp_files = []

    try:
        if isinstance(input_data, bytes):
            image = Image.open(io.BytesIO(input_data))
        elif isinstance(input_data, str) and os.path.isfile(input_data):
            image = Image.open(input_data)
        else:
            raise ValueError("Invalid input data format. Expected image bytes or image file path.")

        accepted_formats = {"PNG", "JPEG", "JPG", "TIFF", "WEBP"}
        if image.format not in accepted_formats:
            raise ValueError(f"Unsupported image format '{image.format}'. Accepted formats are: {', '.join(accepted_formats)}")

        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        # Create a temporary file for the image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image_file:
            image.save(temp_image_file.name)
            temp_files.append(temp_image_file.name)

            # Convert image to PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
                pdf_bytes = img2pdf.convert(temp_image_file.name)

                # Write PDF bytes to the temporary file
                temp_pdf_file.write(pdf_bytes)
                temp_pdf_path = temp_pdf_file.name
                temp_files.append(temp_pdf_path)

        # Parse the PDF file
        full_text, images, out_meta = parse_single_pdf(temp_pdf_path, model_state.model_list)
        images = encode_images(images)

        return {"message": "Document parsed successfully", "markdown": full_text, "metadata": out_meta, "images": images}

    finally:
        # Clean up the temporary files
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)

def process_image(input_data, task, model_state) -> dict:
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
            raise ValueError("Invalid input data format. Expected image bytes or image file path.")

        # Open the saved image using PIL
        image_data = Image.open(temp_file_path).convert("RGB")

        # Process the image using your function (e.g., process_image)
        results = pre_process_image(image_data, task, vision_model = model_state.vision_model, vision_processor = model_state.vision_processor)

        return {"results": results}

    finally:
        # Clean up the temporary files
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.remove(file_path)
