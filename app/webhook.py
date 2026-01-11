from aiohttp import web
from aiogram import Bot

async def webhook_handler(request: web.Request):
    """
    Handles notifications from the backend.
    """
    bot: Bot = request.app["bot"]
    data = await request.json()
    
    notification_type = data.get("type")
    
    try:
        if notification_type == "matches_found_for_offer":
            driver_telegram_id = data.get("driver_telegram_id")
            matches = data.get("matches", [])
            
            if driver_telegram_id:
                text = "🎉 <b>Found matching passengers!</b>\n\n"
                for r in matches:
                    text += f"👤 <b>Passenger Requirement:</b>\n"
                    text += f"📅 {r['travel_start_date']} at {r['travel_start_time']}\n"
                    text += f"🪑 Seats: {r['seat_amount']}\n"
                    text += f"-------------------------\n"
                
                await bot.send_message(chat_id=driver_telegram_id, text=text, parse_mode="HTML")

        elif notification_type == "matches_found_for_request":
            passenger_telegram_id = data.get("passenger_telegram_id")
            matches = data.get("matches", [])
            
            if passenger_telegram_id:
                text = "🎉 <b>Found matching drivers!</b>\n\n"
                for o in matches:
                    text += f"🚗 <b>{o['car_model']}</b>\n"
                    text += f"📅 {o['travel_start_date']} at {o['travel_start_time']}\n"
                    text += f"🪑 Free Seats: {o['free_seats']}\n"
                    text += f"-------------------------\n"
                
                await bot.send_message(chat_id=passenger_telegram_id, text=text, parse_mode="HTML")
            
        return web.Response(text="OK")
    except Exception as e:
        print(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)

def setup_webhook_app(bot: Bot) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app.router.add_post("/notify", webhook_handler)
    return app
