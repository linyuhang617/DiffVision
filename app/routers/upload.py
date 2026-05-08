import json
import os
import shutil
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, UploadFile

from app.utils.image_io import save_image

router = APIRouter()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _cleanup_old_temp(temp_dir: Path, retention_hours: float) -> None:
    if not temp_dir.exists():
        return
    cutoff = time.time() - retention_hours * 3600
    for entry in temp_dir.iterdir():
        if entry.is_dir() and entry.stat().st_mtime < cutoff:
            shutil.rmtree(entry, ignore_errors=True)


def _decode_upload(content: bytes) -> np.ndarray:
    arr = np.frombuffer(content, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode image data")
    return img


@router.post("/upload")
async def upload(file_a: UploadFile, file_b: UploadFile):
    try:
        max_mb = float(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
        temp_dir = Path(os.getenv("TEMP_DIR", "temp"))
        retention_hours = float(os.getenv("TEMP_RETENTION_HOURS", "1"))

        _cleanup_old_temp(temp_dir, retention_hours)

        for f in (file_a, file_b):
            if f.content_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(status_code=400, detail=f"不支援的檔案格式：{f.content_type}")

        content_a = await file_a.read()
        content_b = await file_b.read()

        limit = int(max_mb * 1024 * 1024)
        if len(content_a) > limit:
            raise HTTPException(status_code=413, detail="Image A 超過上限")
        if len(content_b) > limit:
            raise HTTPException(status_code=413, detail="Image B 超過上限")

        try:
            img_a = _decode_upload(content_a)
        except ValueError:
            raise HTTPException(status_code=400, detail="Image A 無法解析")
        try:
            img_b = _decode_upload(content_b)
        except ValueError:
            raise HTTPException(status_code=400, detail="Image B 無法解析")

        comparison_id = uuid.uuid4().hex
        out_dir = temp_dir / comparison_id
        out_dir.mkdir(parents=True, exist_ok=True)

        save_image(img_a, out_dir / "a.png")
        save_image(img_b, out_dir / "b.png")

        meta = {
            "file_type_a": "image",
            "file_type_b": "image",
            "page_count_a": None,
            "page_count_b": None,
        }
        (out_dir / "meta.json").write_text(json.dumps(meta))

        return {
            "comparison_id": comparison_id,
            "image_a_url": f"/temp/{comparison_id}/a.png",
            "image_b_url": f"/temp/{comparison_id}/b.png",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
