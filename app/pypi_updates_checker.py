import aiohttp
import asyncio

async def get_latest_version(library: str):
    """Fetches the latest version of a package from PyPI."""
    url = f"https://pypi.org/pypi/{library}/json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {library: data["info"]["version"]}
            return {library: None}  # If the request fails

async def check_multiple_libraries(libraries: list):
    """Fetches the latest versions of multiple libraries in parallel."""
    tasks = [get_latest_version(lib) for lib in libraries]
    results = await asyncio.gather(*tasks)
    return {lib: version for result in results for lib, version in result.items()}