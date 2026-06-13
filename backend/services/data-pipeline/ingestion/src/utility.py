import httpx


def get_request(url: str, proxy: dict, user_agent: str):
    headers = {"User-Agent": user_agent}
    
    # httpx expects proxy as a string or dict. 
    # Our proxy dict is {"http": "...", "https": "..."}
    proxies = None
    if proxy:
        proxies = proxy

    try:
        with httpx.Client(headers=headers, proxy=proxies, timeout=15.0) as client:
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