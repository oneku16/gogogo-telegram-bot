from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from app.states import RideRequestState
from app.handlers.menu import api_client, get_main_menu_kb
from app.keyboards import get_cancel_kb
from app.utils.formatting import parse_date, parse_time

router = Router()

@router.message(F.text == "I am a Passenger 🧍")
async def start_passenger_flow(message: types.Message, state: FSMContext):
    await message.answer("Please enter your Start Location (e.g. Naryn):", reply_markup=get_cancel_kb())
    await state.set_state(RideRequestState.START_LOC)

@router.message(RideRequestState.START_LOC)
async def process_start_loc(message: types.Message, state: FSMContext):
    await state.update_data(start_location=message.text)
    await message.answer("Please enter your Destination (e.g. Bishkek):")
    await state.set_state(RideRequestState.END_LOC)

@router.message(RideRequestState.END_LOC)
async def process_end_loc(message: types.Message, state: FSMContext):
    await state.update_data(end_location=message.text)
    await message.answer("Please enter travel Date (DD.MM.YYYY):")
    await state.set_state(RideRequestState.DATE)

@router.message(RideRequestState.DATE)
async def process_date(message: types.Message, state: FSMContext):
    try:
        d = parse_date(message.text)
        await state.update_data(travel_start_date=d.isoformat())
        await message.answer("Please enter travel Time (HH:MM):")
        await state.set_state(RideRequestState.TIME)
    except ValueError:
        await message.answer("Invalid date format. Please use DD.MM.YYYY")

@router.message(RideRequestState.TIME)
async def process_time(message: types.Message, state: FSMContext):
    try:
        t = parse_time(message.text)
        await state.update_data(travel_start_time=t.isoformat())
        await message.answer("How many seats do you need (e.g. 1, 2)?")
        await state.set_state(RideRequestState.SEATS)
    except ValueError:
        await message.answer("Invalid time format. Please use HH:MM")

@router.message(RideRequestState.SEATS)
async def process_seats(message: types.Message, state: FSMContext):
    seat_amount = message.text # String schema
    
    user_data = await state.get_data()
    
    # Recover ID if missing
    passenger_id = user_data.get("user_id")
    if not passenger_id:
            tg_user = await api_client.get_telegram_user(message.from_user.id)
            if tg_user:
                passenger_id = tg_user["user_id"]
            else:
                await message.answer("Error: User not found. Please /start again.")
                return

    request_data = {
        "travel_start_date": user_data["travel_start_date"],
        "travel_start_time": user_data["travel_start_time"],
        "start_location": user_data["start_location"],
        "end_location": user_data["end_location"],
        "request_source": "telegram_app",
        "seat_amount": seat_amount
    }
    
    try:
        await api_client.create_ride_request(passenger_id, request_data)
        await message.answer("Ride Request Published! 🚕\nSearching for drivers...", reply_markup=get_main_menu_kb())
        await state.clear()
        
    except Exception as e:
        await message.answer(f"Error publishing request: {e}")

# Async matching removed (Moved to Celery)
