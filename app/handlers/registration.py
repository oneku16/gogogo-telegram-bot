from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states import RegistrationState
from app.keyboards import get_phone_request_kb, get_main_menu_kb
from app.services.api_client import ApiClient
from app.locales import t, LANG_EN

router = Router()
from app.services.api_client import api_client
from app.utils.deletion import delete_prev_messages

# cmd_start is now handled in menu.py

@router.message(RegistrationState.WAITING_FOR_PHONE, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
    await delete_prev_messages(message, state)
    contact = message.contact
    
    # 1. Register User
    try:
        user_id = await api_client.create_user(
            phone_number=contact.phone_number,
            first_name=contact.first_name,
            last_name=contact.last_name
        )
    except Exception as e:
        await message.answer(f"Error during registration: {e}")
        return

    # 2. Link Telegram
    try:
        user_data = await state.get_data()
        lang = user_data.get("language", LANG_EN)
        
        await api_client.link_telegram_user(
            telegram_id=message.from_user.id,
            user_id=user_id,
            chat_id=message.chat.id,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
            language=lang # Pass selected language
        )
        
        if user_id:
             # Store user_id
             await state.update_data(user_id=user_id)
             
             # Ask for Role
             from app.keyboards import get_role_kb
             await message.answer(t("choose_role", lang), reply_markup=get_role_kb(lang))
             await state.set_state(RegistrationState.WAITING_FOR_ROLE)
             
    except Exception as e:
        await message.answer(f"Error during registration: {e}") 
        # await state.clear() clears data too. We want to keep user_id if we rely on it.
        # usually state.clear() removes data. 
        # If we use state.set_state(None), data persists.

@router.message(RegistrationState.WAITING_FOR_ROLE)
async def process_role(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    
    # Needs localization for role matching?
    # Or we use a callback KB for roles to be safe? 
    # Let's use get_role_kb with CallbackQuery for safety.
    pass # Wait, let's use callbacks.

@router.callback_query(RegistrationState.WAITING_FOR_ROLE, F.data.startswith("role:"))
async def process_role_callback(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("language", LANG_EN)
    role = callback.data.split(":")[1] # driver / passenger
    
    await callback.message.delete()
    
    user_id = user_data.get("user_id")
    
    # Update Role
    try:
        await api_client.update_user_role(
            telegram_id=callback.from_user.id,
            role=role
        )
        
        # Save Role to state as well
        await state.update_data(role=role)

        # Show Main Menu
        await callback.message.answer(t("registration_complete", lang), reply_markup=get_main_menu_kb(lang, role))
        await state.set_state(None)
        
    except Exception as e:
        await callback.message.answer(f"Error linking account: {e}")
