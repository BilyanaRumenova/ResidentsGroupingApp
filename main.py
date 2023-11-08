from pathlib import Path

from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from utils import process_data

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


@app.post("/process-data")
async def handle_data(csv_file: UploadFile = File(None), text_input: str = Form(None)):
    try:
        if csv_file:
            contents = await csv_file.read()
            processed_data = process_data(contents)
        else:
            processed_data = process_data(text_input)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"processed_data": processed_data})

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error processing data")
