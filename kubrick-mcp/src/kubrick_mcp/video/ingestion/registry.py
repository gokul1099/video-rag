import json
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict

from loguru import logger
from . import contants as cc
from .models import CachedTable, CachedTableMetadata

logger = logger.bind(name="TableRegistry")

VIDEO_INDEXES_REGISTRY: Dict[str, CachedTableMetadata] = {}


@lru_cache
def get_registry() -> Dict[str, CachedTableMetadata]:
    """
    Get the global video index registry
    """

    global VIDEO_INDEXES_REGISTRY
    logger.info(f"viode_index_resitry {VIDEO_INDEXES_REGISTRY}")
    if not VIDEO_INDEXES_REGISTRY:
        try:
            registry_files= [
                f
                for f in os.listdir(cc.DEFAULT_CACHED_TABLES_REGISTRY_DIR)
                if f.startswith("registry_") and f.endswith(".json")
            ]
            logger.info(f"registry file {registry_files}")
            if registry_files:
                latest_file = max(registry_files)
                latest_registry = Path(cc.DEFAULT_CACHED_TABLES_REGISTRY_DIR) / latest_file
                with open(str(latest_registry), 'r') as f:
                    VIDEO_INDEXES_REGISTRY = json.load(f)
                    for key, value in VIDEO_INDEXES_REGISTRY.items():
                        if isinstance(value, str):
                            value = json.load(value)
                        VIDEO_INDEXES_REGISTRY[key] = CachedTableMetadata(**value)
                logger.info(f"Loading registry from {latest_registry}")
        except FileNotFoundError:
            logger.warning("Registry file not found. Returning empty registry")
    else:
        logger.info("Using existing video index registry")
    return VIDEO_INDEXES_REGISTRY


def add_index_to_registry(
        video_name:str,
        video_cache:str,
        frames_view_name: str,
        audio_view_name: str
):
    """
    Register a video index into the global registry
    """
    global VIDEO_INDEXES_REGISTRY
    cached_table_meta = CachedTableMetadata(
        video_name=video_name,
        video_cache=video_cache,
        video_table=f"{video_cache}.table",
        frames_view=frames_view_name,
        audio_chunks_view=audio_view_name
    ).model_dump_json()
    VIDEO_INDEXES_REGISTRY[video_name] = cached_table_meta

    dt = datetime.now()
    dtstr = dt.strftime("%Y-%m-%d%H:%M:%S")
    record_dir = Path(cc.DEFAULT_CACHED_TABLES_REGISTRY_DIR)
    record_dir.mkdir(parents=True, exist_ok=True)
    with open(record_dir / f"registry_{dtstr}.json","w") as f:
        for k,v in VIDEO_INDEXES_REGISTRY.items():
            if isinstance(v, CachedTableMetadata):
                v= v.model_dump_json()
            VIDEO_INDEXES_REGISTRY[k] = v
        json.dump(VIDEO_INDEXES_REGISTRY, f, indent=4)
    logger.info(f"Video index '{video_name}' registered in the global registry")


def get_table(video_name:str)-> Dict[str, CachedTable]:
    registry =get_registry()
    metadata = registry.get(video_name)
    if isinstance(metadata, str):
        metadata=json.load(metadata)
    logger.info(f"Metadata: {metadata}")
    return CachedTable.from_metadata(metadata)

