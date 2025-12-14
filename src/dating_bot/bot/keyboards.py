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
            [KeyboardButton(text="📝Да!")],
            [KeyboardButton(text="⏳ Позже")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
