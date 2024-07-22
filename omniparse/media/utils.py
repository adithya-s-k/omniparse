"""
Title: OmniParse
Author: Adithya S K
Date: 2024-07-02

This code includes portions of code from the CLIP repository by OpenAI.
Original repository: https://github.com/openai/CLIP

Original Author: OpenAI
Original Date: 2021-01-05

License: MIT License
URL: https://github.com/openai/CLIP/blob/main/LICENSE

Description:
This section of the code was adapted from the CLIP repository to integrate audioprocessing capabilities into the OmniParse platform.
All credits for the original implementation go to OpenAI.
"""

import numpy as np


def transcribe(audio_path: str, whisper_model, **whisper_args):
    """Transcribe the audio file using whisper"""

    # Get whisper model
    # NOTE: If mulitple models are selected, this may keep all of them in memory depending on the cache size

    # Set configs & transcribe
    if whisper_args["temperature_increment_on_fallback"] is not None:
        whisper_args["temperature"] = tuple(
            np.arange(
                whisper_args["temperature"],
                1.0 + 1e-6,
                whisper_args["temperature_increment_on_fallback"],
            )
        )
    else:
        whisper_args["temperature"] = [whisper_args["temperature"]]

    del whisper_args["temperature_increment_on_fallback"]

    transcript = whisper_model.transcribe(
        audio_path,
        **whisper_args,
    )

    return transcript


# function for enabling CORS on web server
WHISPER_DEFAULT_SETTINGS = {
    "temperature": 0.0,
    "temperature_increment_on_fallback": 0.2,
    "no_speech_threshold": 0.6,
    "logprob_threshold": -1.0,
    "compression_ratio_threshold": 2.4,
    "condition_on_previous_text": True,
    "verbose": False,
    "task": "transcribe",
}
