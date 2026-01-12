import os
from loguru import logger
import aiofiles
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from app.states import RideOfferState
from app.handlers.menu import api_client, get_main_menu_kb
from app.keyboards import get_cancel_kb, get_common_locations_kb, get_dates_kb, get_seats_kb
from app.utils.formatting import parse_date, parse_time, format_date, format_time

router = Router()

@router.message(F.text == "I am a Driver 🚗")
async def start_driver_flow(message: types.Message, state: FSMContext):
    await message.answer("Please enter your Start Location (e.g. Naryn):", reply_markup=get_common_locations_kb())
    await state.set_state(RideOfferState.START_LOC)

@router.callback_query(RideOfferState.START_LOC, F.data.startswith("loc:"))
async def process_start_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.split(":")[1]
    await state.update_data(start_location=location)
    await callback.answer(f"Selected: {location}")
    await callback.message.answer(f"Start: {location}\n\nPlease enter your Destination (e.g. Bishkek):", reply_markup=get_common_locations_kb())
    await state.set_state(RideOfferState.END_LOC)

@router.message(RideOfferState.START_LOC)
async def process_start_loc(message: types.Message, state: FSMContext):
    await state.update_data(start_location=message.text)
    await message.answer("Please enter your Destination (e.g. Bishkek):", reply_markup=get_common_locations_kb())
    await state.set_state(RideOfferState.END_LOC)

@router.callback_query(RideOfferState.END_LOC, F.data.startswith("loc:"))
async def process_end_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    location = callback.data.split(":")[1]
    await state.update_data(end_location=location)
    await callback.answer(f"Selected: {location}")
    await callback.message.answer(f"Destination: {location}\n\nPlease enter travel Date:", reply_markup=get_dates_kb())
    await state.set_state(RideOfferState.DATE)

@router.message(RideOfferState.END_LOC)
async def process_end_loc(message: types.Message, state: FSMContext):
    await state.update_data(end_location=message.text)
    await message.answer("Please enter travel Date (DD.MM.YYYY):", reply_markup=get_dates_kb())
    await state.set_state(RideOfferState.DATE)

@router.callback_query(RideOfferState.DATE, F.data.startswith("date:"))
async def process_date_callback(callback: types.CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":")[1]
    try:
        d = parse_date(date_str)
        await state.update_data(travel_start_date=d.isoformat())
        await callback.answer(f"Selected: {date_str}")
        await callback.message.answer(f"Date: {date_str}\n\nPlease enter travel Time (HH:MM):")
        await state.set_state(RideOfferState.TIME)
    except ValueError:
        await callback.answer("Error processing date")

@router.message(RideOfferState.DATE)
async def process_date(message: types.Message, state: FSMContext):
    try:
        d = parse_date(message.text)
        await state.update_data(travel_start_date=d.isoformat())
        await message.answer("Please enter travel Time (HH:MM):")
        await state.set_state(RideOfferState.TIME)
    except ValueError:
        await message.answer("Invalid date format. Please use DD.MM.YYYY", reply_markup=get_dates_kb())

@router.message(RideOfferState.TIME)
async def process_time(message: types.Message, state: FSMContext):
    try:
        t = parse_time(message.text)
        await state.update_data(travel_start_time=t.isoformat(), time_iso=t.isoformat())
        await message.answer("How many seats are available?", reply_markup=get_seats_kb())
        await state.set_state(RideOfferState.SEATS)
    except ValueError:
        await message.answer("Invalid time format. Please use HH:MM")

@router.callback_query(RideOfferState.SEATS, F.data.startswith("seats:"))
async def process_seats_callback(callback: types.CallbackQuery, state: FSMContext):
    seats = int(callback.data.split(":")[1])
    await state.update_data(total_seat_amount=seats, free_seats=seats)
    await callback.answer(f"Selected: {seats}")
    await callback.message.answer(f"Seats: {seats}\n\nWhat is your Car Model?")
    await state.set_state(RideOfferState.CAR_MODEL)

@router.message(RideOfferState.SEATS)
async def process_seats(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Please enter a valid number.", reply_markup=get_seats_kb())
        return
    seats = int(message.text)
    await state.update_data(total_seat_amount=seats, free_seats=seats)
    await message.answer("What is your Car Model?")
    await state.set_state(RideOfferState.CAR_MODEL)

@router.message(RideOfferState.CAR_MODEL)
async def process_car(message: types.Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await message.answer("What is the price per seat (in KGS)?")
    await state.set_state(RideOfferState.PRICE)

@router.message(RideOfferState.PRICE)
async def process_price(message: types.Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit():
        await message.answer("Please enter a valid number for price.")
        return
    
    price = int(message.text)
    await state.update_data(price=price)
    
    user_data = await state.get_data()
    driver_id = user_data.get("user_id")

    # Create Offer Data
    offer_data = {
        "travel_start_date": user_data["travel_start_date"],
        "travel_start_time": user_data["travel_start_time"],
        "start_location": user_data["start_location"],
        "end_location": user_data["end_location"],
        "request_source": "telegram_app",
        "car_model": user_data.get("car_model"),
        "total_seat_amount": user_data["total_seat_amount"],
        "free_seats": user_data["free_seats"],
        "price": price
    }
    
    # Show Summary
    summary = (
        f"🚗 <b>New Ride Offer Summary</b>\n\n"
        f"📍 From: {offer_data['start_location']}\n"
        f"📍 To: {offer_data['end_location']}\n"
        f"📅 Date: {offer_data['travel_start_date']}\n"
        f"⏰ Time: {offer_data['travel_start_time']}\n"
        f"🪑 Seats: {offer_data['free_seats']}\n"
        f"🚘 Car: {offer_data['car_model']}\n"
        f"💰 Price: {offer_data['price']} KGS\n\n"
        f"Is this correct?"
    )
    
    from app.keyboards import get_confirmation_kb
    await message.answer(summary, reply_markup=get_confirmation_kb(), parse_mode="HTML")
    await state.set_state(RideOfferState.CONFIRMATION)


@router.message(RideOfferState.CONFIRMATION)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text == "Confirm ✅":
        user_data = await state.get_data()
        driver_id = user_data.get("user_id")
        price = user_data.get("price")
        
        # Reconstruct offer_data from state
        offer_data = {
            "travel_start_date": user_data["travel_start_date"],
            "travel_start_time": user_data["travel_start_time"],
            "start_location": user_data["start_location"],
            "end_location": user_data["end_location"],
            "request_source": "telegram_app",
            "car_model": user_data.get("car_model"),
            "total_seat_amount": user_data["total_seat_amount"],
            "free_seats": user_data["free_seats"],
            "price": price
        }

        try:
            if not driver_id:
                logger.warning(f"driver_id lost, attempting recovery via API for tg_id: {message.from_user.id}")
                tg_user = await api_client.get_telegram_user(message.from_user.id)
                if tg_user:
                    driver_id = tg_user["user_id"]
                else:
                    await message.answer("Error: User not found. Please /start again.")
                    return

            await api_client.create_ride_offer(driver_id, offer_data)
            await message.answer("Ride Offer Published! 🚀", reply_markup=get_main_menu_kb())
            await state.clear()

        except Exception as e:
            await message.answer(f"Error publishing offer: {e}")
            
    elif message.text == "Edit 📝":
        await message.answer("Okay, let's start over.", reply_markup=get_main_menu_kb())
        await state.clear()
        # Alternatively, we could ask which field to edit, but for MVP simple restart is safer
        # Or redirect to start_driver_flow logic if we want to immediately restart:
        # await start_driver_flow(message, state) 
        # But 'start_driver_flow' expects 'I am a Driver' text filter usually.
        # Let's just cancel and ask them to click driver button again.
    else:
        await message.answer("Please choose an option from the keyboard.")

