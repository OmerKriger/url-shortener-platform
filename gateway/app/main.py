from fastapi import FastAPI, Request
import httpx
from starlette.responses import Response
from starlette.status import (
    HTTP_502_BAD_GATEWAY,
    HTTP_301_MOVED_PERMANENTLY,
    HTTP_302_FOUND,
    HTTP_303_SEE_OTHER,
    HTTP_307_TEMPORARY_REDIRECT,
    HTTP_308_PERMANENT_REDIRECT,
)

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

        # Sending task to service by proxy request
        async with httpx.AsyncClient() as client:
            body = await request.body()  # Passing the body of original request
            headers = dict(request.headers)  # Passing the header of original request

            proxy_req = client.build_request(
                method,
                target_service_url,
                headers=headers,
                content=body
            )

            # Sends the request to the downstream service.
            proxy_res = await client.send(proxy_req, stream=True)

            print(f"✅ Target Service ({target_service_url}) response status: {proxy_res.status_code}")

            if proxy_res.status_code in (HTTP_301_MOVED_PERMANENTLY,
                                         HTTP_302_FOUND,
                                         HTTP_303_SEE_OTHER,    
                                         HTTP_307_TEMPORARY_REDIRECT,
                                         HTTP_308_PERMANENT_REDIRECT
                                         ):
                redirect_headers = {}
                if "location" in proxy_res.headers:
                    redirect_headers["location"] = proxy_res.headers["location"]
                return Response(
                    status_code=proxy_res.status_code,
                    headers=redirect_headers
                )

            content = await proxy_res.aread()

            return Response(
                content=content,
                status_code=proxy_res.status_code,
                headers=dict(proxy_res.headers)
            )

    except Exception as e:
        print(f"❌ Gateway error: {str(e)}")
        return Response(content="Gateway Error", status_code=HTTP_502_BAD_GATEWAY)
