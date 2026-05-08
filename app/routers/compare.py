import json
import os
from pathlib import Path

import cv2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import compare_service, diff_service, align_service, region_service, pdf_service
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

        meta = json.loads((out_dir / "meta.json").read_text())

        if meta["file_type_a"] == "pdf":
            if req.page_a >= meta["page_count_a"]:
                raise HTTPException(status_code=400, detail="A 頁碼超出範圍")
            img_a = pdf_service.pdf_page_to_image(out_dir / "a.pdf", req.page_a)
        else:
            img_a = image_io.load_image(out_dir / "a.png")

        if meta["file_type_b"] == "pdf":
            if req.page_b >= meta["page_count_b"]:
                raise HTTPException(status_code=400, detail="B 頁碼超出範圍")
            img_b = pdf_service.pdf_page_to_image(out_dir / "b.pdf", req.page_b)
        else:
            img_b = image_io.load_image(out_dir / "b.png")

        gray_a = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
        gray_b = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)

        if gray_b.shape != gray_a.shape:
            img_b  = cv2.resize(img_b,  (img_a.shape[1], img_a.shape[0]))
            gray_b = cv2.resize(gray_b, (gray_a.shape[1], gray_a.shape[0]))

        img_b_aligned, aligned = align_service.align_images(img_a, img_b)
        gray_b_aligned = cv2.cvtColor(img_b_aligned, cv2.COLOR_BGR2GRAY)

        similarity = compare_service.compute_ssim(gray_a, gray_b_aligned)
        diff_result = diff_service.generate_diff(img_a, gray_a, gray_b_aligned, out_dir)

        regions = region_service.classify_regions(diff_result["contours"])
        (out_dir / "report.json").write_text(
            json.dumps([r.dict() for r in regions], ensure_ascii=False)
        )

        return {
            "comparison_id": req.comparison_id,
            "similarity": similarity,
            "annotated_image_url": f"/temp/{req.comparison_id}/annotated.png",
            "aligned": aligned,
            "regions": [r.dict() for r in regions],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
