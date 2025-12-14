from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from dating_bot.bot.keyboards import agree_kb
from dating_bot.bot.states import Profile


router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Привет! Это MINDY 💫\n"
        "Здесь совпадают не анкеты, а люди 💘\n\n"
        "Пройди короткий психологический тест → я посчитаю точную совместимость →\n"
        "и подберу твоего соулмейта, который уже где-то рядом.\n\n"
        "✅ рекомендации по твоим предпочтениям\n"
        "✅ % совместимости после теста\n"
        "✅ взаимный лайк → предложу Speed Dating\n\n"
        "Готов(а) заполнить анкету?",
        reply_markup=agree_kb(),

    )


@router.message(lambda m: m.text == "да!✨")
async def agree_handler(message: Message, state: FSMContext):
    await message.answer(
        "Отлично! Тогда начнём 😊\nКак тебя зовут?",
        reply_markup = ReplyKeyboardRemove()
    )
    await state.set_state(Profile.name)


@router.message(lambda m: m.text == "не сейчас")
async def decline_handler(message: Message):
    await message.answer(
        "Хорошо 🙂 Если передумаешь — просто напиши /start",
        reply_markup = ReplyKeyboardRemove()
    )
