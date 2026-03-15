from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import shutil
import uuid

from GroqLLM import get_review

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    temp_name = f"temp_{uuid.uuid4()}.pdf"

    with open(temp_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result_file = get_review(temp_name)

    return FileResponse(
        result_file,
        filename="review.md",
        media_type="application/octet-stream"
    )