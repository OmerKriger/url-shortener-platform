from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
import shortuuid
import re

from infrastructure.cache import get_cached_original_code, cache_short_url
from infrastructure.db import connect_db, disconnect_db, save_url_mapping, get_long_url

app = FastAPI()
ALIAS_PATTERN = re.compile(r'^[a-zA-Z0-9\-]{6,30}$')

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

class URLRequest(BaseModel):
    url: str
    alias: Optional[str] = None

def generate_short_code(length=6):
    short_code = shortuuid.ShortUUID().random(length=length)
    return short_code

def validate_url_alias(alias: str) -> bool:
    return ALIAS_PATTERN.match(alias) is not None

@app.post("/shorten")
async def create_short_url(data: URLRequest):
    full_url = data.url
    alias = data.alias

    print(f"\n🔗 Request to shorten: {full_url}")

    if alias:
        print(f"🔍 Requested custom alias: {alias}")

        if not validate_url_alias(alias):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="Invalid custom alias format, Must be 6-30 characters long and contain only letters, numbers"
                )
        
        # Check if alias is already taken
        if await get_long_url(alias) or await get_cached_original_code(alias):
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Custom alias is already taken"
                )
        
        short_url = alias
    else:
        # Attempt to find a unique short URL
        while True:
            short_url = generate_short_code()
            print(f"🔍 Trying short URL: {short_url}")

            # Step #3 - Check Redis
            if await get_cached_original_code(short_url):
                print("⚠️ Short URL exists in cache. Retrying...")
                continue

            # Step #4 - Check DB
            if await get_long_url(short_url):
                print("⚠️ Short URL exists in DB. Retrying...")
                continue

            break  # Short URL is unique

    try:
        await save_url_mapping(short_code=short_url, long_url=full_url)
        print(f"✅ Inserted into DB: {short_url} -> {full_url}")

        await cache_short_url(short_url=short_url,
                              long_url=full_url)
        print(f"🧠 Cached: {short_url} -> {full_url}")

        return {
            "short_url": f"http://localhost:8000/{short_url}", # TODO: Change address to dynamic
            "original_url": full_url,
            "alias": short_url
            } 

    except Exception as e:
        print(f"❌ Error during insert: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal Server Error"
            )