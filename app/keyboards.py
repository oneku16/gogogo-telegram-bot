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

def get_main_menu_kb(lang: str = DEFAULT_LANG, role: str = None, has_active_post: bool = False) -> ReplyKeyboardMarkup:
    if role == "driver":
        if has_active_post:
             kb = [
                [KeyboardButton(text=t("btn_cancel_search", lang))],
                [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("settings_button", lang))]
             ]
        else:
             kb = [
                [KeyboardButton(text=t("driver_action", lang))],
                [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("settings_button", lang))]
             ]
    elif role == "passenger":
        if has_active_post:
             kb = [
                [KeyboardButton(text=t("btn_cancel_search", lang))],
                [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("settings_button", lang))]
             ]
        else:
             kb = [
                [KeyboardButton(text=t("passenger_action", lang))],
                [KeyboardButton(text=t("btn_profile", lang)), KeyboardButton(text=t("settings_button", lang))]
             ]
    else:
        # Fallback
        kb = []
    
    if not kb:
        return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
        
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

def get_common_locations_kb(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    cities = ["Bishkek", "Naryn", "Osh", "Karakol", "Balykchy"]
    buttons = [InlineKeyboardButton(text=city, callback_data=f"loc:{city}") for city in cities]
    
    # Add "Other" button
    buttons.append(InlineKeyboardButton(text=t("loc_other", lang), callback_data="loc:other"))
    
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
    
    # Next 7 days
    for i in range(2, 8):
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

def get_settings_kb(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=t("btn_change_lang", lang), callback_data="settings:lang")],
        [InlineKeyboardButton(text=t("btn_change_role", lang), callback_data="settings:role")],
        [InlineKeyboardButton(text=t("btn_edit_post", lang), callback_data="settings:edit")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_kb(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=t("btn_change_phone", lang), callback_data="profile:phone"),
         InlineKeyboardButton(text=t("btn_change_name", lang), callback_data="profile:name")],
         [InlineKeyboardButton(text=t("btn_change_role", lang), callback_data="settings:role")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_overwrite_confirm_kb(lang: str = DEFAULT_LANG) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=t("overwrite_yes", lang), callback_data="overwrite:yes")],
        [InlineKeyboardButton(text=t("overwrite_no", lang), callback_data="overwrite:no")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
