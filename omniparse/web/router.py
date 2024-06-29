from fastapi import FastAPI, UploadFile, File, HTTPException , APIRouter,  status , Form
from fastapi.responses import JSONResponse
from omniparse import get_shared_state
from omniparse.web import parse_url


model_state = get_shared_state()
website_router = APIRouter()

# Website parsing endpoint
@website_router.post("/parse")
async def parse_website(url: str):
    try:
        result = await parse_url(url, model_state)
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@website_router.post("/crawl")
async def crawl_website(url: str):
    return {"Coming soon"}
    
    
@website_router.post("/search")
async def search_web(url: str , prompt: str):
    return {"Coming soon"}