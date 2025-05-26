from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

app = FastAPI()

url_map = {
    "abc123": "https://www.linkedin.com/in/omer-kriger",
    "xyz789": "https://www.github.com/OmerKriger"
}


def normalize_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url
    return url

@app.get("/{short_code}")
async def redirect(short_code: str):
    raw_url = url_map.get(short_code)
    if not raw_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=normalize_url(raw_url), status_code=307)