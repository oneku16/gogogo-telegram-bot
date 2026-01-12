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
                text += f"📍 From: {offer['start_location']}\n"
                text += f"📍 To: {offer['end_location']}\n"
                text += f"📅 {offer['travel_start_date']} at {offer['travel_start_time']}\n"
                text += f"🪑 Free Seats: {offer['free_seats']}\n"

                price = offer.get('price')
                if price:
                    text += f"💰 Price: {price} KGS\n"

                driver_phone = offer.get('driver_phone')
                driver_username = offer.get('driver_username')
                
                text += f"📞 Driver contacts: "
                contacts_parts = []
                if driver_phone:
                    contacts_parts.append(f"<code>+{driver_phone}</code>")
                if driver_username:
                        contacts_parts.append(f"@{driver_username}")
                
                text += ", ".join(contacts_parts) + "\n"
                
                await bot.send_message(chat_id=passenger_chat_id, text=text, parse_mode="HTML")

        elif notification_type == "matches_found_for_request":
            passenger_telegram_id = data.get("passenger_telegram_id")
            passenger_chat_id = data.get("passenger_chat_id", passenger_telegram_id)
            matches = data.get("matches", [])
            
            if passenger_chat_id:
                # Send introductory message
                await bot.send_message(
                    chat_id=passenger_chat_id, 
                    text=f"🎉 <b>Found {len(matches)} matching drivers!</b>", 
                    parse_mode="HTML"
                )
                
                for o in matches:
                    text = "" 
                    text += f"🚗 <b>{o['car_model']}</b>\n"
                    text += f"📍 From: {o['start_location']}\n"
                    text += f"📍 To: {o['end_location']}\n"
                    text += f"📅 {o['travel_start_date']} at {o['travel_start_time']}\n"
                    text += f"🪑 Free Seats: {o['free_seats']}\n"
                    
                    price = o.get('price')
                    if price:
                        text += f"💰 Price: {price} KGS\n"
                    
                    driver_phone = o.get('driver_phone')
                    driver_username = o.get('driver_username')
                    
                    text += f"📞 Driver contacts: "
                    contacts_parts = []
                    if driver_phone:
                        contacts_parts.append(f"<code>+{driver_phone}</code>")
                    if driver_username:
                         contacts_parts.append(f"@{driver_username}")
                    
                    text += ", ".join(contacts_parts) + "\n"

                    # Send each offer as a separate message
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
