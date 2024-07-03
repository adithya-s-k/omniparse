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

import io
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def plot_bbox(image, data):
    fig, ax = plt.subplots()
    ax.imshow(image)
    for bbox, label in zip(data["bboxes"], data["labels"]):
        x1, y1, x2, y2 = bbox
        rect = patches.Rectangle(
            (x1, y1), x2 - x1, y2 - y1, linewidth=1, edgecolor="r", facecolor="none"
        )
        ax.add_patch(rect)
        plt.text(
            x1,
            y1,
            label,
            color="white",
            fontsize=8,
            bbox=dict(facecolor="red", alpha=0.5),
        )
    ax.axis("off")
    return fig


colormap = [
    "blue",
    "orange",
    "green",
    "purple",
    "brown",
    "pink",
    "gray",
    "olive",
    "cyan",
    "red",
    "lime",
    "indigo",
    "violet",
    "aqua",
    "magenta",
    "coral",
    "gold",
    "tan",
    "skyblue",
]


def draw_polygons(image, prediction, fill_mask=False):
    draw = ImageDraw.Draw(image)
    scale = 1
    for polygons, label in zip(prediction["polygons"], prediction["labels"]):
        color = random.choice(colormap)
        fill_color = random.choice(colormap) if fill_mask else None
        for _polygon in polygons:
            _polygon = np.array(_polygon).reshape(-1, 2)
            if len(_polygon) < 3:
                print("Invalid polygon:", _polygon)
                continue
            _polygon = (_polygon * scale).reshape(-1).tolist()
            if fill_mask:
                draw.polygon(_polygon, outline=color, fill=fill_color)
            else:
                draw.polygon(_polygon, outline=color)
            draw.text((_polygon[0] + 8, _polygon[1] + 2), label, fill=color)
    return image


def convert_to_od_format(data):
    bboxes = data.get("bboxes", [])
    labels = data.get("bboxes_labels", [])
    od_results = {"bboxes": bboxes, "labels": labels}
    return od_results


def draw_ocr_bboxes(image, prediction):
    scale = 1
    draw = ImageDraw.Draw(image)
    bboxes, labels = prediction["quad_boxes"], prediction["labels"]
    for box, label in zip(bboxes, labels):
        color = random.choice(colormap)
        new_box = (np.array(box) * scale).tolist()
        draw.polygon(new_box, width=3, outline=color)
        draw.text(
            (new_box[0] + 8, new_box[1] + 2),
            "{}".format(label),
            align="right",
            fill=color,
        )
    return image


def fig_to_pil(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return Image.open(buf)
