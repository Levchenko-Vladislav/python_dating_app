from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.dating_bot.services.recommendations import RecommendationService
from src.dating_bot.bot.states import BrowsingState
from src.dating_bot.bot.keyboards import main_menu_kb

import asyncio

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
    photo_id = profile.get("photo_id")
    
    if not photo_id:
        # Если фото нет - отправляем только текст с иконкой фото
        await message.answer(
            f"🖼️ {profile_text}",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    else:
        try:
            # Пробуем отправить фото
            await message.answer_photo(
                photo=photo_id,
                caption=profile_text,
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )
        except Exception as e:
            # Если ошибка (неправильный photo_id, фото удалено и т.д.)
            print(f"Ошибка отправки фото: {e}")
            
            # Отправляем текстовую версию с иконкой
            await message.answer(
                f"🖼️ {profile_text}\n\n"
                f"_Фото временно недоступно_",
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )
    await state.update_data(current_index=current_index + 1)


@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery, state: FSMContext):
    """Обработчик лайка"""
    try:
        # Сразу отвечаем Telegram, чтобы убрать "loading..."
        await callback.answer("❤️ Лайк отправлен!", show_alert=False)
        
        # Извлекаем ID профиля
        profile_id = int(callback.data.split("_")[1])
        
        # Обновляем кнопку
        builder = InlineKeyboardBuilder()
        builder.button(text="❤️ Вы лайкнули", callback_data="already_liked")
        builder.button(text="❌ Дизлайк", callback_data=f"dislike_{profile_id}")
        builder.adjust(2)
        
        # Редактируем сообщение
        try:
            await callback.message.edit_reply_markup(
                reply_markup=builder.as_markup()
            )
        except Exception:
            pass  # Игнорируем ошибки редактирования
        
        # Сохраняем лайк в БД (заглушка)
        print(f"Пользователь {callback.from_user.id} лайкнул профиль {profile_id}")
        
        # Проверяем на взаимный лайк
        match_result = await recommendation_service.like_profile(
            callback.from_user.id, 
            profile_id
        )
        
        if match_result.get("is_mutual"):
            # Если взаимный лайк - уведомляем пользователя
            await callback.message.answer(
                f"🎉 {match_result['message']}",
                parse_mode="Markdown"
            )
        
        # Показываем следующую анкету через секунду
        await asyncio.sleep(1)
        await continue_browsing(callback, state)
        
    except Exception as e:
        print(f"Ошибка в process_like: {e}")
        await callback.answer("❌ Ошибка при обработке лайка", show_alert=True)


@router.callback_query(F.data.startswith("dislike_"))
async def process_dislike(callback: CallbackQuery, state: FSMContext):
    """Обработчик дизлайка"""
    try:
        # Сразу отвечаем Telegram
        await callback.answer("❌ Дизлайк отправлен", show_alert=False)
        
        # Извлекаем ID профиля
        profile_id = int(callback.data.split("_")[1])
        
        # Обновляем кнопку
        builder = InlineKeyboardBuilder()
        builder.button(text="❤️ Лайк", callback_data=f"like_{profile_id}")
        builder.button(text="❌ Пропущено", callback_data="already_disliked")
        builder.adjust(2)
        
        # Редактируем сообщение
        try:
            await callback.message.edit_reply_markup(
                reply_markup=builder.as_markup()
            )
        except Exception:
            pass
        
        # Сохраняем дизлайк (заглушка)
        print(f"Пользователь {callback.from_user.id} дизлайкнул профиль {profile_id}")
        
        # Показываем следующую анкету
        await asyncio.sleep(1)
        await continue_browsing(callback, state)
        
    except Exception as e:
        print(f"Ошибка в process_dislike: {e}")
        await callback.answer("❌ Ошибка при обработке дизлайка", show_alert=True)


@router.callback_query(F.data.in_(["already_liked", "already_disliked"]))
async def handle_already_action(callback: CallbackQuery):
    """Обработка повторного нажатия на уже выполненное действие"""
    await callback.answer("Вы уже выполнили это действие", show_alert=False)

@router.callback_query(F.data == "start_speed_dating")
async def start_speed_dating(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Скоро реализуем Speed Dating!")
    await callback.message.answer(
        "🚀 *Speed Dating*\n\n"
        "Эта функция в разработке!\n"
        "Скоро сможете задавать 5 вопросов друг другу.",
        parse_mode="Markdown"
    )