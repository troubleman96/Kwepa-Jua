# app/main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pytz

from app.core.routes_data import daladala_routes
from app.services.sun_calc import calculate_bearing, get_sun_azimuth, determine_best_side

app = FastAPI(title="Kwepajua: Sit Smart")

# Templates and static folders
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "routes": list(daladala_routes.keys()),
        "result": None
    })

@app.post("/", response_class=HTMLResponse)
def process_form(request: Request, route: str = Form(...), hour: int = Form(...), minute: int = Form(...)):
    route_data = daladala_routes.get(route)
    now = datetime.now(pytz.timezone("Africa/Dar_es_Salaam")).replace(hour=hour, minute=minute)

    start, end = route_data["start"], route_data["end"]
    bearing = calculate_bearing(start["lat"], start["lon"], end["lat"], end["lon"])
    sun_az = get_sun_azimuth(now, start["lat"], start["lon"])
    recommendation = determine_best_side(bearing, sun_az)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "routes": list(daladala_routes.keys()),
        "result": {
            "route": route,
            "bearing": round(bearing, 2),
            "sun_azimuth": round(sun_az, 2),
            "recommendation": recommendation,
            "time": now.strftime("%H:%M")
        }
    })
