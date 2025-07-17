from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pytz

from app.core.routes_data import daladala_routes
from app.services.sun_calc import calculate_bearing, get_sun_position, determine_best_side

app = FastAPI(title="Kwepajua: Sit Smart")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "routes": list(daladala_routes.keys())
    })

@app.post("/check-shade", response_class=HTMLResponse)
def check_shade(request: Request, route: str = Form(...), hour: int = Form(...), minute: int = Form(...)):
    route_data = daladala_routes.get(route)
    if not route_data:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Route not found"
        })

    # Create datetime object for Dar es Salaam timezone
    dar_tz = pytz.timezone("Africa/Dar_es_Salaam")
    now = datetime.now(dar_tz).replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    start, end = route_data["start"], route_data["end"]

    # Calculate travel direction
    bearing = calculate_bearing(start["lat"], start["lon"], end["lat"], end["lon"])
    
    # Get sun position using improved calculation
    sun_azimuth, sun_elevation = get_sun_position(now, start["lat"], start["lon"])
    
    # Determine best side to sit
    best_side = determine_best_side(bearing, sun_azimuth)
    
    # Check if it's daylight
    is_daylight = sun_elevation > 0
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "route": route,
        "bearing": round(bearing, 2),
        "sun_azimuth": round(sun_azimuth, 2),
        "sun_elevation": round(sun_elevation, 2),
        "recommendation": best_side,
        "time": now.strftime("%H:%M"),
        "is_daylight": is_daylight
    })