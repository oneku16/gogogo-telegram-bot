from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

def get_phone_request_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Share Phone Number", request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="I am a Driver 🚗")],
        [KeyboardButton(text="I am a Passenger 🧍")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Cancel ❌")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_confirmation_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Confirm ✅")],
        [KeyboardButton(text="Edit 📝")] 
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

def get_dates_kb() -> InlineKeyboardMarkup:
    today = datetime.now()
    dates = []
    
    # Today
    dates.append(InlineKeyboardButton(text="Today", callback_data=f"date:{today.strftime('%d.%m.%Y')}"))
    
    # Tomorrow
    tmrw = today + timedelta(days=1)
    dates.append(InlineKeyboardButton(text="Tomorrow", callback_data=f"date:{tmrw.strftime('%d.%m.%Y')}"))
    
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
