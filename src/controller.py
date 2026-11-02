"""
This module contains the FastAPI application and the endpoints for the floor generation.
"""

import secrets

from fastapi import FastAPI, Path
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from utils import globals as my_globals
from generators.generator import Generator

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
_FILE_NAME = my_globals.DEFAULT_FLOOR_NAME + my_globals.JSON_SUFFIX
_CONTENT_DISPOSITION = f'attachment; filename="{_FILE_NAME}"'
_ROOT = "/"
_GENERATE = "/gen"


def _generate_floor_response(seed: str, floor_id: int) -> Response:
    """
    Generates a floor and returns it as a json file without writing it to disk.
    @param seed: seed for the floor
    @param floor_id: id for the floor
    @return: Floor as json file
    """
    generator = Generator(seed=seed, output_file_name=_FILE_NAME, stage_id=floor_id)
    generator.generate()
    return Response(
        content=generator.to_json(1),
        media_type="application/json",
        headers={"Content-Disposition": _CONTENT_DISPOSITION},
    )


@app.get(_ROOT)
async def root():
    """This endpoint returns a test message."""
    return {"message": "Test"}


@app.get(_GENERATE + "/{floor_id}")
def generate_with_id(floor_id: int = Path(ge=0)) -> Response:
    """
    This endpoint generates a floor with the given id
    and returns it as a json file.
    @param floor_id id for the floor
    @return: Floor in json file
    """
    return _generate_floor_response(secrets.token_hex(16), floor_id)


@app.get(_GENERATE + "/{floor_id}/{seed}")
def generate_with_id_and_seed(
    floor_id: int = Path(ge=0), seed: str = Path()
) -> Response:
    """
    This endpoint generates a floor with the given id
    and seed and returns it as a json file.
    @param floor_id: id for the floor
    @param seed: seed for the floor
    @return: Floor in json file
    """
    return _generate_floor_response(seed, floor_id)


@app.get(_GENERATE)
def generate() -> Response:
    """
    This endpoint generates a floor with the id zero and returns it as a json file.
    @return: Floor as json file
    """
    return _generate_floor_response(secrets.token_hex(16), 0)
