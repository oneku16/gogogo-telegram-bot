from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states import RegistrationState
from app.keyboards import get_phone_request_kb, get_main_menu_kb
from app.services.api_client import ApiClient

router = Router()
from app.services.api_client import api_client

# cmd_start is now handled in menu.py

@router.message(RegistrationState.WAITING_FOR_PHONE, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
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
        await api_client.link_telegram_user(
            telegram_id=message.from_user.id,
            user_id=user_id,
            chat_id=message.chat.id,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
            language=message.from_user.language_code 
        )
        
        # Store user_id in state
        await state.update_data(user_id=user_id)
        
        await message.answer(
            "Registration successful! Please choose your role:", 
            reply_markup=get_main_menu_kb()
        )
        await state.set_state(None) # Clear state but keep data? 
        # await state.clear() clears data too. We want to keep user_id if we rely on it.
        # usually state.clear() removes data. 
        # If we use state.set_state(None), data persists.
        
    except Exception as e:
        await message.answer(f"Error link telegram account: {e}")
