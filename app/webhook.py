from aiohttp import web
from aiohttp import web
from aiogram import Bot
from loguru import logger

async def webhook_handler(request: web.Request):
    """
    Handles notifications from the backend.
    """
    bot: Bot = request.app["bot"]
    data = await request.json()
    
    notification_type = data.get("type")
    logger.info(f"Webhook received. Type: {notification_type}. Data: {data}")
    
    try:
        if notification_type == "new_offer_found":
            passenger_chat_id = data.get("passenger_chat_id")
            offer = data.get("offer")
            
            if passenger_chat_id and offer:
                text = "🎉 <b>Good news! A new ride offer matches your request!</b>\n\n"
                text += f"🚗 <b>{offer['car_model']}</b>\n"
                text += f"📍 {offer['start_location']} -> {offer['end_location']}\n"
                text += f"📅 {offer['travel_start_date']} at {offer['travel_start_time']}\n"
                text += f"🪑 Free Seats: {offer['free_seats']}\n"
                text += f"-------------------------\n"
                
                await bot.send_message(chat_id=passenger_chat_id, text=text, parse_mode="HTML")

        elif notification_type == "matches_found_for_request":
            passenger_telegram_id = data.get("passenger_telegram_id")
            passenger_chat_id = data.get("passenger_chat_id", passenger_telegram_id)
            matches = data.get("matches", [])
            
            if passenger_chat_id:
                text = "🎉 <b>Found matching drivers!</b>\n\n"
                for o in matches:
                    text += f"🚗 <b>{o['car_model']}</b>\n"
                    text += f"📅 {o['travel_start_date']} at {o['travel_start_time']}\n"
                    text += f"🪑 Free Seats: {o['free_seats']}\n"
                    text += f"-------------------------\n"
                
                await bot.send_message(chat_id=passenger_chat_id, text=text, parse_mode="HTML")
            
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)

def setup_webhook_app(bot: Bot) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app.router.add_post("/notify", webhook_handler)
    return app
