from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_307_TEMPORARY_REDIRECT, HTTP_404_NOT_FOUND

from infrastructure.cache import get_cached_original_code, cache_short_url
from infrastructure.db import connect_db, disconnect_db, get_long_url

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("🔵 Connecting to database...")
    await connect_db()
    print("✅ Database connected")

@app.on_event("shutdown")
async def shutdown():
    print("🔵 Disconnecting from database...")
    await disconnect_db()
    print("✅ Database disconnected")

def normalize_url(url: str) -> str:
    if not url.startswith("http://") and not url.startswith("https://"):
        return "https://" + url
    return url

@app.get("/{short_code}")
async def redirect(short_code: str):
    print(f"\n🔍 Lookup for short URL: {short_code}")
    # Step #1 - Try to find the long_url in cache (redis)
    cached_url = await get_cached_original_code(short_code)
    if cached_url:
        print(f"🟢 Cache hit for '{short_code}': {cached_url}")
        return RedirectResponse(url=normalize_url(cached_url), status_code=HTTP_307_TEMPORARY_REDIRECT)
    
    # Cache miss
    print(f"⚪ Cache miss for '{short_code}'. Querying database...")


    # Step #2 - Try to find the long_url in database(PostgreSQL)
    long_url = await get_long_url(short_code)
    if long_url:
        print(f"🟢 Found in DB: {long_url}. Setting cache...")
        # Store in cache for next time
        await cache_short_url(short_url=short_code,
                              long_url=long_url)
        return RedirectResponse(url=normalize_url(long_url), status_code=HTTP_307_TEMPORARY_REDIRECT)

    # Not found anywhere
    print(f"🔴 No matching URL found for '{short_code}'")
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Short URL not found")