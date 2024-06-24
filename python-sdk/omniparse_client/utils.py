import os
import base64

def save_images_and_markdown(response_data, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for pdf in response_data:
        pdf_filename = pdf['filename']
        pdf_output_folder = os.path.join(output_folder, os.path.splitext(pdf_filename)[0])

        # Create a folder for each PDF
        os.makedirs(pdf_output_folder, exist_ok=True)

        # Save markdown
        markdown_text = pdf['markdown']
        with open(os.path.join(pdf_output_folder, 'output.md'), 'w', encoding='utf-8') as f:
            f.write(markdown_text)

        # Save images
        image_data = pdf['images']
        for image_name, image_base64 in image_data.items():
            # Decode base64 image
            image_bytes = base64.b64decode(image_base64)

            # Save image
            with open(os.path.join(pdf_output_folder, image_name), 'wb') as f:
                f.write(image_bytes)
