from fastapi import FastAPI, UploadFile, File, HTTPException # type: ignore
import shutil
import os
from main import run_pipeline
from config import MAX_FILE_SIZE_BYTES
from logger import logger

app = FastAPI(title="AI Data Analysis Agent API")

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # File size validation
        if os.path.getsize(file_path) > MAX_FILE_SIZE_BYTES:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="File too large. Please upload under 5MB."
            )

        logger.info(f"Processing file: {file.filename}")

        result = run_pipeline(file_path)

        logger.info("Pipeline executed successfully")

        return result

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))