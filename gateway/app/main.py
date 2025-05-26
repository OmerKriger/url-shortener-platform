from fastapi import FastAPI, Request
import httpx
from starlette.responses import Response
from starlette.status import HTTP_502_BAD_GATEWAY

app = FastAPI()

SHORTENER_URL = "http://shortener:8000"
REDIRECTOR_URL = "http://redirector:8000"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(path: str, request: Request):
    try:
        method = request.method
        incoming_url = f"/{path}"

        print(f"\n🔵 Gateway received request: {method} {incoming_url}")

        if method == "POST" and path == "shorten":
            target_service_url = f"{SHORTENER_URL}/{path}"
            print("➡️ Forwarding to SHORTENER service")
        else:
            target_service_url = f"{REDIRECTOR_URL}/{path}"
            print("➡️ Forwarding to REDIRECTOR service")

        async with httpx.AsyncClient() as client:
            body = await request.body()
            headers = dict(request.headers)

            print(f"📤 Request body: {body.decode('utf-8') if body else '[Empty]'}")
            print(f"📤 Request headers: {headers}")

            proxy_req = client.build_request(
                method,
                target_service_url,
                headers=headers,
                content=body
            )

            proxy_res = await client.send(proxy_req, stream=True)

            print(f"✅ Response status: {proxy_res.status_code}")

            # טיפול מיוחד להפניות HTTP (3xx)
            if proxy_res.status_code in (301, 302, 303, 307, 308):
                redirect_headers = {}
                if "location" in proxy_res.headers:
                    redirect_headers["location"] = proxy_res.headers["location"]
                return Response(
                    status_code=proxy_res.status_code,
                    headers=redirect_headers
                )

            # טעינת התוכן המלא של התגובה
            content = await proxy_res.aread()

            # החזרת התגובה ללקוח כולל תוכן, סטטוס וכותרות
            return Response(
                content=content,
                status_code=proxy_res.status_code,
                headers=dict(proxy_res.headers)
            )

    except Exception as e:
        print(f"❌ Gateway error: {str(e)}")
        return Response(content="Gateway Error", status_code=HTTP_502_BAD_GATEWAY)
