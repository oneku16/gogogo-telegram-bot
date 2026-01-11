from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app.keyboards import get_main_menu_kb

router = Router()

@router.message(Command("cancel"))
@router.message(F.text == "Cancel ❌")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Action cancelled.", reply_markup=get_main_menu_kb())
