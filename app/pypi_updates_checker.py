import aiohttp

async def get_latest_version(library: str):
    url = f"https://pypi.org/pypi/{library}/json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["info"]["version"]
            return None
