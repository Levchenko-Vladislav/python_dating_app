from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def agree_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="да!✨")],
            [KeyboardButton(text="не сейчас")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True)
def gender_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Женщина 👩"), KeyboardButton(text="Мужчина 🧑")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def edit_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Имя"), KeyboardButton(text="🎂 Возраст")],
            [KeyboardButton(text="📍 Город"), KeyboardButton(text="⚧ Пол")],
            [KeyboardButton(text="🎯 Цель"), KeyboardButton(text="🔍 Кого ищешь")],
            [KeyboardButton(text="💬 Ник"), KeyboardButton(text="📸 Фото")],
            [KeyboardButton(text="↩️ Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def goal_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💘 Отношения")],
            [KeyboardButton(text="🫂 Дружба")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def target_gender_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужчину 👱‍♂️"), KeyboardButton(text="Женщину 👩")],
            [KeyboardButton(text="Не важно 👩👱‍♂️")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
def confirm_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Всё верно")],
            [KeyboardButton(text="✏️ Изменить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def test_ready_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Да!")],
            [KeyboardButton(text="⏳ Позже")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def test_answer_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="1️⃣ - Совсем не согласен"),
                KeyboardButton(text="2️⃣ - Скорее не согласен"),
            ],
            [
                KeyboardButton(text="3️⃣ - Иногда/Нейтрально"),
                KeyboardButton(text="4️⃣ - Скорее согласен"),
            ],
            [
                KeyboardButton(text="5️⃣ - Полностью согласен"),
                KeyboardButton(text="⏭️ Пропустить вопрос"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def start_test_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Начать тест")],
            [KeyboardButton(text="⏳ Не сейчас")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def test_results_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👀 Смотреть анкеты")],
            [KeyboardButton(text="✏️ Изменить профиль"), KeyboardButton(text="🔄 Перепройти тест")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def confirm_retake_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Да, начать заново")],
            [KeyboardButton(text="❌ Нет, отменить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧠 Пройти тест")],
            [KeyboardButton(text="✏️ Редактировать профиль"), KeyboardButton(text="👀 Мой профиль")],
            [KeyboardButton(text="🔍 Начать поиск")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def browse_or_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👀 Смотреть анкеты")],
            [KeyboardButton(text="📋 Главное меню")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def username_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📨 Отправить мой username")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )