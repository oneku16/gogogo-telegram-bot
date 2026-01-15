import httpx
from loguru import logger
from app.config import API_BASE_URL
from typing import Optional

class ApiClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.client: Optional[httpx.AsyncClient] = None

    async def start(self):
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
            logger.info("ApiClient session started")

    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("ApiClient session closed")

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            # Lazy init if start() wasn't called (fallback)
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client

    async def create_user(self, phone_number: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> str:
        """
        Registers a user and returns the user_id (UUID).
        """
        client = await self._get_client()
        payload = {
            "phone_number": phone_number,
            "first_name": first_name,
            "last_name": last_name
        }
        # The API spec expects UserCreate schema
        response = await client.post(f"{self.base_url}/users/", json=payload)
        response.raise_for_status()
        return response.json()["id"]

    async def update_telegram_user(self, telegram_id: int, **kwargs) -> dict:
        client = await self._get_client()
        response = await client.patch(
            f"{self.base_url}/telegram/{telegram_id}",
            json=kwargs
        )
        response.raise_for_status()
        return response.json()

    # Generic alias/wrapper if needed to maintain backward compat or just replace usage
    async def update_user_role(self, telegram_id: int, role: str) -> dict:
        return await self.update_telegram_user(telegram_id, role=role)

    async def link_telegram_user(
        self,
        telegram_id: int,
        user_id: str,
        chat_id: int,
        username: Optional[str] = None,
        language_code: Optional[str] = None,
        language: Optional[str] = None,
        role: Optional[str] = None
    ):
        """Link a Telegram user to an existing backend user."""
        client = await self._get_client()
        payload = {
            "telegram_id": telegram_id,
            "user_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "language_code": language_code,
            "language": language,
            "role": role
        }
        response = await client.post(f"{self.base_url}/telegram/", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def create_ride_offer(self, driver_id: str, data: dict) -> dict:
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/offers",
            params={"driver_id": driver_id},
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def create_ride_request(self, passenger_id: str, data: dict) -> dict:
        client = await self._get_client()
        response = await client.post(
            f"{self.base_url}/requests",
            params={"passenger_id": passenger_id},
            json=data
        )
        response.raise_for_status()
        return response.json()

    async def upload_car_photo(self, driver_id: str, file_content: bytes, filename: str) -> dict:
        client = await self._get_client()
        files = {"file": (filename, file_content, "image/jpeg")}
        response = await client.post(
            f"{self.base_url}/drivers/{driver_id}/photos",
            files=files
        )
        response.raise_for_status()
        return response.json()

    async def search_ride_offers(self, start_location: str, end_location: str, seats_needed: int, start_time: str) -> list:
        client = await self._get_client()
        params = {
            "start_location": start_location,
            "end_location": end_location,
            "seats_needed": seats_needed,
            "start_time": start_time
        }
        response = await client.get(f"{self.base_url}/offers/search", params=params)
        response.raise_for_status()
        return response.json()

    async def search_ride_requests(self, start_location: str, end_location: str, start_time: str) -> list:
        client = await self._get_client()
        params = {
            "start_location": start_location,
            "end_location": end_location,
            "start_time": start_time
        }
        response = await client.get(f"{self.base_url}/requests/search", params=params)
        response.raise_for_status()
        return response.json()

    async def get_driver_offers(self, driver_id: str) -> list:
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/drivers/{driver_id}/offers")
        response.raise_for_status()
        return response.json()

    async def get_passenger_requests(self, passenger_id: str) -> list:
        client = await self._get_client()
        response = await client.get(f"{self.base_url}/passengers/{passenger_id}/requests")
        response.raise_for_status()
        return response.json()

    async def delete_ride_offer(self, offer_id: str, driver_id: str) -> None:
        client = await self._get_client()
        response = await client.delete(
            f"{self.base_url}/offers/{offer_id}",
            params={"driver_id": driver_id}
        )
        response.raise_for_status()

    async def delete_ride_request(self, request_id: str, passenger_id: str) -> None:
        client = await self._get_client()
        response = await client.delete(
            f"{self.base_url}/requests/{request_id}",
            params={"passenger_id": passenger_id}
        )
        response.raise_for_status()

    async def get_telegram_user(self, telegram_id: int) -> Optional[dict]:
        """
        Gets Telegram user info by Telegram ID. Returns None if not found.
        """
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/telegram/{telegram_id}")
            logger.debug(f"GET {self.base_url}/telegram/{telegram_id} -> {response.status_code}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            return None

# Global instance
api_client = ApiClient()


