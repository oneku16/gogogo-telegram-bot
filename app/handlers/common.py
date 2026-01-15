from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app.keyboards import get_main_menu_kb
from app.services.api_client import api_client

router = Router()

async def get_latest_post(user_id: str):
    offers = await api_client.get_driver_offers(user_id)
    requests = await api_client.get_passenger_requests(user_id)
    
    latest_offer = offers[0] if offers else None
    latest_request = requests[0] if requests else None
    
    # Return Offer if exists, else Request (Simple MVP priority)
    if latest_offer:
        return ("offer", latest_offer)
    elif latest_request:
        return ("request", latest_request)
    return (None, None)

async def has_active_post(user_id: str) -> bool:
    if not user_id: return False
    pt, p = await get_latest_post(user_id)
    return p is not None

@router.message(Command("cancel"))
@router.message(F.text == "Cancel ❌")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Action cancelled.", reply_markup=get_main_menu_kb())
