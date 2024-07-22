import warnings
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from omniparse import load_omnimodel
from omniparse.documents.router import document_router
from omniparse.media.router import media_router
from omniparse.image.router import image_router
from omniparse.web.router import website_router
from omniparse.demo import demo_ui

# logging.basicConfig(level=logging.DEBUG)
import gradio as gr

warnings.filterwarnings("ignore", category=UserWarning)  # Filter torch pytree user warnings
# app = FastAPI(lifespan=lifespan)
app = FastAPI()

# io = gr.Interface(lambda x: "Hello, " + x + "!", "textbox", "textbox")


def add(app: FastAPI):
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )


# Include routers in the main app
app.include_router(document_router, prefix="/parse_document", tags=["Documents"])
app.include_router(image_router, prefix="/parse_image", tags=["Images"])
app.include_router(media_router, prefix="/parse_media", tags=["Media"])
app.include_router(website_router, prefix="/parse_website", tags=["Website"])
app = gr.mount_gradio_app(app, demo_ui, path="")


def main():
    # parse environment variables
    import os

    PORT = int(os.getenv("PORT", 8000))
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the omniparse server.")
    parser.add_argument("--host", default="0.0.0.0", help="Host IP address")
    parser.add_argument("--port", type=int, default=PORT, help="Port number")
    parser.add_argument("--documents", action="store_true", help="Load document models")
    parser.add_argument("--media", action="store_true", help="Load media models")
    parser.add_argument("--web", action="store_true", help="Load web models")
    parser.add_argument("--reload", action="store_true", help="Reload Server")
    args = parser.parse_args()

    # Set global variables based on parsed arguments
    load_omnimodel(args.documents, args.media, args.web)

    # Conditionally include routers based on arguments
    app.include_router(document_router, prefix="/parse_document", tags=["Documents"], include_in_schema=args.documents)
    app.include_router(image_router, prefix="/parse_image", tags=["Images"], include_in_schema=args.documents)
    app.include_router(media_router, prefix="/parse_media", tags=["Media"], include_in_schema=args.media)
    app.include_router(website_router, prefix="/parse_website", tags=["Website"], include_in_schema=args.web)

    # Start the server
    import uvicorn

    uvicorn.run("server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
