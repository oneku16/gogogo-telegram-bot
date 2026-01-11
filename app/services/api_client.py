import httpx
from app.config import API_BASE_URL
from typing import Optional

class ApiClient:
    def __init__(self):
        self.base_url = API_BASE_URL

    async def create_user(self, phone_number: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> str:
        """
        Registers a user and returns the user_id (UUID).
        """
        async with httpx.AsyncClient() as client:
            payload = {
                "phone_number": phone_number,
                "first_name": first_name,
                "last_name": last_name
            }
            # The API spec expects UserCreate schema
            response = await client.post(f"{self.base_url}/users/", json=payload)
            response.raise_for_status()
            return response.json()["id"]

    async def link_telegram_user(self, telegram_id: int, user_id: str, username: Optional[str] = None, language_code: Optional[str] = None, language: Optional[str] = None):
        """
        Links a Telegram account to an existing user.
        """
        async with httpx.AsyncClient() as client:
            payload = {
                "telegram_id": telegram_id,
                "user_id": user_id,
                "username": username,
                "language_code": language_code,
                "language": language
            }
            response = await client.post(f"{self.base_url}/telegram/", json=payload)
            response.raise_for_status()
            return response.json()
    
    async def create_ride_offer(self, driver_id: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/offers",
                params={"driver_id": driver_id},
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def create_ride_request(self, passenger_id: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/requests",
                params={"passenger_id": passenger_id},
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def upload_car_photo(self, driver_id: str, file_content: bytes, filename: str) -> dict:
        async with httpx.AsyncClient() as client:
            files = {"file": (filename, file_content, "image/jpeg")}
            response = await client.post(
                f"{self.base_url}/drivers/{driver_id}/photos",
                files=files
            )
            response.raise_for_status()
            return response.json()

    async def search_ride_offers(self, start_location: str, end_location: str, seats_needed: int, start_time: str) -> list:
        async with httpx.AsyncClient() as client:
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
        async with httpx.AsyncClient() as client:
            params = {
                "start_location": start_location,
                "end_location": end_location,
                "start_time": start_time
            }
            response = await client.get(f"{self.base_url}/requests/search", params=params)
            response.raise_for_status()
            return response.json()

    async def get_telegram_user(self, telegram_id: int) -> Optional[dict]:
        """
        Gets Telegram user info by Telegram ID. Returns None if not found.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/telegram/{telegram_id}")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                return None


