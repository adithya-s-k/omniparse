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
This section of the code was adapted from the marker repository to enhance text pdf/word/ppt parsing.
All credits for the original implementation go to VikParuchuri.
"""

import os
import tempfile
import subprocess

# from omniparse.documents.parse import parse_single_pdf
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from omniparse import get_shared_state

# from omniparse.documents import parse_pdf , parse_ppt , parse_doc
# from omniparse.documents import parse_pdf
from marker.convert import convert_single_pdf
from omniparse.utils import encode_images
from omniparse.models import responseDocument

document_router = APIRouter()
model_state = get_shared_state()


# Document parsing endpoints
@document_router.post("/pdf")
async def parse_pdf_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        full_text, images, out_meta = convert_single_pdf(
            file_bytes, model_state.model_list
        )

        result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(images, result)
        # result : responseDocument = convert_single_pdf(file_bytes , model_state.model_list)

        return JSONResponse(content=result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Document parsing endpoints
@document_router.post("/ppt")
async def parse_ppt_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ppt") as tmp_ppt:
        tmp_ppt.write(await file.read())
        tmp_ppt.flush()
        input_path = tmp_ppt.name

    output_dir = tempfile.mkdtemp()
    command = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        input_path,
    ]
    subprocess.run(command, check=True)

    output_pdf_path = os.path.join(
        output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    )

    with open(output_pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    full_text, images, out_meta = convert_single_pdf(pdf_bytes, model_state.model_list)

    os.remove(input_path)
    os.remove(output_pdf_path)
    os.rmdir(output_dir)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(images, result)

    return JSONResponse(content=result.model_dump())


@document_router.post("/docs")
async def parse_doc_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ppt") as tmp_ppt:
        tmp_ppt.write(await file.read())
        tmp_ppt.flush()
        input_path = tmp_ppt.name

    output_dir = tempfile.mkdtemp()
    command = [
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        input_path,
    ]
    subprocess.run(command, check=True)

    output_pdf_path = os.path.join(
        output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    )

    with open(output_pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    full_text, images, out_meta = convert_single_pdf(pdf_bytes, model_state.model_list)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(images, result)

    return JSONResponse(content=result.model_dump())


@document_router.post("")
async def parse_any_endpoint(file: UploadFile = File(...)):
    allowed_extensions = {".pdf", ".ppt", ".pptx", ".doc", ".docx"}
    file_ext = os.path.splitext(file.filename)[1]

    if file_ext.lower() not in allowed_extensions:
        return JSONResponse(
            content={
                "message": "Unsupported file type. Only PDF, PPT, and DOCX are allowed."
            },
            status_code=400,
        )

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(await file.read())
        tmp_file.flush()
        input_path = tmp_file.name

    if file_ext.lower() in {".ppt", ".pptx", ".doc", ".docx"}:
        output_dir = tempfile.mkdtemp()
        command = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            input_path,
        ]
        subprocess.run(command, check=True)
        output_pdf_path = os.path.join(
            output_dir, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
        )
        input_path = output_pdf_path

    # Common parsing logic
    full_text, images, out_meta = convert_single_pdf(input_path, model_state.model_list)

    os.remove(input_path)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(images, result)

    return JSONResponse(content=result.model_dump())


# @document_router.post("/docs")
# async def parse_docs_endpoint(file: UploadFile = File(...)):
#     try:

#         file_bytes = await file.read()
#         result = parse_doc(file_bytes , model_state)

#         return JSONResponse(content=result)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @document_router.post("/ppt")
# async def parse_ppt_endpoint(file: UploadFile = File(...)):
#     try:
#         file_bytes = await file.read()
#         result = parse_ppt(file_bytes , model_state)

#         return JSONResponse(content=result)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
