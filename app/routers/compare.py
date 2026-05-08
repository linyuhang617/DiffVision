import json
import os
from pathlib import Path

import cv2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import compare_service, diff_service
from app.utils import image_io

router = APIRouter()


class CompareRequest(BaseModel):
    comparison_id: str
    page_a: int = 0
    page_b: int = 0


@router.post("/compare")
async def compare(req: CompareRequest):
    try:
        temp_dir = Path(os.getenv("TEMP_DIR", "temp"))
        out_dir = temp_dir / req.comparison_id

        if not out_dir.exists():
            raise HTTPException(status_code=404, detail="找不到對應的比對資料")

        img_a = image_io.load_image(out_dir / "a.png")
        img_b = image_io.load_image(out_dir / "b.png")

        gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
        gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)

        if gray_b.shape != gray_a.shape:
            img_b  = cv2.resize(img_b,  (img_a.shape[1], img_a.shape[0]))
            gray_b = cv2.resize(gray_b, (gray_a.shape[1], gray_a.shape[0]))

        similarity = compare_service.compute_ssim(gray_a, gray_b)
        diff_result = diff_service.generate_diff(img_a, gray_a, gray_b, out_dir)

        return {
            "comparison_id": req.comparison_id,
            "similarity": similarity,
            "annotated_image_url": f"/temp/{req.comparison_id}/annotated.png",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
