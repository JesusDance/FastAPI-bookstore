import httpx
from fastapi import HTTPException
from starlette.requests import Request

from app.logger import logger


def get_httpx_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.httpx_client


class BookClient:
    def __init__(self, url: str, client: httpx.AsyncClient):
        self.url = url
        self.client = client

    async def fetch_book_from_api(self, title: str):
        logger.info("Fetching book from external API", extra={"title": title})

        try:
            response = await self.client.get(self.url + title, timeout=10)
            response.raise_for_status()
            docs = response.json().get("docs", [])
            if not docs:
                logger.warning("Book not found in external API", extra={"title": title})
                raise HTTPException(404, "Book not found in external API")
            title, author = (
                docs[0].get("title", "Unknown"),
                docs[0].get("author_name", "Unknown")[0],
            )
            if not title or not author:
                logger.warning("Invalid response from API", extra={"title": title})
                raise HTTPException(404, "Invalid response from API")
            return title, author
        except httpx.TimeoutException:
            logger.warning("External API timeout", extra={"title": title})
            raise HTTPException(504, "External API timeout")
        except httpx.ConnectError:
            logger.warning("Max size of pools", extra={"title": title})
            raise HTTPException(429, "Max size of pools")
        except httpx.RequestError:
            logger.warning("Book not found in external API", extra={"title": title})
            raise HTTPException(404, "Book not found in external API")
