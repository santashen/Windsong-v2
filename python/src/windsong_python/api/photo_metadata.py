from fastapi import APIRouter

from windsong_python.models.photo_metadata import ParseRequest, ParseResponse
from windsong_python.services.photo_metadata import PhotoMetadataService

router = APIRouter()
photo_metadata_service = PhotoMetadataService()


@router.post("/photo-metadata/parse", response_model=ParseResponse)
async def parse_photo_metadata(payload: ParseRequest) -> ParseResponse:
    return await photo_metadata_service.parse(payload.content)
