import httpx


def get_request(url: str, proxy: dict | str | None, user_agent: str):
    headers = {"User-Agent": user_agent}
    
    # httpx expects proxy as a string or an httpx.Proxy instance.
    # Our proxy can be a dict: {"http": "...", "https": "..."} or a string.
    proxy_url = None
    if proxy:
        if isinstance(proxy, dict):
            # Try to get https first, then http
            proxy_url = proxy.get("https") or proxy.get("http")
        else:
            proxy_url = proxy

    try:
        with httpx.Client(headers=headers, proxy=proxy_url, timeout=15.0) as client:
            response = client.get(url)
            response.raise_for_status() 
            return response.text

    except httpx.HTTPStatusError as e:
        print(f"Server error {e.response.status_code} while fetching {url}")
    except httpx.RequestError as e:
        print(f"Connection error: {e} while fetching {url}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None