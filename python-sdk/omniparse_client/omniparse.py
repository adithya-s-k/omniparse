import os
import requests
import base64
from .utils import save_images_and_markdown

class OmniParse:
    def __init__(self, api_key=None, base_url="http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url

    def load_data(self, file_path):
        return self.convert_pdf_to_markdown_and_save([file_path])

    def convert_pdf_to_markdown_and_save(self, pdf_file_paths):
        files = []

        # Prepare the files for the request
        for pdf_file_path in pdf_file_paths:
            with open(pdf_file_path, 'rb') as f:
                pdf_content = f.read()
            files.append(('pdf_files', (os.path.basename(pdf_file_path), pdf_content, 'application/pdf')))

        # Send request to FastAPI server with all PDF files attached
        response = requests.post(self.base_url, files=files)

        # Check if request was successful
        if response.status_code == 200:
            # Save markdown and images
            response_data = response.json()
            output_folder = os.path.splitext(os.path.basename(pdf_file_paths[0]))[0]
            save_images_and_markdown(response_data, output_folder)
            print("Markdown and images saved successfully.")
        else:
            print(f"Error: {response.text}")

