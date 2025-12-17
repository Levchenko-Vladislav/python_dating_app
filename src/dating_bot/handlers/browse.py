from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.dating_bot.services.recommendations import RecommendationService
from src.dating_bot.bot.states import BrowsingState
from src.dating_bot.bot.keyboards import main_menu_kb

router = Router()
recommendation_service = RecommendationService()


@router.message(F.text == "👀 Смотреть анкеты")
async def start_browsing(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("test_completed"):
        await message.answer(
            "❌ Сначала пройди психологический тест!\n"
            "Это нужно для точного подбора анкет.",
            reply_markup=main_menu_kb()
        )
        return
    await message.answer(
        "🔍 *Ищу подходящие анкеты...*\n\n"
        "Сейчас покажу людей с максимальной совместимостью!",
        parse_mode="Markdown"
    )
    recommendations = await recommendation_service.get_recommendations(
        user_id=message.from_user.id,
        limit=5
    )
    if not recommendations:
        await message.answer(
            "😔 Пока нет подходящих анкет.\n"
            "Загляни позже!",
            reply_markup=main_menu_kb()
        )
        return
    await state.update_data(
        recommendations=recommendations,
        current_index=0,
        viewed_profiles=[]
    )
    await show_next_profile(message, state)


async def show_next_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    recommendations = data.get("recommendations", [])
    current_index = data.get("current_index", 0)
    if current_index >= len(recommendations):
        await message.answer(
            "🎯 На сегодня это все анкеты!\n"
            "Загляни завтра, будут новые люди 😊",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return
    profile = recommendations[current_index]
    profile_text = (
        f"👤 *{profile['name']}, {profile['age']}*\n"
        f"📍 {profile['city']}\n"
        f"🎯 {profile['goal']}\n"
        f"💫 *Совместимость: {profile['compatibility']}%*\n\n"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="❤️ Лайк", callback_data=f"like_{profile['id']}")
    builder.button(text="❌ Дизлайк", callback_data=f"dislike_{profile['id']}")
    builder.adjust(2) 
    await message.answer_photo(
        photo=profile["photo_id"],
        caption=profile_text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await state.update_data(current_index=current_index + 1)


@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery, state: FSMContext):
    profile_id = int(callback.data.split("_")[1])
    result = await recommendation_service.like_profile(
        user_id=callback.from_user.id,
        liked_profile_id=profile_id
    )
    await callback.answer(result["message"])
    if result["is_mutual"]:
        await callback.message.answer(
            f"🎉 *Взаимная симпатия с {result['matched_profile']['name']}!*\n\n"
            "Хочешь начать Speed Dating?\n"
            "Это 5 вопросов чтобы лучше узнать друг друга!",
            reply_markup=InlineKeyboardBuilder()
                .button(text="🚀 Начать Speed Dating", callback_data="start_speed_dating")
                .button(text="Позже", callback_data="skip_speed_dating")
                .as_markup(),
            parse_mode="Markdown"
        )
    await show_next_profile(callback.message, state)


@router.callback_query(F.data.startswith("dislike_"))
async def process_dislike(callback: CallbackQuery, state: FSMContext):
    profile_id = int(callback.data.split("_")[1])
    await recommendation_service.dislike_profile(
        user_id=callback.from_user.id,
        disliked_profile_id=profile_id
    )
    await callback.answer("👎 Запомнил, больше не покажу")
    await show_next_profile(callback.message, state)

@router.callback_query(F.data == "start_speed_dating")
async def start_speed_dating(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Скоро реализуем Speed Dating!")
    await callback.message.answer(
        "🚀 *Speed Dating*\n\n"
        "Эта функция в разработке!\n"
        "Скоро сможете задавать 5 вопросов друг другу.",
        parse_mode="Markdown"
    )