import subprocess
import os
from fastapi import UploadFile


async def convert_to_pdf(input_file: UploadFile, output_dir: str) -> str:
    """Converts a document to PDF using LibreOffice.

    Args:
        input_file: The UploadFile object of the input document.
        output_dir: The directory where the output PDF will be saved.

    Returns:
        The path of the converted PDF file.
    """
    # Save the input file to the temporary directory
    input_path = os.path.join(output_dir, input_file.filename)
    with open(input_path, "wb") as f:
        content = input_file.file.read()
        f.write(content)

    # Perform the conversion
    command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, input_path]
    subprocess.run(command, check=True)
    
    # Get the path to the converted PDF file
    pdf_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf")
    
    return pdf_file