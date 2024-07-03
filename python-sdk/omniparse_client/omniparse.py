import os
import httpx
import base64
import aiofiles
from typing import Optional
from .utils import save_images_and_markdown, ParsedDocument


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
            with open(pdf_file_path, "rb") as f:
                pdf_content = f.read()
            files.append(("pdf_files", (os.path.basename(pdf_file_path), pdf_content, "application/pdf")))

        # Send request to FastAPI server with all PDF files attached
        response = httpx.post(self.base_url, files=files)

        # Check if request was successful
        if response.status_code == 200:
            # Save markdown and images
            response_data = response.json()
            output_folder = os.path.splitext(os.path.basename(pdf_file_paths[0]))[0]
            save_images_and_markdown(response_data, output_folder)
            print("Markdown and images saved successfully.")
        else:
            print(f"Error: {response.text}")


class AsyncOmniParse:
    """
    An asynchronous client for interacting with the OmniParse server.

    OmniParse is a platform that ingests and parses unstructured data into structured,
    actionable data optimized for GenAI (LLM) applications. This client provides methods
    to interact with the OmniParse server, allowing users to parse various types of
    unstructured data including documents, images, videos, audio files, and web pages.

    The client supports parsing of multiple file types and provides structured output
    in markdown format, making it ideal for AI applications such as RAG (Retrieval-Augmented Generation)
    and fine-tuning.

    Attributes:
        api_key (str): API key for authentication with the OmniParse server.
        base_url (str): Base URL for the OmniParse API endpoints.
        timeout (int): Timeout for API requests in seconds.

    Usage Examples:
        ```python
        # Initialize the client
        parser = AsyncOmniParse(api_key="your_api_key", base_url="http://localhost:8000")

        # Parse a PDF document
        async def parse_pdf_example():
            result = await parser.parse_pdf("/path/to/document.pdf", output_folder="/path/to/output")
            print(result.markdown)  # Access the parsed content

        # Process an image
        async def process_image_example():
            result = await parser.process_image("/path/to/image.jpg", task="Caption", prompt="Describe this image")
            print(result)  # Print the image processing result

        # Parse a website
        async def parse_website_example():
            result = await parser.parse_website("https://example.com")
            print(result)  # Print the parsed website content

        # Parse a video file
        async def parse_video_example():
            result = await parser.parse_video("/path/to/video.mp4")
            print(result)  # Print the parsed video content

        # Use in an async context
        async def main():
            await parse_pdf_example()
            await process_image_example()
            await parse_website_example()
            await parse_video_example()

        # Run the async main function
        import asyncio
        asyncio.run(main())
        ```
    """

    def __init__(self, api_key=None, base_url="http://localhost:8000", timeout=120):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        self.parse_media_endpoint = "/parse_media"
        self.parse_website_endpoint = "/parse_website"
        self.parse_document_endpoint = "/parse_document"

        self.image_process_tasks = {
            "OCR",
            "OCR with Region",
            "Caption",
            "Detailed Caption",
            "More Detailed Caption",
            "Object Detection",
            "Dense Region Caption",
            "Region Proposal",
        }

        self.allowed_audio_extentions = {".mp3", ".wav", ".aac"}
        self.allowed_video_extentions = {".mp4", ".mkv", ".avi", ".mov"}
        self.allowed_document_extentions = {".pdf", ".ppt", ".pptx", ".doc", ".docs"}
        self.allowed_image_extentions = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".heic"}

    async def __request__(self, endpoint: str, files: Optional[dict] = None, json: Optional[dict] = None) -> dict:
        """
        Internal method to make API requests.

        Args:
            endpoint (str): API endpoint.
            files (dict, optional): Files to be sent with the request.
            json (dict, optional): JSON data to be sent with the request.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, files=files, json=json, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

    async def parse_document(self, file_path: str, output_folder: Optional[str]) -> ParsedDocument:
        """
        Parse a document file (PDF, PPT, or DOCX) and convert it to structured markdown.

        This method extracts text, tables, and images from the document, providing a
        structured output optimized for LLM applications.

        Args:
            file_path (str): Path to the document file.
            output_folder (Optional[str]): If provided, the parsed data will be saved in this folder.
                A new subfolder will be created with the name of the input file, and the parsed
                content will be saved within this subfolder.

        Returns:
            ParsedDocument: Parsed document data including extracted text, tables, and images.

        Raises:
            ValueError: If the file type is not supported.

        Note:
            If output_folder is provided, the method will save the parsed data and print a
            confirmation message.
        """
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext not in self.allowed_document_extentions:
            raise ValueError(
                f"Unsupported file type. Only files of format {', '.join(self.allowed_document_extentions)} are allowed."
            )

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        response = await self.__request__(self.parse_document_endpoint, files={"file": file_data})
        data = ParsedDocument(**response, source_path=file_path, output_folder=output_folder)
        if output_folder:
            data.save_data(echo=True)
        return data

    async def parse_pdf(self, file_path: str, output_folder: Optional[str]) -> ParsedDocument:
        """
        Parse a PDF file and convert it to structured markdown.

        Args:
            file_path (str): Path to the PDF file.
            output_folder (Optional[str]): If provided, the parsed data will be saved in this folder.
                A new subfolder will be created with the name of the PDF file, and the parsed
                content will be saved within this subfolder.

        Returns:
            ParsedDocument: Parsed PDF data including extracted text, tables, and images.

        Raises:
            ValueError: If the file is not a PDF.

        Note:
            If output_folder is provided, the method will save the parsed data and print a
            confirmation message.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext != ".pdf":
            raise ValueError(f"The file must be a PDF (.pdf), but received a file of type {file_ext}")

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        response = await self.__request__(f"{self.parse_document_endpoint}/pdf", files={"file": file_data})
        data = ParsedDocument(**response, source_path=file_path, output_folder=output_folder)
        if output_folder:
            data.save_data(echo=True)
        return data

    async def parse_ppt(self, file_path: str, output_folder: Optional[str]) -> ParsedDocument:
        """
        Parse a PowerPoint file and convert it to structured markdown.

        Args:
            file_path (str): Path to the PPT or PPTX file.
            output_folder (Optional[str]): If provided, the parsed data will be saved in this folder.
                A new subfolder will be created with the name of the PowerPoint file, and the parsed
                content will be saved within this subfolder.

        Returns:
            ParsedDocument: Parsed PowerPoint data including extracted text, tables, and images.

        Raises:
            ValueError: If the file is not a PPT or PPTX.

        Note:
            If output_folder is provided, the method will save the parsed data and print a
            confirmation message.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in [".ppt", ".pptx"]:
            raise ValueError(f"The file must be a PPT file (.ppt or .pptx), but received a file of type {file_ext}")

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        response = await self.__request__(f"{self.parse_document_endpoint}/ppt", files={"file": file_data})
        data = ParsedDocument(**response, source_path=file_path, output_folder=output_folder)
        if output_folder:
            data.save_data(echo=True)
        return data

    async def parse_docs(self, file_path: str, output_folder: Optional[str]) -> ParsedDocument:
        """
        Parse a Word document file and convert it to structured markdown.

        Args:
            file_path (str): Path to the DOC or DOCS file.
            output_folder (Optional[str]): If provided, the parsed data will be saved in this folder.
                A new subfolder will be created with the name of the Word document file, and the parsed
                content will be saved within this subfolder.

        Returns:
            ParsedDocument: Parsed Word document data including extracted text, tables, and images.

        Raises:
            ValueError: If the file is not a DOC or DOCS.

        Note:
            If output_folder is provided, the method will save the parsed data and print a
            confirmation message.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in [".doc", ".docs"]:
            raise ValueError(f"The file must be a DOC file (.doc or .docs), but received a file of type {file_ext}")

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        response = await self.__request__(f"{self.parse_document_endpoint}/docs", files={"file": file_data})
        data = ParsedDocument(**response, source_path=file_path, output_folder=output_folder)
        if output_folder:
            data.save_data(echo=True)
        return data

    async def parse_image(self, file_path: str) -> dict:
        """
        Parse an image file, extracting visual information and generating captions.

        This method can be used for tasks such as object detection, image captioning,
        and text extraction (OCR) from images.

        Args:
            file_path (str): Path to the image file.

        Returns:
            dict: Parsed image data including captions, detected objects, and extracted text.

        Raises:
            ValueError: If the file type is not supported.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.allowed_image_extentions:
            raise ValueError(
                f"Unsupported file type. Only files of format {', '.join(self.allowed_image_extentions)} are allowed."
            )

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        return await self.__request__(f"{self.parse_media_endpoint}/image", files={"file": file_data})

    async def parse_video(self, file_path: str) -> dict:
        """
        Parse a video file, extracting key frames, generating captions, and transcribing audio.

        This method provides a structured representation of the video content, including
        visual and audio information.

        Args:
            file_path (str): Path to the video file.

        Returns:
            dict: Parsed video data including transcriptions, captions, and key frame information.

        Raises:
            ValueError: If the file type is not supported.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.allowed_video_extentions:
            raise ValueError(
                f"Unsupported file type. Only files of format {', '.join(self.allowed_video_extentions)} are allowed."
            )

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        return await self.__request__(f"{self.parse_media_endpoint}/video", files={"file": file_data})

    async def parse_audio(self, file_path: str) -> dict:
        """
        Parse an audio file, transcribing speech to text.

        This method converts spoken words in the audio file to text, providing a textual
        representation of the audio content.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            dict: Parsed audio data including the transcription.

        Raises:
            ValueError: If the file type is not supported.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.allowed_audio_extentions:
            raise ValueError(
                f"Unsupported file type. Only files of format {', '.join(self.allowed_audio_extentions)} are allowed."
            )

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        return await self.__request__(f"{self.parse_media_endpoint}/audio", files={"file": file_data})

    async def process_image(self, file_path: str, task: str, prompt: Optional[str] = None) -> dict:
        """
        Process an image with a specific task such as OCR, captioning, or object detection.

        This method allows for more specific image processing tasks beyond basic parsing.

        Args:
            file_path (str): Path to the image file.
            task (str): Image processing task to perform (e.g., "OCR", "Caption", "Object Detection").
            prompt (Optional[str]): Optional prompt for certain tasks, useful for guided processing.

        Returns:
            dict: Processed image data specific to the requested task.

        Raises:
            ValueError: If the task is invalid or the file type is not supported.
        """
        if task not in self.image_process_tasks:
            raise ValueError(f"Invalid task. Choose from: {', '.join(self.image_process_tasks)}")
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.allowed_image_extentions:
            raise ValueError(
                f"Unsupported file type. Only files of format {', '.join(self.allowed_image_extentions)} are allowed."
            )

        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        data = {"task": task}
        if prompt:
            data["prompt"] = prompt
        return await self.__request__(
            json=data, files={"image": file_data}, endpoint=f"{self.parse_media_endpoint}/process_image"
        )

    async def parse_website(self, url: str) -> dict:
        """
        Parse a website, extracting structured content from web pages.

        This method crawls the specified URL, extracting text, images, and other relevant
        content in a structured format.

        Args:
            url (str): URL of the website to parse.

        Returns:
            dict: Parsed website data including extracted text, links, and media references.
        """
        return await self.__request__(self.parse_website_endpoint, json={"url": url})
