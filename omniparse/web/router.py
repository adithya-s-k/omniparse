from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from omniparse import get_shared_state
from omniparse.web import parse_url
from omniparse.models import responseDocument
# from omniparse.models import Document

model_state = get_shared_state()
website_router = APIRouter()


# Website parsing endpoint
@website_router.post("/parse")
async def parse_website(url: str):
    try:
        parse_web_result: responseDocument = await parse_url(url, model_state)

        return JSONResponse(content=parse_web_result.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@website_router.post("/crawl")
async def crawl_website(url: str):
    return {"Coming soon"}


@website_router.post("/search")
async def search_web(url: str, prompt: str):
    return {"Coming soon"}
