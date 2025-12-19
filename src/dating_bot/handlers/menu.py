from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.dating_bot.bot.states import Profile
from src.dating_bot.bot.keyboards import edit_menu_kb, main_menu_kb

# Импорты для работы с БД
from src.dating_bot.services.user_service import UserService
from src.dating_bot.services.test_service import TestService
from src.dating_bot.utils.data_mappers import map_gender_to_ui, map_target_gender_to_ui
from src.dating_bot.utils.data_mappers import map_goal_to_db, map_goal_to_ui

router = Router()


@router.message(F.text == "🧠 Пройти тест")
async def start_test_from_menu(message: Message, state: FSMContext):
    from src.dating_bot.handlers.psychological_test import start_test_command
    await start_test_command(message, state)


@router.message(F.text == "👀 Мой профиль")
async def show_my_profile_menu(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)

    # Получаем данные из БД
    user_profile_data = await UserService.get_user_profile(telegram_id)

    if user_profile_data and user_profile_data.get('user'):
        user = user_profile_data['user']

        # Проверяем в БД, прошел ли пользователь тест
        has_completed_test = await TestService.has_completed_test(user.id)

        # Получаем данные из состояния (для полей, которых нет в БД)
        state_data = await state.get_data()
        goal_text = map_goal_to_ui(user.goal) if user.goal else "Не указано"

        # Определяем статус теста
        test_status = "✅ Тест пройден" if has_completed_test else "❌ Тест не пройден"

        # Если тест пройден, получаем результаты
        test_results_text = ""
        if has_completed_test:
            test_results = await TestService.get_user_test_results(user.id)
            if test_results and test_results.get('category_scores'):
                from src.dating_bot.services.test_calculator import format_results_for_display
                test_results_text = f"\n\n*Результаты теста:*\n{format_results_for_display(test_results['category_scores'])}"

        profile_text = (
            "👤 *Твой профиль:*\n\n"
            f"• Имя: {user.name}\n"
            f"• Возраст: {user.age if user.age else '—'}\n"
            f"• Город: {user.city if user.city else '—'}\n"
            f"• Пол: {map_gender_to_ui(user.sex) if user.sex else '—'}\n"
            f"• Цель: {goal_text}\n"
            f"• Ищу: {map_target_gender_to_ui(user.search_sex) if user.search_sex else '—'}\n"
            f"{test_status}"
            f"{test_results_text}"
        )

        photo_id = user.photo_id if user.photo_id else state_data.get('photo_id')

        if photo_id:
            await message.answer_photo(
                photo=photo_id,
                caption=profile_text,
                parse_mode="Markdown"
            )
        else:
            await message.answer(profile_text, parse_mode="Markdown")

        await message.answer(
            "Выбери действие:",
            reply_markup=main_menu_kb()
        )
    else:
        # Если нет в БД, проверяем состояние
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