from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from api.mypage import router as mypage_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.include_router(mypage_router, prefix="/api", tags=["mypage"])

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/mypage", response_class=HTMLResponse)
def mypage_view(request: Request):
    return templates.TemplateResponse("mypage.html", {"request": request})

# 실행: uvicorn main:app --reload
