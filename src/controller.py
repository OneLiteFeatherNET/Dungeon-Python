"""
This module contains the FastAPI application and the endpoints for the floor generation.
"""
import secrets

from fastapi import FastAPI, Path
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from utils import globals as my_globals
from generators.generator import Generator

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_FILE_NAME = my_globals.DEFAULT_FLOOR_NAME + my_globals.JSON_SUFFIX
_ROOT = "/"
_GENERATE = "/gen"


@app.get(_ROOT)
async def root():
    """This endpoint returns a test message."""
    return {"message": "Test"}


@app.get(_GENERATE + "/{floor_id}")
async def generate_with_id(floor_id: int = Path(ge=0)) -> FileResponse:
    """
    This endpoint generates a floor with the given id
    and returns it in a FileResponse as a json file.
    @param floor_id id for the floor
    @return: Floor in json file
    """
    generator = Generator(
        seed=secrets.token_hex(16), output_file_name=_FILE_NAME, stage_id=floor_id
    )
    generator.generate()
    path = generator.save()
    return FileResponse(path=path, filename=_FILE_NAME)


@app.get(_GENERATE + "/{floor_id}/{seed}")
async def generate_with_id_and_seed(
    floor_id: int = Path(ge=0), seed: str = Path()
) -> FileResponse:
    """
    This endpoint generates a floor with the given id
    and seed and returns it in a FileResponse as a json file.
    @param floor_id: id for the floor
    @param seed: seed for the floor
    @return: Floor in json file
    """
    generator = Generator(seed=seed, output_file_name=_FILE_NAME, stage_id=floor_id)
    generator.generate()
    path = generator.save()
    return FileResponse(path=path, filename=_FILE_NAME)


@app.get(_GENERATE)
async def generate() -> FileResponse:
    """
    This endpoint generates a floor with the id zero and returns it as a json file.
    @return: Floor as json file
    """
    generator = Generator(
        seed=secrets.token_hex(16), output_file_name=_FILE_NAME, stage_id=0
    )
    generator.generate()
    path = generator.save()
    return FileResponse(path=path, filename=_FILE_NAME)
