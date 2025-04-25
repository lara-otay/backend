import httpx

async def send_structured_request(request_data: dict, base_url: str = "https://fakestoreapi.com") -> dict:
    # Extract request parts
    method = request_data.get("method", "").upper()
    path = request_data.get("url")  # path like "/products"
    headers = request_data.get("headers", {})
    body = request_data.get("body", {})

    # Basic validation
    if not method or not path:
        return {"error": "Request must include 'method' and 'url'"}

    # Build the full URL
    full_url = f"{base_url}{path}"

    try:
        # Send the HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=full_url,
                headers=headers,
                json=body
            )

        # Try to parse JSON response
        if "application/json" in response.headers.get("content-type", ""):
            return {
                "status_code": response.status_code,
                "response": response.json()
            }

        # Fallback for non-JSON response
        return {
            "status_code": response.status_code,
            "response": response.text
        }

    except Exception as e:
        return {"error": str(e)}
