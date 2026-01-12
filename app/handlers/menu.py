from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.services.api_client import api_client
from app.states import RegistrationState, EditPostState, RideOfferState, RideRequestState
from app.keyboards import get_main_menu_kb, get_phone_request_kb, get_common_locations_kb, get_language_kb
from app.handlers.ride_offer import start_driver_flow
from app.handlers.ride_request import start_passenger_flow
from app.locales import t, LANG_EN, LANG_RU, LANG_KG

router = Router()

INSTRUCTION_TEXT = (
    "<b>Welcome to GoGoGo!</b> 🚕\n\n"
    "This bot matches Drivers 🚗 and Passengers 🧍 for inter-city rides.\n\n"
    "<b>How it works:</b>\n"
    "1. Choose your role (Driver or Passenger).\n"
    "2. Enter your trip details (Location, Date, Time).\n"
    "3. We'll verify your phone number (one time).\n"
    "4. We notify you when a match is found!\n\n"
    "<b>Commands:</b>\n"
    "/start - Start the bot\n"
    "/help - Show this guide\n"
    "/mypost - Show your current active ride\n"
    "/edit - Refile (delete & new) your active ride"
)

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Check if user is registered
    tg_user = await api_client.get_telegram_user(message.from_user.id)
    
    if tg_user:
        # Registered
        user_id = tg_user["user_id"]
        lang = tg_user.get("language") or tg_user.get("language_code", LANG_EN)
        role = tg_user.get("role")
        
        # Ensure state matches DB
        await state.update_data(user_id=user_id, language=lang, role=role)
        
        if role:
            await message.answer(
                t("welcome_back", lang, name=message.from_user.first_name) + "\n\n" + t("instruction", lang),
                reply_markup=get_main_menu_kb(lang, role),
                parse_mode="HTML"
            )
        else:
            # Role missing (legacy user?), ask for role
            from app.keyboards import get_role_kb
            await message.answer(t("choose_role", lang), reply_markup=get_role_kb(lang))
            await state.set_state(RegistrationState.WAITING_FOR_ROLE)
            
    else:
        # Not registered
        # Ask for Language FIRST
        await message.answer(t("welcome_new", LANG_EN), reply_markup=get_language_kb())
        await state.set_state(RegistrationState.WAITING_FOR_LANGUAGE)

@router.message(Command("changerole"))
async def cmd_changerole(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    
    # Just show role KB
    from app.keyboards import get_role_kb
    await message.answer(t("choose_role", lang), reply_markup=get_role_kb(lang))
    
    # Reuse the registration handler logic or duplicate partial logic?
    # The registration handler expects RegistrationState.WAITING_FOR_ROLE
    # So we can just set that state!
    await state.set_state(RegistrationState.WAITING_FOR_ROLE)
    await state.set_state(RegistrationState.WAITING_FOR_ROLE)

@router.message(Command("stop"))
async def cmd_stop(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    lang = user_data.get("language", LANG_EN)
    
    if not user_id:
         # ... (Authentication fallback logic repeated or refactored)
         tg_user = await api_client.get_telegram_user(message.from_user.id)
         if tg_user:
             user_id = tg_user["user_id"]
             lang = tg_user.get("language", LANG_EN)
             role = tg_user.get("role")
             await state.update_data(user_id=user_id, language=lang, role=role)
         else:
             await message.answer(t("welcome_new", lang), reply_markup=get_language_kb())
             return
             
    role = user_data.get("role") # Try getting from state if not fetched above
    if not role and user_id: 
         # Double check if we didn't fetch it above
         tg_user = await api_client.get_telegram_user(message.from_user.id)
         if tg_user:
             role = tg_user.get("role")
             await state.update_data(role=role)

    try:
        post_type, post = await get_latest_post(user_id)
        
        if not post:
            await message.answer(t("mypost_none", lang))
            return

        if post_type == "offer":
            await api_client.delete_ride_offer(post['id'], driver_id=user_id)
        else:
            await api_client.delete_ride_request(post['id'], passenger_id=user_id)
            
        await message.answer(t("stopped", lang), reply_markup=get_main_menu_kb(lang, role))
        
    except Exception as e:
        await message.answer(t("error_generic", lang, error=str(e)))
@router.callback_query(RegistrationState.WAITING_FOR_LANGUAGE, F.data.startswith("lang:"))
async def process_language_selection(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split(":")[1]
    await state.update_data(language=lang_code)
    
    await callback.answer(f"Selected: {lang_code}")
    
    # Now show instructions in selected language
    await callback.message.answer(t("instruction", lang_code), parse_mode="HTML")
    
    # Then ask for phone
    await callback.message.answer(
        t("share_phone", lang_code),
        reply_markup=get_phone_request_kb(lang_code) # We might need to localize this KB too perfectly, but text is static in get_phone_request_kb for now.
    )
    await state.set_state(RegistrationState.WAITING_FOR_PHONE)

@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    role = user_data.get("role")
    
    # If role missing, maybe fetch? But help is simple.
    # If role is None, get_main_menu_kb returns empty/hidden, which is fine as per "remove them at all".
    await message.answer(t("instruction", lang), parse_mode="HTML", reply_markup=get_main_menu_kb(lang, role))

async def get_latest_post(user_id: str):
    offers = await api_client.get_driver_offers(user_id)
    requests = await api_client.get_passenger_requests(user_id)
    
    latest_offer = offers[0] if offers else None
    latest_request = requests[0] if requests else None
    
    # Simple logic: return the one created most recently
    # Assuming API returns sorted by created_at desc (which repo does)
    if latest_offer and latest_request:
        # Compare dates (naive string comparison might work if ISO, but safer to parse)
        # Assuming created_at field exists in DTO? Yes, BaseModel usually. 
        # API DTO doesn't explicitly modify created_at, but Models handle it. 
        # DTO usually includes it. Let's assume we pick the "newer" type based on simple heuristic or just Offer priority for now request/offer confusion.
        # Let's just return the very first one from either list that looks "active" (future date?).
        # For MVP: Return Offer if exists, else Request.
        return ("offer", latest_offer)
    elif latest_offer:
        return ("offer", latest_offer)
    elif latest_request:
        return ("request", latest_request)
    return (None, None)

@router.message(Command("mypost"))
async def cmd_mypost(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    # Always try to get lang
    lang = user_data.get("language", LANG_EN)
    
    if not user_id:
        tg_user = await api_client.get_telegram_user(message.from_user.id)
        if tg_user:
            user_id = tg_user["user_id"]
            lang = tg_user.get("language", LANG_EN)
            await state.update_data(user_id=user_id, language=lang)
        else:
            await message.answer(t("welcome_new", lang), reply_markup=get_language_kb())
            return

    try:
        post_type, post = await get_latest_post(user_id)
        
        if not post:
            await message.answer(t("mypost_none", lang))
            return

        if post_type == "offer":
            text = t("mypost_offer", lang,
                start=post['start_location'],
                end=post['end_location'],
                date=post['travel_start_date'],
                time=post['travel_start_time'],
                seats=post['free_seats']
            )
        else:
            text = t("mypost_request", lang,
                start=post['start_location'],
                end=post['end_location'],
                date=post['travel_start_date'],
                time=post['travel_start_time'],
                seats=post['seat_amount']
            )
            
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(t("error_generic", lang, error=str(e)))

@router.message(Command("edit"))
async def cmd_edit(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    lang = user_data.get("language", LANG_EN)
    
    if not user_id:
        tg_user = await api_client.get_telegram_user(message.from_user.id)
        if tg_user:
            user_id = tg_user["user_id"]
            lang = tg_user.get("language", LANG_EN)
            await state.update_data(user_id=user_id, language=lang)
        else:
            await message.answer(t("welcome_new", lang), reply_markup=get_language_kb())
            return

    try:
        post_type, post = await get_latest_post(user_id)
        
        if not post:
            await message.answer(t("mypost_none", lang))
            return
            
        # Store for deletion
        await state.update_data(target_id=post['id'], target_type=post_type)
        
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        # Custom small KB just for this yes/no
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=t("refile_yes", lang)), KeyboardButton(text=t("refile_no", lang))]
        ], resize_keyboard=True, one_time_keyboard=True)

        await message.answer(
            t("refile_prompt", lang, type=post_type.upper(), date=post['travel_start_date'], start=post['start_location']),
            reply_markup=kb
        )
        await state.set_state(EditPostState.CONFIRM_REFILE)
        
    except Exception as e:
        await message.answer(t("error_generic", lang, error=str(e)))

@router.message(EditPostState.CONFIRM_REFILE)
async def process_refile_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", LANG_EN)
    role = data.get("role")
    yes_text = t("refile_yes", lang)
    
    if message.text == yes_text:
        # ... (lines 248-267) ...
        user_id = data.get("user_id")
        target_id = data.get("target_id")
        target_type = data.get("target_type")
        
        try:
            if target_type == "offer":
                await api_client.delete_ride_offer(target_id, driver_id=user_id)
                await message.answer(t("cancelled", lang), reply_markup=types.ReplyKeyboardRemove())
                await start_driver_flow(message, state)
            else:
                await api_client.delete_ride_request(target_id, passenger_id=user_id)
                await message.answer(t("cancelled", lang), reply_markup=types.ReplyKeyboardRemove())
                await start_passenger_flow(message, state)
                
        except Exception as e:
            # Need role here? If error, show menu.
            await message.answer(t("error_generic", lang, error=str(e)), reply_markup=get_main_menu_kb(lang, role))
            await state.clear()
            
    else:
        await message.answer(t("cancelled", lang), reply_markup=get_main_menu_kb(lang, role))
        await state.clear()
