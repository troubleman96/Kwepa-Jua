from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pytz

from app.core.routes_data import daladala_routes, daladala_routes_by_corridor
from app.services.sun_calc import calculate_bearing, get_sun_position, determine_best_side
from app.services.language import language_service

app = FastAPI(title="Kwepajua: Sit Smart")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def show_form(request: Request, lang: str = Cookie(default="en")):
    translations = language_service.get_translations(lang)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "routes": list(daladala_routes.keys()),
        "routes_by_corridor": daladala_routes_by_corridor,
        "translations": translations,
        "current_lang": lang
    })

@app.post("/set-language")
def set_language(lang: str = Form(...)):
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="lang", value=lang, max_age=31536000)
    return response

@app.post("/calculate", response_class=HTMLResponse)
def calculate_shade(
    request: Request,
    route: str = Form(...),
    hour: int = Form(...),
    minute: int = Form(...),
    lang: str = Cookie(default="en")
):
    translations = language_service.get_translations(lang)
    
    if route not in daladala_routes:
        return templates.TemplateResponse("results.html", {
            "request": request,
            "error": "Route not found",
            "translations": translations,
            "current_lang": lang
        })
    
    bearing = calculate_bearing(daladala_routes[route])
    
    dar_tz = pytz.timezone('Africa/Dar_es_Salaam')
    current_date = datetime.now(dar_tz).date()
    now = dar_tz.localize(datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minute)))
    
    sun_azimuth, sun_elevation = get_sun_position(now)
    is_daylight = sun_elevation > 0
    
    print(f"Debug: Time={now}, Sun elevation={sun_elevation}, Is daylight={is_daylight}")
    
    best_side = determine_best_side(bearing, sun_azimuth, translations, lang) if is_daylight else None
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "route": route,
        "bearing": round(bearing, 2),
        "sun_azimuth": round(sun_azimuth, 2),
        "sun_elevation": round(sun_elevation, 2),
        "recommendation": best_side,
        "time": now.strftime("%H:%M"),
        "is_daylight": is_daylight,
        "translations": translations,
        "current_lang": lang
    })
