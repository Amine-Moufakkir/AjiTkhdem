import httpx



#! dans cette methode on utilse pas les proxies
def get_request(url: str, proxy: dict, user_agent: str):
    headers = {"User-Agent": user_agent}
    # proxy_url = proxy.get("https")

    try:
        with httpx.Client(headers=headers, timeout=10.0) as client:
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