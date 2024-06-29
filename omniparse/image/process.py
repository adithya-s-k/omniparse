
def pre_process_image(image, task_prompt, vision_model, vision_processor):
    # :Convert binary image data to PIL Image
    # image = Image.fromarray(image) 
    if task_prompt == 'Caption':
        task_prompt = '<CAPTION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Detailed Caption':
        task_prompt = '<DETAILED_CAPTION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'More Detailed Caption':
        task_prompt = '<MORE_DETAILED_CAPTION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Object Detection':
        task_prompt = '<OD>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Dense Region Caption':
        task_prompt = '<DENSE_REGION_CAPTION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Region Proposal':
        task_prompt = '<REGION_PROPOSAL>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Caption to Phrase Grounding':
        task_prompt = '<CAPTION_TO_PHRASE_GROUNDING>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Referring Expression Segmentation':
        task_prompt = '<REFERRING_EXPRESSION_SEGMENTATION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Region to Segmentation':
        task_prompt = '<REGION_TO_SEGMENTATION>'
        results = run_example(task_prompt, image,vision_model, vision_processor)
    elif task_prompt == 'Open Vocabulary Detection':
        task_prompt = '<OPEN_VOCABULARY_DETECTION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Region to Category':
        task_prompt = '<REGION_TO_CATEGORY>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'Region to Description':
        task_prompt = '<REGION_TO_DESCRIPTION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'OCR':
        task_prompt = '<OCR>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    elif task_prompt == 'OCR with Region':
        task_prompt = '<OCR_WITH_REGION>'
        results = run_example(task_prompt, image, vision_model, vision_processor)
    else:
        return {"error": "Invalid task prompt"}

    return results

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
    generated_text = vision_processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    parsed_answer = vision_processor.post_process_generation(
        generated_text,
        task=task_prompt,
        image_size=(image.width, image.height)
    )
    return parsed_answer
