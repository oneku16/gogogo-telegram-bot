from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from app.locales import t, DEFAULT_LANG

def get_phone_request_kb(lang: str = DEFAULT_LANG) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=t("phone_button", lang), request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_role_kb(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=t("driver_button", lang), callback_data="role:driver")],
        [InlineKeyboardButton(text=t("passenger_button", lang), callback_data="role:passenger")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu_kb(lang: str = DEFAULT_LANG, role: str = None) -> ReplyKeyboardMarkup:
    if role == "driver":
        kb = [[KeyboardButton(text=t("driver_action", lang))]] # e.g. "Create Ride"
    elif role == "passenger":
        kb = [[KeyboardButton(text=t("passenger_action", lang))]] # e.g. "Find Ride"
    else:
        # Fallback if no role yet - show nothing or rely on inline role picker
        # User requested to remove "I am..." buttons entirely.
        kb = []
    
    if not kb:
        return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True) # Empty
        
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_kb(lang: str = DEFAULT_LANG) -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=t("cancel_button", lang))]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_confirmation_kb(lang: str = DEFAULT_LANG) -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=t("confirm_button", lang))],
        [KeyboardButton(text=t("edit_button", lang))] 
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_common_locations_kb() -> InlineKeyboardMarkup:
    cities = ["Bishkek", "Naryn", "Osh", "Karakol", "Balykchy"]
    buttons = [InlineKeyboardButton(text=city, callback_data=f"loc:{city}") for city in cities]
    
    # Chunk into 2 columns
    rows = []
    for i in range(0, len(buttons), 2):
        rows.append(buttons[i:i+2])
        
    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_dates_kb(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    today = datetime.now()
    dates = []
    
    # Today
    dates.append(InlineKeyboardButton(text=t("kb_today", lang), callback_data=f"date:{today.strftime('%d.%m.%Y')}"))
    
    # Tomorrow
    tmrw = today + timedelta(days=1)
    dates.append(InlineKeyboardButton(text=t("kb_tomorrow", lang), callback_data=f"date:{tmrw.strftime('%d.%m.%Y')}"))
    
    # Next 2 days
    for i in range(2, 4):
         next_d = today + timedelta(days=i)
         dates.append(InlineKeyboardButton(text=next_d.strftime("%d.%m"), callback_data=f"date:{next_d.strftime('%d.%m.%Y')}"))

    rows = []
    for i in range(0, len(dates), 2):
         rows.append(dates[i:i+2])

    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_seats_kb() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f"seats:{i}") for i in range(1, 5)]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def get_language_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="English 🇺🇸", callback_data="lang:en")],
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang:ru")],
        [InlineKeyboardButton(text="Кыргызча 🇰🇬", callback_data="lang:kg")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
