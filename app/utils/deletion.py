from aiogram import types
from aiogram.fsm.context import FSMContext
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

async def delete_prev_messages(message: types.Message, state: FSMContext):
    """
    Deletes the user's message and the last bot message ID stored in state.
    """
    # 1. Delete User Message
    with suppress(TelegramBadRequest):
        await message.delete()

    # 2. Delete Last Bot Message
    data = await state.get_data()
    last_bot_msg_id = data.get("last_bot_msg_id")
    if last_bot_msg_id:
        with suppress(TelegramBadRequest):
            # We need the bot instance or method to delete by ID + Chat ID.
            # message.bot is available on the message object
            await message.bot.delete_message(chat_id=message.chat.id, message_id=last_bot_msg_id)
        
        # We don't necessarily need to clear it if we are going to overwrite it immediately,
        # but it's good practice so we don't try to delete it again if something fails.
        # However, updating state is async and might be overkill if we do it right after.
        # Let's leave it for now.

async def record_bot_message(state: FSMContext, message: types.Message):
    """
    Records the bot message ID to state for future deletion.
    """
    await state.update_data(last_bot_msg_id=message.message_id)
