import os
import aiofiles
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from app.states import RideOfferState
from app.handlers.menu import api_client, get_main_menu_kb
from app.keyboards import get_cancel_kb
from app.utils.formatting import parse_date, parse_time, format_date, format_time

router = Router()

@router.message(F.text == "I am a Driver 🚗")
async def start_driver_flow(message: types.Message, state: FSMContext):
    await message.answer("Please enter your Start Location (e.g. Naryn):", reply_markup=get_cancel_kb())
    await state.set_state(RideOfferState.START_LOC)

@router.message(RideOfferState.START_LOC)
async def process_start_loc(message: types.Message, state: FSMContext):
    await state.update_data(start_location=message.text)
    await message.answer("Please enter your Destination (e.g. Bishkek):")
    await state.set_state(RideOfferState.END_LOC)

@router.message(RideOfferState.END_LOC)
async def process_end_loc(message: types.Message, state: FSMContext):
    await state.update_data(end_location=message.text)
    await message.answer("Please enter travel Date (DD.MM.YYYY):")
    await state.set_state(RideOfferState.DATE)

@router.message(RideOfferState.DATE)
async def process_date(message: types.Message, state: FSMContext):
    try:
        d = parse_date(message.text)
        await state.update_data(travel_start_date=d.isoformat())
        await message.answer("Please enter travel Time (HH:MM):")
        await state.set_state(RideOfferState.TIME)
    except ValueError:
        await message.answer("Invalid date format. Please use DD.MM.YYYY")

@router.message(RideOfferState.TIME)
async def process_time(message: types.Message, state: FSMContext):
    try:
        t = parse_time(message.text)
        await state.update_data(travel_start_time=t.isoformat(), time_iso=t.isoformat())
        await message.answer("How many seats are available?")
        await state.set_state(RideOfferState.SEATS)
    except ValueError:
        await message.answer("Invalid time format. Please use HH:MM")

@router.message(RideOfferState.SEATS)
async def process_seats(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a valid number.")
        return
    seats = int(message.text)
    await state.update_data(total_seat_amount=seats, free_seats=seats)
    await message.answer("What is your Car Model?")
    await state.set_state(RideOfferState.CAR_MODEL)

@router.message(RideOfferState.CAR_MODEL)
async def process_car(message: types.Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await message.answer("Please upload a photo of your car (or type 'skip' if not available now).")
    await state.set_state(RideOfferState.PHOTO)

@router.message(RideOfferState.PHOTO, F.photo)
async def process_photo(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    driver_id = user_data.get("user_id") # We need this from session
    
    # 1. Create Offer First (if not created yet? or create after?)
    # The flow says: 1-3 pictures.
    # To simplify MVP: Create offer first, then upload photo to driver? 
    # Or create offer then attach photo? 
    # Schema `CarPhoto` is linked to `Driver` (User), not `RideOffer`.
    # So we can upload photo to Driver profile.
    
    # Let's create offer now.
    offer_data = {
        "travel_start_date": user_data["travel_start_date"],
        "travel_start_time": user_data["travel_start_time"],
        "start_location": user_data["start_location"],
        "end_location": user_data["end_location"],
        "request_source": "telegram_app",
        "car_model": user_data["car_model"],
        "total_seat_amount": user_data["total_seat_amount"],
        "free_seats": user_data["free_seats"]
    }
    
    try:
        # We need check if user_id is in state. 
        # If flow started from Menu, we might have it. 
        # But wait, Registration clears state. Menu set it.
        if not driver_id:
             # Try fallback to recover from API using tg ID?
             tg_user = await api_client.get_telegram_user(message.from_user.id)
             if tg_user:
                 driver_id = tg_user["user_id"]
             else:
                 await message.answer("Error: User not found. Please /start again.")
                 return

        await api_client.create_ride_offer(driver_id, offer_data)

        # 2. Upload Photo
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        # Download
        file_content = await bot.download_file(file_info.file_path)
        
        # Upload
        # file_content is BytesIO, read bytes
        if hasattr(file_content, 'read'):
             content = file_content.read()
        else:
             content = file_content # already bytes? check aiogram docs. typically it returns BytesIO or similar.

        # aiogram 3 bot.download_file returns io.BytesIO
        if hasattr(file_content, 'getvalue'):
            content = file_content.getvalue()

        await api_client.upload_car_photo(driver_id, content, f"car_{driver_id}.jpg")
        
        await message.answer("Ride Offer Published! 🚀\nSearching for passengers...", reply_markup=get_main_menu_kb())
        await state.clear()
        
        
    except Exception as e:
        await message.answer(f"Error publishing offer: {e}")

# Async matching removed (Moved to Celery)


@router.message(RideOfferState.PHOTO, F.text.lower() == "skip")
async def skip_photo(message: types.Message, state: FSMContext):
    # Same logic but no photo
    user_data = await state.get_data()
    driver_id = user_data.get("user_id")
    
    if not driver_id:
            tg_user = await api_client.get_telegram_user(message.from_user.id)
            if tg_user:
                driver_id = tg_user["user_id"]
            else:
                await message.answer("Error: User not found. Please /start again.")
                return

    offer_data = {
        "travel_start_date": user_data["travel_start_date"],
        "travel_start_time": user_data["travel_start_time"],
        "start_location": user_data["start_location"],
        "end_location": user_data["end_location"],
        "request_source": "telegram_app",
        "car_model": user_data["car_model"],
        "total_seat_amount": user_data["total_seat_amount"],
        "free_seats": user_data["free_seats"]
    }
    
    try:
        await api_client.create_ride_offer(driver_id, offer_data)
        await message.answer("Ride Offer Published (No photo)! 🚀\nSearching for passengers...", reply_markup=get_main_menu_kb())
        await state.clear()
        
        # Async Matching
        import asyncio
        asyncio.create_task(check_for_passengers(message, offer_data))

    except Exception as e:
        await message.answer(f"Error publishing offer: {e}")

