import warnings
warnings.filterwarnings("ignore", category=UserWarning) # Filter torch pytree user warnings

import pypdfium2 as pdfium # Needs to be at the top to avoid warnings
from PIL import Image

from omniparse.documents.utils import flush_cuda_memory
from omniparse.documents.tables.table import format_tables
from omniparse.documents.debug.data import dump_bbox_debug_data
from omniparse.documents.layout.layout import surya_layout, annotate_block_types
from omniparse.documents.layout.order import surya_order, sort_blocks_in_reading_order
from omniparse.documents.ocr.lang import replace_langs_with_codes, validate_langs
from omniparse.documents.ocr.detection import surya_detection
from omniparse.documents.ocr.recognition import run_ocr
from omniparse.documents.pdf.extract_text import get_text_blocks
from omniparse.documents.cleaners.headers import filter_header_footer, filter_common_titles
from omniparse.documents.equations.equations import replace_equations
from omniparse.documents.pdf.utils import find_filetype
from omniparse.documents.postprocessors.editor import edit_full_text
from omniparse.documents.cleaners.code import identify_code_blocks, indent_blocks
from omniparse.documents.cleaners.bullets import replace_bullets
from omniparse.documents.cleaners.headings import split_heading_blocks
from omniparse.documents.cleaners.fontstyle import find_bold_italic
from omniparse.documents.postprocessors.markdown import merge_spans, merge_lines, get_full_text
from omniparse.documents.cleaners.text import cleanup_text
from omniparse.documents.images.extract import extract_images
from omniparse.documents.images.save import images_to_dict

from typing import List, Dict, Tuple, Optional
from omniparse.documents.settings import settings


def parse_single_image(
        image: Image.Image,
        model_lst: List,
        metadata: Optional[Dict] = None,
        langs: Optional[List[str]] = None,
        batch_multiplier: int = 1
) -> Tuple[str, Dict[str, Image.Image], Dict]:
    # Set language needed for OCR
    if langs is None:
        langs = [settings.DEFAULT_LANG]

    if metadata:
        langs = metadata.get("languages", langs)

    langs = replace_langs_with_codes(langs)
    validate_langs(langs)

    # Find the filetype

    # Setup output metadata
    out_meta = {
        "languages": langs,
    }

    texify_model, layout_model, order_model, edit_model, detection_model, ocr_model = model_lst

    # Identify text lines on pages
    text_line_prediction = surya_detection(image, detection_model, batch_multiplier=batch_multiplier)
    flush_cuda_memory()

    # OCR pages as needed
    pages, ocr_stats = run_ocr(image, langs, ocr_model, batch_multiplier=batch_multiplier)
    flush_cuda_memory()

    surya_layout(image, layout_model, batch_multiplier=batch_multiplier)
    flush_cuda_memory()

    # Find headers and footers
    bad_span_ids = filter_header_footer(pages)
    out_meta["block_stats"] = {"header_footer": len(bad_span_ids)}

    # Add block types in
    annotate_block_types(pages)

    # Dump debug data if flags are set
    dump_bbox_debug_data(image, pages)

    # Find reading order for blocks
    # Sort blocks by reading order
    surya_order(image, order_model, batch_multiplier=batch_multiplier)
    sort_blocks_in_reading_order(pages)
    flush_cuda_memory()

    # Fix code blocks
    code_block_count = identify_code_blocks(image)
    out_meta["block_stats"]["code"] = code_block_count
    indent_blocks(image)

    # Fix table blocks
    table_count = format_tables(image)
    out_meta["block_stats"]["table"] = table_count

    
    for block in image.blocks:
        block.filter_spans(bad_span_ids)
        block.filter_bad_span_types()

    filtered, eq_stats = replace_equations(
        image,
        texify_model,
        batch_multiplier=batch_multiplier
    )
    flush_cuda_memory()
    out_meta["block_stats"]["equations"] = eq_stats

    # Extract images and figures
    if settings.EXTRACT_IMAGES:
        extract_images(image, pages)

    # Split out headers
    split_heading_blocks(image)
    find_bold_italic(image)

    # Copy to avoid changing original data
    merged_lines = merge_spans(filtered)
    text_blocks = merge_lines(merged_lines)
    text_blocks = filter_common_titles(text_blocks)
    full_text = get_full_text(text_blocks)

    # Handle empty blocks being joined
    full_text = cleanup_text(full_text)

    # Replace bullet characters with a -
    full_text = replace_bullets(full_text)

    # Postprocess text with editor model
    full_text, edit_stats = edit_full_text(
        full_text,
        edit_model,
        batch_multiplier=batch_multiplier
    )
    flush_cuda_memory()
    out_meta["postprocess_stats"] = {"edit": edit_stats}
    doc_images = images_to_dict(pages)

    return full_text, doc_images, out_meta