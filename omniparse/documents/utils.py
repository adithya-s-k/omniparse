import os
import torch
import base64
from omniparse.documents.settings import settings


def flush_cuda_memory():
    if settings.TORCH_DEVICE_MODEL == "cuda":
        torch.cuda.empty_cache()
