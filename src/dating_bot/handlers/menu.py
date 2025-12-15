from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.dating_bot.bot.states import Profile
from src.dating_bot.bot.keyboards import edit_menu_kb, main_menu_kb

router = Router()

@router.message(F.text == "🧠 Пройти тест")
async def start_test_from_menu(message: Message, state: FSMContext):
    from src.dating_bot.handlers.psychological_test import start_test_command
    await start_test_command(message, state)

@router.message(F.text == "👀 Мой профиль")
async def show_my_profile_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("photo_id"):
        await message.answer_photo(
            photo=data["photo_id"],
            caption=(
                "👤 *Твой профиль:*\n\n"
                f"• Имя: {data.get('name', '—')}\n"
                f"• Возраст: {data.get('age', '—')}\n"
                f"• Город: {data.get('city', '—')}\n"
                f"• Пол: {data.get('gender', '—')}\n"
                f"• Цель: {data.get('goal', '—')}\n"
                f"• Ищу: {data.get('target_gender', '—')}\n"
                f"• Телеграм: {data.get('username', '—')}\n\n"
                f"{'✅ Тест пройден' if data.get('test_completed') else '❌ Тест не пройден'}"
            ),
            parse_mode="Markdown"
        )
        await message.answer(
            "Выбери действие:",
            reply_markup=main_menu_kb()
        )
    else:
        await message.answer("Профиль не заполнен. Напиши /start")

@router.message(F.text == "🔍 Начать поиск")
async def start_search_menu(message: Message, state: FSMContext):
    await message.answer(
        "🔍 *Поиск совместимых людей*\n\n"
        "Эта функция скоро будет доступна!\n"
        "Сейчас мы работаем над алгоритмом подбора.",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )