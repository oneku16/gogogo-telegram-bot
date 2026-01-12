import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.config import BOT_TOKEN
from app.handlers import registration, menu, common, ride_offer, ride_request

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(common.router)
    dp.include_router(menu.router)
    dp.include_router(registration.router)
    dp.include_router(ride_offer.router)
    dp.include_router(ride_request.router)

    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start Webhook Server
    from app.webhook import setup_webhook_app
    from aiohttp import web
    
    web_app = setup_webhook_app(bot)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8001)
    await site.start()
    logging.info("Webhook server started on port 8001")

    # Start ApiClient Session
    from app.services.api_client import api_client
    await api_client.start()

    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await api_client.close()

if __name__ == "__main__":
    asyncio.run(main())
