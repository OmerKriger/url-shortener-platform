from databases import Database
from asyncio import sleep as asyncio_sleep
DATABASE_URL = "postgresql://url_user:url_pass@postgres:5432/url_db" #TODO: Change it to be dynamic

database = Database(DATABASE_URL)

async def connect_db():
    print("🔵 Connecting to database...")
    await connect_db_with_retry(database)
    print("✅ Database connected")

async def disconnect_db():
    print("🔵 Disconnecting from database...")
    await database.disconnect()
    print("✅ Database disconnected")

async def save_url_mapping(short_code: str, long_url: str):
    query = """
    INSERT INTO url_mappings (short_code, long_url)
    VALUES (:short_code, :long_url)
    """
    await database.execute(query, {"short_code": short_code, "long_url": long_url})

async def get_long_url(short_code: str) -> str | None:
    query = "SELECT long_url FROM url_mappings WHERE short_code = :short_code"
    result = await database.fetch_one(query, {"short_code": short_code})
    if result:
        return result["long_url"]
    return None

async def connect_db_with_retry(database, retries=5, delay=2):
    for attempt in range(retries):
        try:
            await database.connect()
            print("Connected to DB")
            return
        except Exception as e:
            print(f"DB connection failed (attempt {attempt+1}/{retries}): {e}")
            await asyncio_sleep(delay)
    raise Exception("Failed to connect to DB after retries")