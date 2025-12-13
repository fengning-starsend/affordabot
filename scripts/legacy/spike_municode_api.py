import httpx
import asyncio
import json

# Known San Jose URL: https://library.municode.com/ca/san_jose/codes/code_of_ordinances

async def probe_municode_config():
    """
    Attempt to find the Client ID for San Jose by checking the config endpoint 
    that the SPA likely hits.
    
    Based on network inspection of Municode:
    - It often requests `https://api.municodeweb.com/api/config/n/clients` or similar.
    - Or `https://library.municode.com/ca/san_jose` might contain pre-hydrated state.
    """
    
    # Let's try to fetch the main library page and regex for client ID
    url = "https://library.municode.com/ca/san_jose/codes/code_of_ordinances"
    print(f"Fetching {url}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch page: {resp.status_code}")
            return

        content = resp.text
        # Look for typical config patterns
        # Usually looking for "clientId" or "client_id"
        print(f"Page length: {len(content)}")
        
        # Try to guess API calls.
        # Often: GET https://api.municodeweb.com/api/v2/clients/{client_id}/products/{product_id}/
        
        # Let's try searching for "san_jose" in the client list API if possible.
        # But `library.municode.com` is an SPA.
        
        # Another approach: Municode often uses an initialization config in a script tag.
        import re
        client_id_match = re.search(r'clientId["\']\s*:\s*["\'](\d+)["\']', content)
        if client_id_match:
            print(f"Found Client ID via regex: {client_id_match.group(1)}")
        else:
            print("No Client ID found via regex.")
            
        product_id_match = re.search(r'productId["\']\s*:\s*["\'](\d+)["\']', content)
        if product_id_match:
            print(f"Found Product ID via regex: {product_id_match.group(1)}")

async def main():
    await probe_municode_config()

if __name__ == "__main__":
    asyncio.run(main())
