from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import httpx

app = FastAPI(title="SmartTrip Tools", version="1.0")

@app.get("/fx-rate")
async def fx_rate(base: str, quote: str):
    url = f"https://api.exchangerate.host/convert?from={base}&to={quote}"
    async with httpx.AsyncClient() as c:
        rate = (await c.get(url)).json()["result"]
    return {"base": base, "quote": quote, "rate": rate}

@app.get("/scavenger-targets")
async def scavenger(lat: float, lon: float, radius_m: int = 2000):
    url = (
        "https://en.wikipedia.org/w/api.php"
        "?action=query&list=geosearch&format=json"
        f"&gscoord={lat}|{lon}&gsradius={radius_m}&gslimit=5"
    )
    async with httpx.AsyncClient() as c:
        data = (await c.get(url)).json()
    return {"targets": data["query"]["geosearch"][:5]}

class PackReq(BaseModel):
    destination: str
    activities: list[str]
    season: str | None = None
    lodging_amenities: list[str] | None = None

@app.post("/pack-list")
async def pack_list(req: PackReq):
    base = ["passport", "phone charger", "toiletries"]
    if "hike" in ",".join(req.activities).lower():
        base += ["trail shoes", "day-pack"]
    nice = ["hand warmers"] if (req.season or "").lower() == "winter" else []
    return {"necessary": base, "nice_to_have": nice}


PRIVACY_HTML = """
<!doctype html>
<title>Privacy Policy – Smart Trip Planner GPT</title>
<h1>Privacy Policy</h1>
<p>This demo API stores no personal data. Incoming requests are
processed in-memory and discarded after the response is returned.</p>
<p>No cookies, no analytics, no third-party tracking.</p>
<p>Contact: youremail@example.com</p>
"""

@app.get("/privacy", include_in_schema=False)
async def privacy():
    return HTMLResponse(PRIVACY_HTML)

