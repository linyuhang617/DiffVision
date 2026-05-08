import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/download/{comparison_id}")
async def download(comparison_id: str, format: str):
    if format not in ("image", "json"):
        raise HTTPException(status_code=400, detail="format 必須是 image 或 json")

    temp_dir = Path(os.getenv("TEMP_DIR", "temp"))
    out_dir = temp_dir / comparison_id

    if not out_dir.exists():
        raise HTTPException(status_code=404, detail="找不到對應的比對資料")

    if format == "image":
        target = out_dir / "annotated.png"
        if not target.exists():
            raise HTTPException(status_code=404, detail="尚未產生標記圖，請先執行比對")
        return FileResponse(str(target), media_type="image/png", filename="diff.png")

    if format == "json":
        target = out_dir / "report.json"
        if not target.exists():
            raise HTTPException(status_code=404, detail="尚未產生報告，請先執行比對")
        return FileResponse(str(target), media_type="application/json", filename="diff-report.json")
