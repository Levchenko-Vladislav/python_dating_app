from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from src.dating_bot.bot.keyboards import agree_kb, main_menu_kb
from src.dating_bot.bot.states import Profile
from src.dating_bot.services.user_service import UserService

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username

    await state.clear()

    # Telegram ID как строка
    telegram_id = str(user_id)

    # Проверяем по Telegram ID
    user_exists = await UserService.check_user_exists(telegram_id)

    if user_exists:
        user_profile = await UserService.get_user_profile(telegram_id)

        if user_profile and user_profile.get('user'):
            user = user_profile['user']

            await state.update_data({
                "name": user.name,
                "age": user.age,
                "city": user.city,
                "photo_id": user.photo_id,
                "is_registered": True,
                "user_id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username if user.username else f"ID: {user_id}"
            })

        await message.answer(
            "Привет! Это MINDY 💫\n"
            "Здесь совпадают не анкеты, а люди 💘\n\n"
            "Пройди короткий психологический тест → я посчитаю точную совместимость →\n"
            "и подберу твоего соулмейта, который уже где-то рядом.\n\n"
            "✅ рекомендации по твоим предпочтениям\n"
            "✅ % совместимости после теста\n"
            "✅ взаимный лайк → предложу Speed Dating\n\n"
            "Что хочешь сделать?",
            reply_markup=main_menu_kb()
        )

    else:
        # Username для отображения
        display_username = f"@{username}" if username else f"ID: {user_id}"

        await state.update_data({
            "username": display_username,  # Для отображения
            "telegram_id": telegram_id,  # Для БД
            "user_id": user_id
        })

        await message.answer(
            "Привет! Это MINDY 💫\n"
            "Здесь совпадают не анкеты, а люди 💘\n\n"
            "Пройди короткий психологический тест → я посчитаю точную совместимость →\n"
            "и подберу твоего соулмейта, который уже где-то рядом.\n\n"
            "✅ рекомендации по твоим предпочтениям\n"
            "✅ % совместимости после теста\n"
            "✅ взаимный лайк → предложу Speed Dating\n\n"
            "Готов(а) заполнить анкету?",
            reply_markup=agree_kb()
        )


@router.message(lambda m: m.text == "да!✨")
async def agree_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = data.get('telegram_id', str(message.from_user.id))

    user_exists = await UserService.check_user_exists(telegram_id)

    if user_exists:
        await message.answer(
            "Вы уже зарегистрированы! Что хочешь сделать?",
            reply_markup=main_menu_kb()
        )
        return

    await message.answer(
        "Отлично! Тогда начнём 😊\nКак тебя зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Profile.name)
    await state.update_data(is_registered=False)


@router.message(lambda m: m.text == "не сейчас")
async def decline_handler(message: Message, state: FSMContext):
    await message.answer(
        "Хорошо 🙂 Если передумаешь — просто напиши /start",
        reply_markup=ReplyKeyboardRemove()
    )