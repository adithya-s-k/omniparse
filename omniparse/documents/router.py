"""
Title: OmniPrase
Author: Adithya S Kolavi
Date: 2025-05-23

This code includes portions of code from the Docling repository.
Original repository: https://github.com/docling-project/docling

License: MIT
URL: https://github.com/docling-project/docling/blob/main/LICENSE

Description:
This section of the code was adapted from the Docling repository to enhance text pdf/word/ppt parsing.
All credits for the original implementation go to Docling.
"""

import os
import tempfile
import subprocess
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from omniparse import get_shared_state

from omniparse.utils import encode_images
from omniparse.models import responseDocument
from docling.datamodel.base_models import DocumentStream

document_router = APIRouter()
model_state = get_shared_state()


# Document parsing endpoints
@document_router.post("/pdf")
async def parse_pdf_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        source = DocumentStream(name=file.filename, stream=BytesIO(file_bytes))
        filetype = os.path.splitext(file.filename)[1].lstrip('.').upper()
        out_meta = {"filename": file.filename, "filetype": filetype}

        docling_result = model_state.docling_converter.convert(source)
        full_text = docling_result.document.export_to_markdown()

        out_meta["block_stats"] = {
            "images": len(docling_result.document.pictures),
            "tables": len(docling_result.document.tables),
        }

        result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(file.filename, docling_result.document, result)

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

    source = DocumentStream(name=file.filename, stream=BytesIO(pdf_bytes))
    filetype = os.path.splitext(file.filename)[1].lstrip('.').upper()
    out_meta = {"filename": file.filename, "filetype": filetype}

    docling_result = model_state.docling_converter.convert(source)
    full_text = docling_result.document.export_to_markdown()

    out_meta["block_stats"] = {
        "images": len(docling_result.document.pictures),
        "tables": len(docling_result.document.tables),
    }

    os.remove(input_path)
    os.remove(output_pdf_path)
    os.rmdir(output_dir)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(file.filename, docling_result.document, result)

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

    source = DocumentStream(name=file.filename, stream=BytesIO(pdf_bytes))
    filetype = os.path.splitext(file.filename)[1].lstrip('.').upper()
    out_meta = {"filename": file.filename, "filetype": filetype}

    docling_result = model_state.docling_converter.convert(source)
    full_text = docling_result.document.export_to_markdown()

    out_meta["block_stats"] = {
        "images": len(docling_result.document.pictures),
        "tables": len(docling_result.document.tables),
    }

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(file.filename, docling_result.document, result)

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

    docling_result = model_state.docling_converter.convert(Path(input_path))
    full_text = docling_result.document.export_to_markdown()

    filetype = os.path.splitext(file.filename)[1].lstrip('.').upper()
    out_meta = {
        "filename": file.filename,
        "filetype": filetype,
        "block_stats": {
            "images": len(docling_result.document.pictures),
            "tables": len(docling_result.document.tables),
        },
    }

    os.remove(input_path)

    result = responseDocument(text=full_text, metadata=out_meta)
    encode_images(file.filename, docling_result.document, result)

    return JSONResponse(content=result.model_dump())
