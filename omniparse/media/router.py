from fastapi import FastAPI, UploadFile, File, HTTPException , APIRouter,  status , Form
from fastapi.responses import JSONResponse
from omniparse.models import responseDocument
from omniparse.media import parse_audio , parse_video
from omniparse import get_shared_state

media_router = APIRouter()
model_state = get_shared_state()

@media_router.post("/audio")
async def parse_audio_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        result:responseDocument = parse_audio(file_bytes , model_state)
        return JSONResponse(content=result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@media_router.post("/video")
async def parse_video_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        result:responseDocument = parse_video(file_bytes , model_state)
        return JSONResponse(content=result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))