from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from app.states import RideRequestState, OverwriteState
from app.services.api_client import api_client
from app.keyboards import get_main_menu_kb, get_cancel_kb, get_common_locations_kb, get_dates_kb, get_seats_kb, get_confirmation_kb, get_overwrite_confirm_kb
from app.handlers.common import has_active_post, get_latest_post
from app.utils.formatting import parse_date, parse_time, format_date, format_time
from app.locales import t, LANG_EN
from datetime import date, time

router = Router()

# Localization Helper for filters
def get_localized_texts(key):
    from app.locales import MESSAGES
    return [MESSAGES[lang].get(key) for lang in MESSAGES]

@router.message(F.text.in_(get_localized_texts("passenger_action")))
async def start_passenger_flow(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    user_id = user_data.get("user_id")

    # Check active post
    if await has_active_post(user_id):
        pt, p = await get_latest_post(user_id)
        # Create summary of active post
        post_summary = t("mypost_none", lang)
        if p:
             if pt == "offer":
                 post_summary = t("mypost_offer", lang, start=p['start_location'], end=p['end_location'], date=p['travel_start_date'], time=p['travel_start_time'], seats=p['free_seats'])
             else:
                 post_summary = t("mypost_request", lang, start=p['start_location'], end=p['end_location'], date=p['travel_start_date'], time=p['travel_start_time'], seats=p['seat_amount'])

        await message.answer(t("active_post_limit", lang, post_summary=post_summary), reply_markup=get_overwrite_confirm_kb(lang))
        await state.set_state(OverwriteState.CONFIRM)
        await state.update_data(next_flow="passenger")
        return

    await message.answer(t("start_loc_prompt", lang), reply_markup=get_common_locations_kb())
    await state.set_state(RideRequestState.START_LOC)

@router.callback_query(RideRequestState.START_LOC, F.data.startswith("loc:"))
async def process_start_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    city = callback.data.split(":")[1]
    
    await state.update_data(start_location=city)
    await callback.answer(t("selected", lang, value=city))
    await callback.message.answer(t("loc_start", lang, value=city))
    await callback.message.answer(t("end_loc_prompt", lang), reply_markup=get_common_locations_kb())
    await state.set_state(RideRequestState.END_LOC)

@router.message(RideRequestState.START_LOC)
async def process_start_loc_text(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await state.update_data(start_location=message.text)
    await message.answer(t("end_loc_prompt", lang), reply_markup=get_common_locations_kb())
    await state.set_state(RideRequestState.END_LOC)

@router.callback_query(RideRequestState.END_LOC, F.data.startswith("loc:"))
async def process_end_loc_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    location = callback.data.split(":")[1]
    await state.update_data(end_location=location)
    await callback.answer(t("selected", lang, value=location))
    await callback.message.answer(t("loc_dest", lang, value=location))
    await callback.message.answer(t("date_prompt", lang), reply_markup=get_dates_kb(lang))
    await state.set_state(RideRequestState.DATE)

@router.message(RideRequestState.END_LOC)
async def process_end_loc(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await state.update_data(end_location=message.text)
    await message.answer(t("date_prompt", lang), reply_markup=get_dates_kb(lang))
    await state.set_state(RideRequestState.DATE)

@router.callback_query(RideRequestState.DATE, F.data.startswith("date:"))
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
        await state.set_state(RideRequestState.TIME)
    except ValueError:
        await callback.answer(t("error_generic", lang, error="Date error"))

@router.message(RideRequestState.DATE)
async def process_date(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    try:
        d = parse_date(message.text)
        await state.update_data(travel_start_date=d.isoformat())
        await message.answer(t("time_prompt", lang))
        await state.set_state(RideRequestState.TIME)
    except ValueError:
        await message.answer(t("error_date", lang), reply_markup=get_dates_kb(lang))

@router.message(RideRequestState.TIME)
async def process_time(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    try:
        t_val = parse_time(message.text)
        await state.update_data(travel_start_time=t_val.isoformat())
        await message.answer(t("seats_request_prompt", lang), reply_markup=get_seats_kb())
        await state.set_state(RideRequestState.SEATS)
    except ValueError:
        await message.answer(t("error_time", lang))

@router.callback_query(RideRequestState.SEATS, F.data.startswith("seats:"))
async def process_seats_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    seat_amount = callback.data.split(":")[1]
    await state.update_data(seat_amount=seat_amount)
    
    # Show Summary
    summary = t("summary_request", lang,
        start=user_data['start_location'],
        end=user_data['end_location'],
        date=format_date(date.fromisoformat(user_data['travel_start_date'])),
        time=format_time(time.fromisoformat(user_data['travel_start_time'])),
        seats=seat_amount
    )
    
    await callback.answer(t("selected", lang, value=seat_amount))
    await callback.message.answer(summary, reply_markup=get_confirmation_kb(lang), parse_mode="HTML")
    await state.set_state(RideRequestState.CONFIRMATION)

@router.message(RideRequestState.SEATS)
async def process_seats(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    seat_amount = message.text 
    await state.update_data(seat_amount=seat_amount)
    
    # Show Summary
    summary = t("summary_request", lang,
        start=user_data['start_location'],
        end=user_data['end_location'],
        date=format_date(date.fromisoformat(user_data['travel_start_date'])),
        time=format_time(time.fromisoformat(user_data['travel_start_time'])),
        seats=seat_amount
    )
    
    await message.answer(summary, reply_markup=get_confirmation_kb(lang), parse_mode="HTML")
    await state.set_state(RideRequestState.CONFIRMATION)


@router.message(RideRequestState.CONFIRMATION)
async def process_confirmation(message: types.Message, state: FSMContext, bot):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    
    # Check against localized button text
    confirm_text = t("confirm_button", lang)
    edit_text = t("edit_button", lang)
    
    if message.text == confirm_text:
        # Recover ID if missing
        passenger_id = user_data.get("user_id")
        if not passenger_id:
             tg_user = await api_client.get_telegram_user(message.from_user.id)
             if tg_user:
                 passenger_id = tg_user["user_id"]
             else:
                 await message.answer(t("error_generic", lang, error="User not found. Please /start again."))
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
            await message.answer(t("published_request", lang), reply_markup=get_main_menu_kb(lang, role="passenger"))
            await state.clear()
            
        except Exception as e:
            await message.answer(t("error_generic", lang, error=str(e)))
            
    elif message.text == edit_text:
        await message.answer(t("cancelled", lang), reply_markup=get_main_menu_kb(lang, role="passenger"))
        await state.clear()
    else:
        await message.answer(t("error_generic", lang, error="Please tap button."), reply_markup=get_confirmation_kb(lang))

# Async matching removed (Moved to Celery)
