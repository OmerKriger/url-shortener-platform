import redis.asyncio as redis

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

async def cache_short_url(long_url: str, short_url: str):
    try:
        await redis_client.set(short_url, long_url)
        print(f"✅ Redis saved: {short_url} -> {long_url}")
    except Exception as e:
        print(f"❌ Redis save failed: {e}")

async def get_cached_original_code(short_code: str) -> str | None:
    try:
        result = await redis_client.get(short_code)
        if result:
            print(f"📥 Redis hit: {short_code} -> {result}")
        return result
    except Exception as e:
        print(f"❌ Redis fetch failed: {e}")
        return None