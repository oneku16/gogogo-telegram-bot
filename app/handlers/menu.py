from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.keyboards import get_main_menu_kb, get_phone_request_kb
from app.services.api_client import ApiClient
from app.states import RegistrationState

router = Router()
api_client = ApiClient()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Check if user is registered
    tg_user = await api_client.get_telegram_user(message.from_user.id)
    
    if tg_user:
        # Registered
        await message.answer(
            f"Welcome back, {message.from_user.first_name}!",
            reply_markup=get_main_menu_kb()
        )
        # Store user_id in state for session
        await state.update_data(user_id=tg_user["user_id"])
    else:
        # Not registered
        await message.answer(
            "Welcome! To use this bot, please share your phone number to register.",
            reply_markup=get_phone_request_kb()
        )
        await state.set_state(RegistrationState.WAITING_FOR_PHONE)
