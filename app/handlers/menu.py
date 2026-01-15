from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.services.api_client import api_client
from app.states import RegistrationState, EditPostState, RideOfferState, RideRequestState
from app.keyboards import (
    get_main_menu_kb, get_phone_request_kb, get_common_locations_kb, 
    get_language_kb, get_settings_kb, get_profile_kb, get_overwrite_confirm_kb
)
from app.handlers.ride_offer import start_driver_flow
from app.handlers.ride_request import start_passenger_flow
from app.handlers.common import get_latest_post, has_active_post
from app.locales import t, LANG_EN, LANG_RU, LANG_KG, MESSAGES
from app.states import RegistrationState, EditPostState, RideOfferState, RideRequestState, SettingsState, OverwriteState, ProfileState
from app.utils.deletion import delete_prev_messages, record_bot_message

router = Router()

def get_localized_texts(key):
    return [MESSAGES[lang].get(key) for lang in MESSAGES]

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
                reply_markup=get_main_menu_kb(lang, role, has_active_post=await has_active_post(user_id)),
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
    await callback.message.delete()
    
    # Now show instructions in selected language
    await callback.message.answer(t("instruction", lang_code), parse_mode="HTML")
    
    # Then ask for phone
    msg = await callback.message.answer(
        t("share_phone", lang_code),
        reply_markup=get_phone_request_kb(lang_code) # We might need to localize this KB too perfectly, but text is static in get_phone_request_kb for now.
    )
    await record_bot_message(state, msg)
    await state.set_state(RegistrationState.WAITING_FOR_PHONE)

@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    role = user_data.get("role")
    
    # If role missing, maybe fetch? But help is simple.
    # If role is None, get_main_menu_kb returns empty/hidden, which is fine as per "remove them at all".
    await message.answer(t("instruction", lang), parse_mode="HTML", reply_markup=get_main_menu_kb(lang, role))



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
    await delete_prev_messages(message, state)
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

        msg = await message.answer(
            t("refile_prompt", lang, type=post_type.upper(), date=post['travel_start_date'], start=post['start_location']),
            reply_markup=kb
        )
        await record_bot_message(state, msg)
        await state.set_state(EditPostState.CONFIRM_REFILE)
        
    except Exception as e:
        await message.answer(t("error_generic", lang, error=str(e)))

@router.message(EditPostState.CONFIRM_REFILE)
async def process_refile_confirm(message: types.Message, state: FSMContext):
    await delete_prev_messages(message, state)
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

# Profile & Cancel Handlers

@router.message(F.text.in_(get_localized_texts("btn_profile")))
@router.message(Command("profile"))
async def cmd_profile(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    lang = user_data.get("language", LANG_EN)
    
    if not user_id:
        # Fallback fetch
        tg_user = await api_client.get_telegram_user(message.from_user.id)
        if tg_user:
             user_id = tg_user["user_id"]
             await state.update_data(user_id=user_id, role=tg_user.get("role"))
    
    # Get user details for profile
    # We might need a proper get_user endpoint or just use tg info + phone
    # Ideally backend provides this. For now, use what we have or mock.
    # We have phone from registration? It might be in state if session persisted, 
    # but safer to fetch if backend supports. 
    # Let's assume we can get it from tg_user result or a new "get_me" endpoint. 
    # The get_telegram_user returns some info.
    
    tg_user = await api_client.get_telegram_user(message.from_user.id)
    name = f"{tg_user.get('first_name', '')} {tg_user.get('last_name', '')}".strip()
    phone = tg_user.get("phone_number", "N/A")
    role = tg_user.get("role", "N/A")
    
    # Check active post
    post_type, post = await get_latest_post(user_id)
    post_summary = t("mypost_none", lang)
    if post:
        if post_type == "offer":
             post_summary = t("mypost_offer", lang, start=post['start_location'], end=post['end_location'], date=post['travel_start_date'], time=post['travel_start_time'], seats=post['free_seats'])
        else:
             post_summary = t("mypost_request", lang, start=post['start_location'], end=post['end_location'], date=post['travel_start_date'], time=post['travel_start_time'], seats=post['seat_amount'])

    text = t("profile_title", lang, name=name, phone=phone, role=role)
    text += "\n\n" + post_summary
    
    await message.answer(text, reply_markup=get_profile_kb(lang), parse_mode="HTML")

@router.message(F.text.in_(get_localized_texts("btn_cancel_search")))
async def cmd_cancel_search(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    lang = user_data.get("language", LANG_EN)
    role = user_data.get("role")
    
    post_type, post = await get_latest_post(user_id)
    if post:
        if post_type == "offer":
            await api_client.delete_ride_offer(post['id'], driver_id=user_id)
        else:
            await api_client.delete_ride_request(post['id'], passenger_id=user_id)
        await message.answer(t("stopped", lang), reply_markup=get_main_menu_kb(lang, role, has_active_post=False))
    else:
        await message.answer(t("mypost_none", lang), reply_markup=get_main_menu_kb(lang, role, has_active_post=False))



# Settings Handlers



@router.message(F.text.in_(get_localized_texts("settings_button")))
async def cmd_settings(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await message.answer(t("settings_button", lang), reply_markup=get_settings_kb(lang))

@router.callback_query(F.data == "settings:role")
async def process_settings_role(callback: types.CallbackQuery, state: FSMContext):
    # Just reuse cmd_changerole logic but from callback
    message = callback.message
    # We can call cmd_changerole but it expects Message object.
    # Let's just do logic here.
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    from app.keyboards import get_role_kb
    await callback.message.delete()
    
    # We could record this message, but since next action is callback which deletes itself, it's fine.
    # But if user gets stuck, maybe record? 
    # Let's keep it simple.
    
    msg = await callback.message.answer(t("choose_role", lang), reply_markup=get_role_kb(lang))
    await record_bot_message(state, msg)
    await state.set_state(RegistrationState.WAITING_FOR_ROLE)
    await callback.answer()

@router.callback_query(F.data == "settings:lang")
async def process_settings_lang(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await callback.message.delete()
    msg = await callback.message.answer(t("welcome_new", lang), reply_markup=get_language_kb())
    await record_bot_message(state, msg)
    await state.set_state(SettingsState.WAITING_LANG)
    await callback.answer()

@router.callback_query(SettingsState.WAITING_LANG, F.data.startswith("lang:"))
async def process_settings_lang_confirm(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split(":")[1]
    
    # Update state
    await state.update_data(language=lang_code)
    
    # Update API/DB
    try:
        await api_client.update_telegram_user(
            telegram_id=callback.from_user.id,
            language=lang_code,
            language_code=lang_code 
        )
    except Exception as e:
        await callback.answer(f"Error updating language: {e}", show_alert=True)
        return

    # Show menu with new language
    user_data = await state.get_data()
    role = user_data.get("role")
    
    await callback.answer(t("selected", lang_code, value=lang_code))
    await callback.message.delete()
    await callback.message.answer(t("instruction", lang_code), parse_mode="HTML", reply_markup=get_main_menu_kb(lang_code, role))

    await state.set_state(None) # Clear state

@router.callback_query(OverwriteState.CONFIRM, F.data.startswith("overwrite:"))
async def process_overwrite_confirm(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", LANG_EN)
    role = data.get("role")
    action = callback.data.split(":")[1]
    
    if action == "yes":
        user_id = data.get("user_id")
        # Deactivate old post
        post_type, post = await get_latest_post(user_id)
        if post:
            if post_type == "offer":
                await api_client.delete_ride_offer(post['id'], driver_id=user_id)
            else:
                await api_client.delete_ride_request(post['id'], passenger_id=user_id)
        
        # Start new flow
        next_flow = data.get("next_flow")
        
        # We need to simulate a message to start flow? 
        # start_driver_flow expects (message, state)
        # We can pass callback.message but we might need to delete the overwrite prompt first or edit it.
        await callback.message.delete()
        
        if next_flow == "driver":
            await start_driver_flow(callback.message, state)
        elif next_flow == "passenger":
            await start_passenger_flow(callback.message, state)
            
    else:
        # No, Keep active
        await callback.answer(t("cancelled", lang))
        await callback.message.delete()
        await callback.message.answer(t("cancelled", lang), reply_markup=get_main_menu_kb(lang, role, has_active_post=True))
        await state.set_state(None)

@router.callback_query(F.data == "settings:edit")
async def process_settings_edit(callback: types.CallbackQuery, state: FSMContext):
    await cmd_edit(callback.message, state) # Reuse cmd_edit logic
    await callback.answer()

@router.callback_query(F.data == "profile:phone")
async def process_profile_phone(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await callback.message.delete() # Clear profile view
    msg = await callback.message.answer(t("share_phone", lang), reply_markup=get_phone_request_kb(lang))
    await record_bot_message(state, msg)
    await state.set_state(ProfileState.WAITING_PHONE)
    await callback.answer()

@router.callback_query(F.data == "profile:name")
async def process_profile_name(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    await callback.message.delete()
    msg = await callback.message.answer(t("btn_change_name", lang) + ":", reply_markup=types.ReplyKeyboardRemove())
    await record_bot_message(state, msg)
    await state.set_state(ProfileState.WAITING_NAME)
    await callback.answer()

@router.message(ProfileState.WAITING_PHONE)
async def process_profile_phone_input(message: types.Message, state: FSMContext):
    await delete_prev_messages(message, state) # Cleanup input + prompt
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    phone = None
    
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text
        
    # Update API
    try:
        await api_client.update_telegram_user(message.from_user.id, phone_number=phone)
        await message.answer(t("selected", lang, value=phone), reply_markup=get_main_menu_kb(lang, user_data.get("role")))
        await state.set_state(None)
    except Exception as e:
         msg = await message.answer(t("error_generic", lang, error=str(e)))
         await record_bot_message(state, msg)

@router.message(ProfileState.WAITING_NAME)
async def process_profile_name_input(message: types.Message, state: FSMContext):
    await delete_prev_messages(message, state)
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    name = message.text
    
    parts = name.split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    
    try:
        await api_client.update_telegram_user(message.from_user.id, first_name=first_name, last_name=last_name)
        await message.answer(t("selected", lang, value=name), reply_markup=get_main_menu_kb(lang, user_data.get("role")))
        await state.set_state(None)
    except Exception as e:
         msg = await message.answer(t("error_generic", lang, error=str(e)))
         await record_bot_message(state, msg)
