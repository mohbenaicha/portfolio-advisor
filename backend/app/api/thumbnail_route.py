from fastapi import APIRouter, Query
from app.services.article_utils import extract_thumbnail_image

router = APIRouter()

@router.get("/thumbnail")
def get_thumbnail(url: str = Query(...)):
    return extract_thumbnail_image(url) 