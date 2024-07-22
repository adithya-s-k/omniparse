"""
Title: OmniPrase
Author: Adithya S Kolavi
Date: 2024-07-02

This code includes portions of code from the Florence-2 repository by gokaygokay.
Original repository: https://huggingface.co/spaces/gokaygokay/Florence-2

Original Author: gokaygokay
Original Date: 2024-06-30

URL: https://huggingface.co/spaces/gokaygokay/Florence-2
"""

from typing import Dict, Any, Union
from PIL import Image as PILImage
import base64
from io import BytesIO
import copy
from omniparse.image.utils import plot_bbox, fig_to_pil, draw_polygons, draw_ocr_bboxes
from omniparse.models import responseDocument


def process_image_task(
    image_data: Union[str, bytes, PILImage.Image], task_prompt: str, model_state
) -> Dict[str, Any]:
    # Convert image_data if it's in bytes
    if isinstance(image_data, bytes):
        pil_image = PILImage.open(BytesIO(image_data))
    elif isinstance(image_data, str):
        try:
            image_bytes = base64.b64decode(image_data)
            pil_image = PILImage.open(BytesIO(image_bytes))
        except Exception as e:
            raise ValueError(f"Failed to decode base64 image: {str(e)}")
    elif isinstance(image_data, PILImage.Image):
        pil_image = image_data
    else:
        raise ValueError(
            "Unsupported image_data type. Should be either string (file path), bytes (binary image data), or PIL.Image instance."
        )

    # Process based on task_prompt
    if task_prompt == "Caption":
        task_prompt_model = "<CAPTION>"
    elif task_prompt == "Detailed Caption":
        task_prompt_model = "<DETAILED_CAPTION>"
    elif task_prompt == "More Detailed Caption":
        task_prompt_model = "<MORE_DETAILED_CAPTION>"
    elif task_prompt == "Caption + Grounding":
        task_prompt_model = "<CAPTION>"
    elif task_prompt == "Detailed Caption + Grounding":
        task_prompt_model = "<DETAILED_CAPTION>"
    elif task_prompt == "More Detailed Caption + Grounding":
        task_prompt_model = "<MORE_DETAILED_CAPTION>"
    elif task_prompt == "Object Detection":
        task_prompt_model = "<OD>"
    elif task_prompt == "Dense Region Caption":
        task_prompt_model = "<DENSE_REGION_CAPTION>"
    elif task_prompt == "Region Proposal":
        task_prompt_model = "<REGION_PROPOSAL>"
    elif task_prompt == "Caption to Phrase Grounding":
        task_prompt_model = "<CAPTION_TO_PHRASE_GROUNDING>"
    elif task_prompt == "Referring Expression Segmentation":
        task_prompt_model = "<REFERRING_EXPRESSION_SEGMENTATION>"
    elif task_prompt == "Region to Segmentation":
        task_prompt_model = "<REGION_TO_SEGMENTATION>"
    elif task_prompt == "Open Vocabulary Detection":
        task_prompt_model = "<OPEN_VOCABULARY_DETECTION>"
    elif task_prompt == "Region to Category":
        task_prompt_model = "<REGION_TO_CATEGORY>"
    elif task_prompt == "Region to Description":
        task_prompt_model = "<REGION_TO_DESCRIPTION>"
    elif task_prompt == "OCR":
        task_prompt_model = "<OCR>"
    elif task_prompt == "OCR with Region":
        task_prompt_model = "<OCR_WITH_REGION>"
    else:
        raise ValueError("Invalid task prompt")

    results, processed_image = pre_process_image(
        pil_image,
        task_prompt_model,
        model_state.vision_model,
        model_state.vision_processor,
    )
    # Update responseDocument fields based on the results
    process_image_result = responseDocument(text=str(results))

    if processed_image is not None:
        process_image_result.add_image(f"{task_prompt}", processed_image)

    return process_image_result


# Your pre_process_image function with some adjustments
def pre_process_image(image, task_prompt, vision_model, vision_processor):
    if task_prompt == "<CAPTION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        return results, None
    elif task_prompt == "<DETAILED_CAPTION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        return results, None
    elif task_prompt == "<MORE_DETAILED_CAPTION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        return results, None
    elif task_prompt == "<CAPTION_TO_PHRASE_GROUNDING>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<DETAILED_CAPTION + GROUNDING>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<MORE_DETAILED_CAPTION + GROUNDING>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<OD>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<DENSE_REGION_CAPTION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<REGION_PROPOSAL>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<CAPTION_TO_PHRASE_GROUNDING>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<REFERRING_EXPRESSION_SEGMENTATION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        output_image = copy.deepcopy(image)
        output_image = draw_polygons(output_image, results[task_prompt], fill_mask=True)
        return results, output_image
    elif task_prompt == "<REGION_TO_SEGMENTATION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        output_image = copy.deepcopy(image)
        output_image = draw_polygons(output_image, results[task_prompt], fill_mask=True)
        return results, output_image
    elif task_prompt == "<OPEN_VOCABULARY_DETECTION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        fig = plot_bbox(image, results[task_prompt])
        return results, fig_to_pil(fig)
    elif task_prompt == "<REGION_TO_CATEGORY>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        return results, None
    elif task_prompt == "<REGION_TO_DESCRIPTION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        return results, None
    elif task_prompt == "<OCR>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        return results, None
    elif task_prompt == "<OCR_WITH_REGION>":
        results = run_example(task_prompt, image, vision_model, vision_processor)
        output_image = copy.deepcopy(image)
        output_image = draw_ocr_bboxes(output_image, results[task_prompt])
        return results, output_image
    else:
        raise ValueError("Invalid task prompt")


def run_example(task_prompt, image, vision_model, vision_processor):
    # if text_input is None:
    prompt = task_prompt
    # else:
    #     prompt = task_prompt + text_input
    inputs = vision_processor(text=prompt, images=image, return_tensors="pt").to("cuda")
    generated_ids = vision_model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        early_stopping=False,
        do_sample=False,
        num_beams=3,
    )
    generated_text = vision_processor.batch_decode(
        generated_ids, skip_special_tokens=False
    )[0]
    parsed_answer = vision_processor.post_process_generation(
        generated_text, task=task_prompt, image_size=(image.width, image.height)
    )
    return parsed_answer
