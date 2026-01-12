from typing import Dict

# Language Codes
LANG_EN = "en"
LANG_RU = "ru"
LANG_KG = "kg"

DEFAULT_LANG = LANG_EN

MESSAGES: Dict[str, Dict[str, str]] = {
    LANG_EN: {
        "welcome_back": "Welcome back, {name}!",
        "welcome_new": "Welcome to GoGoGo! Please choose your language:",
        "share_phone": "Please share your phone number to register.",
        "phone_button": "Share Phone Contact 📱",
        "choose_role": "Registration successful! Choose your role (you can change it later with /changerole):",
        "driver_button": "I am a Driver 🚗",
        "passenger_button": "I am a Passenger 🧍",
        "driver_action": "Create Trip 🚗",
        "passenger_action": "Find Ride 🧍",
        "registration_complete": "Registration complete! How can we help you today?",
        "cancel_button": "Cancel ❌",
        "role_switched": "Role switched to: {role}",
        "start_loc_prompt": "Please enter your Start Location (e.g. Naryn):",
        "end_loc_prompt": "Please enter your Destination (e.g. Bishkek):",
        "date_prompt": "Please enter travel Date (e.g. 25.12.2024):",
        "time_prompt": "Please enter travel Time (24h format, e.g. 14:30):",
        "seats_offer_prompt": "How many seats are available? (Choose below or type a number)",
        "seats_request_prompt": "How many seats do you need? (Choose below or type a number)",
        "car_model_prompt": "What is your Car Model? (e.g. Toyota Camry, Honda Fit)",
        "price_prompt": "What is the price per seat in KGS? (e.g. 500)",
        "summary_offer": "🚗 <b>New Ride Offer Summary</b>\n\n📍 From: {start}\n📍 To: {end}\n📅 Date: {date}\n⏰ Time: {time}\n🪑 Seats: {seats}\n🚘 Car: {car}\n💰 Price: {price} KGS\n\nIs this correct?",
        "summary_request": "🚕 <b>New Ride Request Summary</b>\n\n📍 From: {start}\n📍 To: {end}\n📅 Date: {date}\n⏰ Time: {time}\n🪑 Seats: {seats}\n\nIs this correct?",
        "confirm_button": "Confirm ✅",
        "edit_button": "Edit 📝",
        "published_offer": "Ride Offer Published! 🚀",
        "published_request": "Ride Request Published! 🚕\nSearching for drivers...",
        "error_generic": "Error: {error}",
        "error_date": "Invalid date format. Please use DD.MM.YYYY",
        "error_time": "Invalid time format. Please use HH:MM (24h)",
        "error_number": "Please enter a valid number.",
        "selected": "Selected: {value}",
        "instruction": (
            "<b>Welcome to GoGoGo!</b> 🚕\n\n"
            "This bot matches Drivers 🚗 and Passengers 🧍 for inter-city rides.\n\n"
            "<b>How it works:</b>\n"
            "1. Choose your role (Driver or Passenger).\n"
            "2. Enter your trip details (Location, Date, Time).\n"
            "3. We'll verify your phone number (one time).\n"
            "4. We notify you when a match is found!\n\n"
            "<b>Commands:</b>\n"
            "/start - Start the bot\n"
            "/help - Show this guide\n"
            "/mypost - Show your current active ride\n"
            "/edit - Refile (delete & new) your active ride\n"
            "/stop - Stop/Delete your active ride\n"
            "/changerole - Switch between Driver and Passenger"
        ),
        "mypost_offer": "🚗 <b>Your Last Offer</b>\nFrom: {start}\nTo: {end}\nDate: {date}\nTime: {time}\nFree Seats: {seats}",
        "mypost_request": "🧍 <b>Your Last Request</b>\nFrom: {start}\nTo: {end}\nDate: {date}\nTime: {time}\nSeats Needed: {seats}",
        "mypost_none": "You have no active posts.",
        "refile_prompt": "Found your last {type}.\nDate: {date}\nFrom: {start}\n\nDo you want to delete this and create a new one?",
        "refile_yes": "Yes, Refile ✅",
        "refile_no": "No, Keep ❌",
        "cancelled": "Cancelled.",
        "loc_start": "Start: {value}",
        "loc_dest": "Destination: {value}",
        "date_selected": "Date: {value}",
        "stopped": "Your active ride/request has been stopped and removed. 🛑",
        "kb_today": "Today",
        "kb_tomorrow": "Tomorrow",
    },
    LANG_RU: {
        "welcome_back": "С возвращением, {name}!",
        "welcome_new": "Добро пожаловать в GoGoGo! Пожалуйста, выберите язык:",
        "share_phone": "Пожалуйста, поделитесь своим номером телефона для регистрации.",
        "phone_button": "Поделиться контактом 📱",
        "choose_role": "Регистрация успешна! Выберите роль (можно сменить через /changerole):",
        "driver_button": "Я Водитель 🚗",
        "passenger_button": "Я Пассажир 🧍",
        "driver_action": "Создать Поездку 🚗",
        "passenger_action": "Найти Поездку 🧍",
        "registration_complete": "Регистрация завершена! Чем можем помочь?",
        "cancel_button": "Отмена ❌",
        "role_switched": "Роль изменена на: {role}",
        "start_loc_prompt": "Введите место отправления (например, Нарын):",
        "end_loc_prompt": "Введите место назначения (например, Бишкек):",
        "date_prompt": "Введите дату поездки (например, 25.12.2024):",
        "time_prompt": "Введите время поездки (24ч формат, например 14:30):",
        "seats_offer_prompt": "Сколько мест свободно? (Выберите или введите цифру)",
        "seats_request_prompt": "Сколько мест нужно? (Выберите или введите цифру)",
        "car_model_prompt": "Какая у вас модель машины? (например, Toyota Camry, Honda Fit)",
        "price_prompt": "Цена за место в сомах? (например, 500)",
        "summary_offer": "🚗 <b>Сводка Предложения</b>\n\n📍 Откуда: {start}\n📍 Куда: {end}\n📅 Дата: {date}\n⏰ Время: {time}\n🪑 Мест: {seats}\n🚘 Авто: {car}\n💰 Цена: {price} KGS\n\nВсё верно?",
        "summary_request": "🚕 <b>Сводка Запроса</b>\n\n📍 Откуда: {start}\n📍 Куда: {end}\n📅 Дата: {date}\n⏰ Время: {time}\n🪑 Мест: {seats}\n\nВсё верно?",
        "confirm_button": "Подтвердить ✅",
        "edit_button": "Изменить 📝",
        "published_offer": "Предложение опубликовано! 🚀",
        "published_request": "Запрос опубликован! 🚕\nИщем водителей...",
        "error_generic": "Ошибка: {error}",
        "error_date": "Неверный формат даты. Используйте ДД.ММ.ГГГГ",
        "error_time": "Неверный формат времени. Используйте ЧЧ:ММ (24ч)",
        "error_number": "Введите корректное число.",
        "selected": "Выбрано: {value}",
        "instruction": (
            "<b>Добро пожаловать в GoGoGo!</b> 🚕\n\n"
            "Бот соединяет Водителей 🚗 и Пассажиров 🧍 для междугородних поездок.\n\n"
            "<b>Как это работает:</b>\n"
            "1. Выберите роль (Водитель или Пассажир).\n"
            "2. Введите детали поездки (Место, Дата, Время).\n"
            "3. Подтвердите номер телефона (один раз).\n"
            "4. Мы уведомим вас, когда найдется попутчик!\n\n"
            "<b>Команды:</b>\n"
            "/start - Запуск бота\n"
            "/help - Показать эту справку\n"
            "/mypost - Моя активная поездка\n"
            "/edit - Пересоздать поездку\n"
            "/stop - Остановить/Удалить поездку\n"
            "/changerole - Сменить роль (Водитель/Пассажир)"
        ),
        "mypost_offer": "🚗 <b>Ваше Предложение</b>\nОткуда: {start}\nКуда: {end}\nДата: {date}\nВремя: {time}\nСвободно мест: {seats}",
        "mypost_request": "🧍 <b>Ваш Запрос</b>\nОткуда: {start}\nКуда: {end}\nДата: {date}\nВремя: {time}\nНужно мест: {seats}",
        "mypost_none": "У вас нет активных поездок.",
        "refile_prompt": "Нашли вашу последнюю {type}.\nДата: {date}\nОткуда: {start}\n\nХотите удалить её и создать новую?",
        "refile_yes": "Да, Пересоздать ✅",
        "refile_no": "Нет, Оставить ❌",
        "cancelled": "Отменено.",
        "loc_start": "Старт: {value}",
        "loc_dest": "Назначение: {value}",
        "loc_dest": "Назначение: {value}",
        "date_selected": "Дата: {value}",
        "stopped": "Ваша активная поездка/запрос остановлены и удалены. 🛑",
        "kb_today": "Сегодня",
        "kb_tomorrow": "Завтра",
    },
    LANG_KG: {
        "welcome_back": "Куш келиңиз, {name}!",
        "welcome_new": "GoGoGo'го куш келиңиз! Тилди тандаңыз:",
        "share_phone": "Катталуу үчүн телефон номериңизди бөлүшүңүз.",
        "phone_button": "Телефон номерди бөлүшүү 📱",
        "choose_role": "Каттоо ийгиликтүү! Ролду тандаңыз (кийин /changerole менен алмаштырса болот):",
        "driver_button": "Мен Айдоочумун 🚗",
        "passenger_button": "Мен Жүргүнчүмүн 🧍",
        "driver_action": "Сапар Түзүү 🚗",
        "passenger_action": "Сапар Издөө 🧍",
        "registration_complete": "Каттоо аяктады! Сизге кандай жардам бере алабыз?",
        "cancel_button": "Жокко чыгаруу ❌",
        "role_switched": "Роль өзгөртүлдү: {role}",
        "start_loc_prompt": "Башталуучу жерин жазыңыз (мис. Нарын):",
        "end_loc_prompt": "Баруучу жерин жазыңыз (мис. Бишкек):",
        "date_prompt": "Жөнөө күнүн жазыңыз (мис. 25.12.2024):",
        "time_prompt": "Жөнөө саатын жазыңыз (24-сааттык формат, мис. 14:30):",
        "seats_offer_prompt": "Бош орун канча? (Тандаңыз же жазыңыз)",
        "seats_request_prompt": "Канча орун керек? (Тандаңыз же жазыңыз)",
        "car_model_prompt": "Унааңыздын модели кандай? (мис. Toyota Camry, Honda Fit)",
        "price_prompt": "Орун баасы канча сом? (мис. 500)",
        "summary_offer": "🚗 <b>Сапар Тууралуу</b>\n\n📍 Кайдан: {start}\n📍 Кайда: {end}\n📅 Күнү: {date}\n⏰ Сааты: {time}\n🪑 Орундар: {seats}\n🚘 Унаа: {car}\n💰 Баасы: {price} сом\n\nБаары туурабы?",
        "summary_request": "🚕 <b>Суроо Тууралуу</b>\n\n📍 Кайдан: {start}\n📍 Кайда: {end}\n📅 Күнү: {date}\n⏰ Сааты: {time}\n🪑 Орундар: {seats}\n\nБаары туурабы?",
        "confirm_button": "Ооба, туура ✅",
        "edit_button": "Өзгөртүү 📝",
        "published_offer": "Сапар жарыяланды! 🚀",
        "published_request": "Суроо жарыяланды! 🚕\nАйдоочуларды издеп жатабыз...",
        "error_generic": "Ката: {error}",
        "error_date": "Күн туура эмес жазылды. ДД.ММ.ЖЖЖЖ форматын колдонуңуз",
        "error_time": "Саат туура эмес жазылды. СС:ММ (24с) форматын колдонуңуз",
        "error_number": "Туура сан жазыңыз.",
        "selected": "Тандалды: {value}",
        "instruction": (
            "<b>GoGoGo'го куш келиңиз!</b> 🚕\n\n"
            "Бул бот Айдоочулар 🚗 менен Жүргүнчүлөрдү 🧍 байланыштырат.\n\n"
            "<b>Кантип иштейт:</b>\n"
            "1. Ролду тандаңыз (Айдоочу же Жүргүнчү).\n"
            "2. Сапар маалыматын жазыңыз (Жер, Күн, Саат).\n"
            "3. Телефон номериңизди ырастаңыз (бир жолу).\n"
            "4. Попутчик табылганда кабар беребиз!\n\n"
            "<b>Командалар:</b>\n"
            "/start - Ботту баштоо\n"
            "/help - Жардам\n"
            "/mypost - Менин сапарым\n"
            "/edit - Сапарды жаңылоо\n"
            "/stop - Сапарды токтотуу/өчүрүү\n"
            "/changerole - Ролду алмаштыруу"
        ),
        "mypost_offer": "🚗 <b>Сиздин Сапарыңыз</b>\nКайдан: {start}\nКайда: {end}\nКүнү: {date}\nСааты: {time}\nБош орун: {seats}",
        "mypost_request": "🧍 <b>Сиздин Сурооңуз</b>\nКайдан: {start}\nКайда: {end}\nКүнү: {date}\nСааты: {time}\nОрун керек: {seats}",
        "mypost_none": "Сизде активдүү сапар жок.",
        "refile_prompt": "Сиздин акыркы {type} табылды.\nКүнү: {date}\nКайдан: {start}\n\nМуну өчүрүп, жаңысын түзөсүзб?",
        "refile_yes": "Ооба, Жаңылоо ✅",
        "refile_no": "Жок, Калтыруу ❌",
        "cancelled": "Жокко чыгарылды.",
        "loc_start": "Башталышы: {value}",
        "loc_dest": "Багыты: {value}",
        "loc_dest": "Багыты: {value}",
        "date_selected": "Күнү: {value}",
        "stopped": "Сиздин активдүү сапарыңыз/сурооңуз токтотулду жана өчүрүлдү. 🛑",
        "kb_today": "Бүгүн",
        "kb_tomorrow": "Эртең",
    }
}

def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Get localized string."""
    lang_dict = MESSAGES.get(lang, MESSAGES[DEFAULT_LANG])
    msg = lang_dict.get(key, MESSAGES[DEFAULT_LANG].get(key, key))
    if kwargs:
        return msg.format(**kwargs)
    return msg
