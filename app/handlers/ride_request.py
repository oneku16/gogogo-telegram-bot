from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from app.states import RideRequestState
from app.handlers.menu import api_client, get_main_menu_kb
from app.keyboards import get_cancel_kb, get_common_locations_kb, get_dates_kb, get_seats_kb
from app.utils.formatting import parse_date, parse_time

router = Router()

@router.message(F.text == "I am a Passenger 🧍")
async def start_passenger_flow(message: types.Message, state: FSMContext):
    await message.answer("Please enter your Start Location (e.g. Naryn):", reply_markup=get_common_locations_kb())
    await state.set_state(RideRequestState.START_LOC)

@router.callback_query(RideRequestState.START_LOC, F.data.startswith("loc:"))
async def process_start_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.split(":")[1]
    await state.update_data(start_location=location)
    await callback.answer(f"Selected: {location}")
    await callback.message.answer(f"Start: {location}\n\nPlease enter your Destination (e.g. Bishkek):", reply_markup=get_common_locations_kb())
    await state.set_state(RideRequestState.END_LOC)

@router.message(RideRequestState.START_LOC)
async def process_start_loc(message: types.Message, state: FSMContext):
    await state.update_data(start_location=message.text)
    await message.answer("Please enter your Destination (e.g. Bishkek):", reply_markup=get_common_locations_kb())
    await state.set_state(RideRequestState.END_LOC)

@router.callback_query(RideRequestState.END_LOC, F.data.startswith("loc:"))
async def process_end_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.split(":")[1]
    await state.update_data(end_location=location)
    await callback.answer(f"Selected: {location}")
    await callback.message.answer(f"Destination: {location}\n\nPlease enter travel Date:", reply_markup=get_dates_kb())
    await state.set_state(RideRequestState.DATE)

@router.message(RideRequestState.END_LOC)
async def process_end_loc(message: types.Message, state: FSMContext):
    await state.update_data(end_location=message.text)
    await message.answer("Please enter travel Date (DD.MM.YYYY):", reply_markup=get_dates_kb())
    await state.set_state(RideRequestState.DATE)

@router.callback_query(RideRequestState.DATE, F.data.startswith("date:"))
async def process_date_callback(callback: types.CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":")[1]
    # format is DD.MM.YYYY from our helper
    # but we store ISO.
    # We should re-parse it just to be safe and consistent with logic
    try:
        d = parse_date(date_str) 
        await state.update_data(travel_start_date=d.isoformat())
        await callback.answer(f"Selected: {date_str}")
        await callback.message.answer(f"Date: {date_str}\n\nPlease enter travel Time (HH:MM):")
        await state.set_state(RideRequestState.TIME)
    except ValueError:
        await callback.answer("Error processing date")

@router.message(RideRequestState.DATE)
async def process_date(message: types.Message, state: FSMContext):
    try:
        d = parse_date(message.text)
        await state.update_data(travel_start_date=d.isoformat())
        await message.answer("Please enter travel Time (HH:MM):")
        await state.set_state(RideRequestState.TIME)
    except ValueError:
        await message.answer("Invalid date format. Please use DD.MM.YYYY", reply_markup=get_dates_kb())

@router.message(RideRequestState.TIME)
async def process_time(message: types.Message, state: FSMContext):
    try:
        t = parse_time(message.text)
        await state.update_data(travel_start_time=t.isoformat())
        await message.answer("How many seats do you need?", reply_markup=get_seats_kb())
        await state.set_state(RideRequestState.SEATS)
    except ValueError:
        await message.answer("Invalid time format. Please use HH:MM")

@router.callback_query(RideRequestState.SEATS, F.data.startswith("seats:"))
async def process_seats_callback(callback: types.CallbackQuery, state: FSMContext):
    seat_amount = callback.data.split(":")[1]
    await state.update_data(seat_amount=seat_amount)
    
    user_data = await state.get_data()
    
    # Show Summary
    summary = (
        f"🚕 <b>New Ride Request Summary</b>\n\n"
        f"📍 From: {user_data['start_location']}\n"
        f"📍 To: {user_data['end_location']}\n"
        f"📅 Date: {user_data['travel_start_date']}\n"
        f"⏰ Time: {user_data['travel_start_time']}\n"
        f"🪑 Seats: {seat_amount}\n\n"
        f"Is this correct?"
    )
    
    from app.keyboards import get_confirmation_kb
    await callback.answer(f"Selected: {seat_amount}")
    await callback.message.answer(summary, reply_markup=get_confirmation_kb(), parse_mode="HTML")
    await state.set_state(RideRequestState.CONFIRMATION)

@router.message(RideRequestState.SEATS)
async def process_seats(message: types.Message, state: FSMContext):
    seat_amount = message.text # String schema
    await state.update_data(seat_amount=seat_amount)
    
    user_data = await state.get_data()
    
    # Show Summary
    summary = (
        f"🚕 <b>New Ride Request Summary</b>\n\n"
        f"📍 From: {user_data['start_location']}\n"
        f"📍 To: {user_data['end_location']}\n"
        f"📅 Date: {user_data['travel_start_date']}\n"
        f"⏰ Time: {user_data['travel_start_time']}\n"
        f"🪑 Seats: {seat_amount}\n\n"
        f"Is this correct?"
    )
    
    from app.keyboards import get_confirmation_kb
    await message.answer(summary, reply_markup=get_confirmation_kb(), parse_mode="HTML")
    await state.set_state(RideRequestState.CONFIRMATION)


@router.message(RideRequestState.CONFIRMATION)
async def process_confirmation(message: types.Message, state: FSMContext, bot):
    if message.text == "Confirm ✅":
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
            "seat_amount": user_data.get("seat_amount")
        }
        
        try:
            await api_client.create_ride_request(passenger_id, request_data)
            await message.answer("Ride Request Published! 🚕\nSearching for drivers...", reply_markup=get_main_menu_kb())
            await state.clear()
            
        except Exception as e:
            await message.answer(f"Error publishing request: {e}")
            
    elif message.text == "Edit 📝":
        await message.answer("Okay, let's start over.", reply_markup=get_main_menu_kb())
        await state.clear()
    else:
        await message.answer("Please choose an option from the keyboard.")

# Async matching removed (Moved to Celery)
