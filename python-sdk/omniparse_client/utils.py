import os
import re
import base64
import mimetypes
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, model_validator


class ImageObj(BaseModel):
    """
    Represents an image object with name, binary data, and MIME type.

    Attributes:
        name (str): The name of the image file.
        bytes (str): The binary data of the image, encoded as a string.
        mime_type (str): The MIME type of the image, automatically guessed if not provided.

    Methods:
        set_mime_type: A validator that automatically sets the MIME type based on the file name if not provided.
    """

    name: str
    bytes: bytes
    mime_type: Optional[str] = None

    @model_validator(mode="before")
    def set_mime_type(cls, values):
        name = values.get("name")
        mime_type = values.get("mime_type")

        if not mime_type and name:
            mime_type, _ = mimetypes.guess_type(name)
            values["mime_type"] = mime_type
        return values


class TableObj(BaseModel):
    """
    Represents a table extracted from markdown.

    Attributes:
        name (str): The name of the table.
        markdown (str): The original markdown representation of the table.
        titles (List[str]): The column titles of the table.
        data (List[List[str]]): The table data as a list of rows, where each row is a list of cell values.
    """

    name: str
    markdown: str
    titles: Optional[List[str]] = None
    data: Optional[List[List[str]]] = None


class MetaData(BaseModel):
    """
    Contains metadata about a parsed document.

    Attributes:
        filetype (str): The type of the file (e.g., 'pdf', 'docx').
        language (List[str]): The detected languages in the document.
        toc (List[Any]): Table of contents, if available.
        pages (int): Number of pages in the document.
        ocr_stats (Dict[str, Any]): Statistics related to OCR processing.
        block_stats (Dict[str, Any]): Statistics about document blocks.
        postprocess_stats (Dict[str, Any]): Statistics about post-processing.
    """

    filetype: str
    language: List[str] = []
    toc: List[Any] = []
    pages: int = 0
    ocr_stats: Dict[str, Any] = {}
    block_stats: Dict[str, Any] = {}
    postprocess_stats: Dict[str, Any] = {}


class ParsedDocument(BaseModel):
    """
    Represents a parsed document with its content and associated data.

    Attributes:
        markdown (str): The document content in markdown format.
        images (Optional[List[ImageObj]|dict]): Images extracted from the document.
        tables (Optional[List[TableObj]]): Tables extracted from the document.
        metadata (Optional[MetaData]): Metadata about the document.
        source_path (Optional[str]): Path to the source document.
        output_folder (Optional[str]): Folder to save parsed data.

    Methods:
        set_mime_type: A validator that processes images and tables data.
        save_data: Saves the parsed document data to files.
    """

    markdown: str
    images: Optional[List[ImageObj] | dict] = None
    tables: Optional[List[TableObj]] = None
    metadata: Optional[MetaData] = None
    source_path: str
    output_folder: Optional[str] = None

    @model_validator(mode="before")
    def set_mime_type(cls, values):
        images: dict = values.get("images")
        markdown_text: str = values.get("markdown")
        has_tables: bool = values.get("metadata", {}).get("block_stats", False)

        if has_tables:
            values["tables"] = [table.model_dump() for table in markdown_to_tables(markdown_text)]
        if isinstance(images, dict):
            values["images"] = []
            for name, data in images.items():
                values["images"].append(ImageObj(name=name, bytes=data).model_dump())

        return values

    def save_data(self, echo: bool = False):
        """
        Saves the parsed document data to files.

        Args:
            echo (bool): If True, prints a message after saving the data.
        """
        if not self.output_folder:
            print("No target path provided for saving the parsed data.")
            return
        base_name = os.path.basename(self.source_path)
        filename = os.path.splitext(base_name)[0]

        markdown_output_path = os.path.join(self.output_folder, f"{filename}/output.md")
        image_output_dir = os.path.join(self.output_folder, filename)
        os.makedirs(image_output_dir, exist_ok=True)

        with open(markdown_output_path, "w", encoding="utf-8") as md_file:
            md_file.write(self.markdown)

        if self.images:
            for image_obj in self.images:
                image_filename = image_obj.name
                image_path = os.path.join(image_output_dir, image_filename)

                _, ext = os.path.splitext(image_filename)
                assert image_obj is not None and image_obj.mime_type is not None
                if ext != "." + image_obj.mime_type.split("/")[1]:
                    image_filename += ext

                with open(image_path, "wb") as img_file:
                    img_file.write(image_obj.bytes)
        if echo:
            print(f"Data saved to {markdown_output_path}")


def extract_markdown_tables(markdown_string: str) -> List[str]:
    """
    Extracts all tables from a markdown string.

    Args:
        markdown_string (str): The input markdown string containing tables.

    Returns:
        List[str]: A list of strings, where each string is a complete markdown table.
    """
    table_pattern = r"(\|[^\n]+\|\n)((?:\|:?[-]+:?)+\|)(\n(?:\|[^\n]+\|\n?)+)"
    tables = re.findall(table_pattern, markdown_string, re.MULTILINE)
    return ["".join(table) for table in tables]


def markdown_to_tables(markdown: str) -> List[TableObj] | None:
    """
    Converts markdown tables to a list of TableObj instances.

    Args:
        markdown (str): The input markdown string containing tables.

    Returns:
        List[TableObj]|None: A list of TableObj instances if tables are found, None otherwise.
    """
    markdown_tables = extract_markdown_tables(markdown)
    tables = []
    if markdown_tables:
        for i, table_md in enumerate(markdown_tables):
            rows = table_md.strip().split("\n")
            titles = [cell.strip() for cell in rows[0].split("|") if cell.strip()]
            data_rows = [row for row in rows[2:] if not set(row.strip(" |")).issubset(set(":-"))]
            data = [[cell.strip() for cell in row.split("|") if cell.strip()] for row in data_rows]
            tables.append(TableObj(data=data, titles=titles, name=f"table_{i}", markdown=table_md))
    return tables or None


def save_images_and_markdown(response_data, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for pdf in response_data:
        pdf_filename = pdf["filename"]
        pdf_output_folder = os.path.join(output_folder, os.path.splitext(pdf_filename)[0])

        # Create a folder for each PDF
        os.makedirs(pdf_output_folder, exist_ok=True)

        # Save markdown
        markdown_text = pdf["markdown"]
        with open(os.path.join(pdf_output_folder, "output.md"), "w", encoding="utf-8") as f:
            f.write(markdown_text)

        # Save images
        image_data = pdf["images"]
        for image_name, image_base64 in image_data.items():
            # Decode base64 image
            image_bytes = base64.b64decode(image_base64)

            # Save image
            with open(os.path.join(pdf_output_folder, image_name), "wb") as f:
                f.write(image_bytes)
