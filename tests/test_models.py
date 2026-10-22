import sys
import types
import unittest
from importlib import import_module
from pathlib import Path


# Load the lightweight response models without importing the application package,
# whose __init__ eagerly loads OCR, vision, audio, and crawler runtimes.
if "omniparse" not in sys.modules:
    package = types.ModuleType("omniparse")
    package.__path__ = [str(Path(__file__).resolve().parents[1] / "omniparse")]
    sys.modules["omniparse"] = package

models = import_module("omniparse.models")
responseDocument = models.responseDocument
responseImage = models.responseImage


class ResponseDocumentTests(unittest.TestCase):
    def test_image_processor_uses_images_and_only_fills_missing_captions(self):
        document = responseDocument(
            images=[
                responseImage(
                    image_name="already-captioned.png",
                    image_info={"caption": "existing synthetic caption"},
                ),
                responseImage(image_name="needs-caption.png", image_info={}),
                responseImage(image_name="nullable-info.png", image_info=None),
            ]
        )
        processed = []

        document.image_processor(
            lambda image_name: processed.append(image_name) or f"caption:{image_name}"
        )

        self.assertEqual(processed, ["needs-caption.png", "nullable-info.png"])
        self.assertEqual(
            document.images[0].image_info["caption"], "existing synthetic caption"
        )
        self.assertEqual(
            document.images[1].image_info["caption"], "caption:needs-caption.png"
        )
        self.assertEqual(
            document.images[2].image_info["caption"], "caption:nullable-info.png"
        )


if __name__ == "__main__":
    unittest.main()
