"""
Script to download models
"""

import argparse
from omniparse import load_omnimodel


def download_models():
    parser = argparse.ArgumentParser(description="Download models for omniparse")

    parser.add_argument("--documents", action="store_true", help="Load document models")
    parser.add_argument("--media", action="store_true", help="Load media models")
    parser.add_argument("--web", action="store_true", help="Load web models")
    args = parser.parse_args()

    load_omnimodel(args.documents, args.media, args.web)


if __name__ == "__main__":
    download_models()
