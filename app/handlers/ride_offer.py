import os
from loguru import logger
import aiofiles
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from app.states import RideOfferState
from app.services.api_client import api_client
from app.keyboards import get_main_menu_kb, get_cancel_kb, get_common_locations_kb, get_dates_kb, get_seats_kb, get_confirmation_kb
from app.utils.formatting import parse_date, parse_time, format_date, format_time
from app.locales import t, LANG_EN
from datetime import date, time

router = Router()

# Localization Helper for filters
def get_localized_texts(key):
    from app.locales import MESSAGES
    return [MESSAGES[lang].get(key) for lang in MESSAGES]

@router.message(F.text.in_(get_localized_texts("driver_action")))
async def start_driver_flow(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await message.answer(t("start_loc_prompt", lang), reply_markup=get_common_locations_kb())
    await state.set_state(RideOfferState.START_LOC)

@router.message(RideOfferState.START_LOC, F.text)
async def process_start_loc_text(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await state.update_data(start_location=message.text)
    await message.answer(t("end_loc_prompt", lang), reply_markup=get_common_locations_kb()) 
    await state.set_state(RideOfferState.END_LOC)

@router.callback_query(RideOfferState.START_LOC, F.data.startswith("loc:"))
async def process_start_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    city = callback.data.split(":")[1]
    
    await state.update_data(start_location=city)
    await callback.answer(t("selected", lang, value=city))
    await callback.message.answer(t("loc_start", lang, value=city))
    await callback.message.answer(t("end_loc_prompt", lang), reply_markup=get_common_locations_kb())
    await state.set_state(RideOfferState.END_LOC)

@router.callback_query(RideOfferState.END_LOC, F.data.startswith("loc:"))
async def process_end_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    location = callback.data.split(":")[1]
    await state.update_data(end_location=location)
    await callback.answer(t("selected", lang, value=location))
    await callback.message.answer(t("loc_dest", lang, value=location))
    await callback.message.answer(t("date_prompt", lang), reply_markup=get_dates_kb(lang))
    await state.set_state(RideOfferState.DATE)

@router.message(RideOfferState.END_LOC)
async def process_end_loc(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await state.update_data(end_location=message.text)
    await message.answer(t("date_prompt", lang), reply_markup=get_dates_kb(lang))
    await state.set_state(RideOfferState.DATE)

@router.callback_query(RideOfferState.DATE, F.data.startswith("date:"))
async def process_date_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    date_str = callback.data.split(":")[1]
    try:
        d = parse_date(date_str)
        await state.update_data(travel_start_date=d.isoformat())
        await callback.answer(t("selected", lang, value=date_str))
        await callback.message.answer(t("date_selected", lang, value=date_str))
        await callback.message.answer(t("time_prompt", lang))
        await state.set_state(RideOfferState.TIME)
    except ValueError:
        await callback.answer(t("error_generic", lang, error="Date error"))

@router.message(RideOfferState.DATE)
async def process_date(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    try:
        d = parse_date(message.text)
        await state.update_data(travel_start_date=d.isoformat())
        await message.answer(t("time_prompt", lang))
        await state.set_state(RideOfferState.TIME)
    except ValueError:
        await message.answer(t("error_date", lang), reply_markup=get_dates_kb(lang))

@router.message(RideOfferState.TIME)
async def process_time(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    try:
        t_val = parse_time(message.text)
        await state.update_data(travel_start_time=t_val.isoformat(), time_iso=t_val.isoformat())
        await message.answer(t("seats_offer_prompt", lang), reply_markup=get_seats_kb())
        await state.set_state(RideOfferState.SEATS)
    except ValueError:
        await message.answer(t("error_time", lang))

@router.callback_query(RideOfferState.SEATS, F.data.startswith("seats:"))
async def process_seats_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    seats = int(callback.data.split(":")[1])
    await state.update_data(total_seat_amount=seats, free_seats=seats)
    await callback.answer(t("selected", lang, value=seats))
    await callback.message.answer(t("car_model_prompt", lang))
    await state.set_state(RideOfferState.CAR_MODEL)

@router.message(RideOfferState.SEATS)
async def process_seats(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    if not message.text.isdigit():
        await message.answer(t("error_number", lang), reply_markup=get_seats_kb())
        return
    seats = int(message.text)
    await state.update_data(total_seat_amount=seats, free_seats=seats)
    await message.answer(t("car_model_prompt", lang))
    await state.set_state(RideOfferState.CAR_MODEL)

@router.message(RideOfferState.CAR_MODEL)
async def process_car(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await state.update_data(car_model=message.text)
    await message.answer(t("price_prompt", lang))
    await state.set_state(RideOfferState.PRICE)

@router.message(RideOfferState.PRICE)
async def process_price(message: types.Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    if not message.text.isdigit():
        await message.answer(t("error_number", lang))
        return
    
    price = int(message.text)
    await state.update_data(price=price)
    
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
    summary = t("summary_offer", lang, 
        start=offer_data['start_location'],
        end=offer_data['end_location'],
        date=format_date(date.fromisoformat(offer_data['travel_start_date'])),
        time=format_time(time.fromisoformat(offer_data['travel_start_time'])),
        seats=offer_data['free_seats'],
        car=offer_data['car_model'],
        price=offer_data['price']
    )
    
    await message.answer(summary, reply_markup=get_confirmation_kb(lang), parse_mode="HTML")
    await state.set_state(RideOfferState.CONFIRMATION)


@router.message(RideOfferState.CONFIRMATION)
async def process_confirmation(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    
    # Check against localized button text
    confirm_text = t("confirm_button", lang)
    edit_text = t("edit_button", lang)
    
    if message.text == confirm_text:
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
                    await message.answer(t("error_generic", lang, error="User not found. Please /start again."))
                    return

            await api_client.create_ride_offer(driver_id, offer_data)
            await message.answer(t("published_offer", lang), reply_markup=get_main_menu_kb(lang, role="driver"))
            await state.clear()

        except Exception as e:
            await message.answer(t("error_generic", lang, error=str(e)))
            
    elif message.text == edit_text:
        await message.answer(t("cancelled", lang), reply_markup=get_main_menu_kb(lang, role="driver"))
        await state.clear()
    else:
        # If user typed something else, maybe show KB again
        await message.answer(t("error_generic", lang, error="Please tap button."), reply_markup=get_confirmation_kb(lang))

