import os
import tempfile
import subprocess
from omniparse.documents.parse import parse_single_pdf
from omniparse.utils import encode_images
# Function to handle PDF parsing
def parse_pdf(input_data , model_state) -> dict:
    try:
        if isinstance(input_data, bytes):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf_file:
                temp_pdf_file.write(input_data)
                temp_pdf_path = temp_pdf_file.name

            input_path = temp_pdf_path
            cleanup_tempfile = True

        elif isinstance(input_data, str) and input_data.endswith(".pdf"):
            input_path = input_data
            cleanup_tempfile = False

        else:
            raise ValueError("Invalid input data format. Expected bytes or PDF file path.")

        full_text, images, out_meta = parse_single_pdf(input_path, model_state.model_list)
        images = encode_images(images)

        if cleanup_tempfile:
            os.remove(input_path)

        return {"message": "PDF parsed successfully", "markdown": full_text, "metadata": out_meta, "images": images}

    except Exception as e:
        raise RuntimeError(f"Error parsing PPT: {str(e)}")

# Function to handle PPT and DOC parsing
def parse_ppt(input_data ,model_state) -> dict:
    try:
        if isinstance(input_data, bytes):
            print("Recieved ppt file")
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(input_data)
                tmp_file.flush()
                input_path = tmp_file.name
        
        elif isinstance(input_data, str) and (input_data.endswith(".ppt") or input_data.endswith(".pptx") or input_data.endswith(".doc") or input_data.endswith(".docx")):
            input_path = input_data
        
        else:
            raise ValueError("Invalid input data format. Expected bytes or PPT/DOC file path.")

        if input_path.endswith((".ppt", ".pptx", ".doc", ".docx")):
            output_dir = tempfile.mkdtemp()
            command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, input_path]
            subprocess.run(command, check=True)
            output_pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
            input_path = output_pdf_path
        
        full_text, images, out_meta = parse_single_pdf(input_path, model_state.model_list)
        images = encode_images(images)
        
        if input_data != input_path:
            os.remove(input_path)
        
        return {"message": "Document parsed successfully", "markdown": full_text, "metadata": out_meta, "images": images}

    except Exception as e:
        raise RuntimeError(f"Error parsing PPT: {str(e)}")

def parse_doc(input_data ,model_state) -> dict:
    try:
        if isinstance(input_data, bytes):
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(input_data)
                tmp_file.flush()
                input_path = tmp_file.name
        
        elif isinstance(input_data, str) and (input_data.endswith(".ppt") or input_data.endswith(".pptx") or input_data.endswith(".doc") or input_data.endswith(".docx")):
            input_path = input_data
        
        else:
            raise ValueError("Invalid input data format. Expected bytes or PPT/DOC file path.")

        if input_path.endswith((".ppt", ".pptx", ".doc", ".docx")):
            output_dir = tempfile.mkdtemp()
            command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, input_path]
            subprocess.run(command, check=True)
            output_pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
            input_path = output_pdf_path
        
        full_text, images, out_meta = parse_single_pdf(input_path, model_state.model_list)
        images = encode_images(images)
        
        if input_data != input_path:
            os.remove(input_path)
        
        return {"message": "Document parsed successfully", "markdown": full_text, "metadata": out_meta, "images": images}

    except Exception as e:
        raise RuntimeError(f"Error parsing PPT: {str(e)}")