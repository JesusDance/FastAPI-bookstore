import httpx
import logging
from fastapi import HTTPException

# logging.basicConfig(
#     format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.DEBUG
# )
# httpx.get("")


class BookClient:
    def __init__(self, url: str):
        self.url = url

    async def fetch_book_from_api(self, title: str):
        try:
            async with httpx.AsyncClient(http2=True) as client:
                response = await client.get(self.url + title, timeout=10)
                response.raise_for_status()
                docs = response.json().get("docs")
                title, author = (
                    docs[0].get("title", "Unknown"),
                    docs[0].get("author_name", "Unknown")[0],
                )
            if not title or not author:
                raise HTTPException(404, "Invalid response from API")
            return title, author
        except httpx.TimeoutException:
            raise HTTPException(504, "External API timeout")
        except httpx.RequestError:
            raise HTTPException(404, "Book not found in external API")
