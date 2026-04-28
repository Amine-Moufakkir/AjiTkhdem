import httpx

def get_request(url: str, proxy: dict, user_agent: str):
    headers = {"User-Agent": user_agent}
    try:
        with httpx.Client(proxies=proxy, headers=headers, timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status() 
            print(f"Successfully fetched {url} | Status: {response.status_code}")
            return response.text

    except httpx.HTTPStatusError as e:
        print(f"Server error {e.response.status_code} while fetching {url}")
    except httpx.RequestError as e:
        print(f"Connection error: {e} while fetching {url}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None