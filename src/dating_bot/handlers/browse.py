from aiogram import Router, F, Bot
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
    from src.dating_bot.services.test_service import TestService
    from src.dating_bot.services.user_service import UserService

    telegram_id = str(message.from_user.id)
    user_profile = await UserService.get_user_profile(telegram_id)

    if not user_profile or not user_profile.get('user'):
        await message.answer(
            "❌ Сначала заполни профиль через /start",
            reply_markup=main_menu_kb()
        )
        return

    user_id = user_profile['user'].id

    # Проверяем в БД, прошел ли пользователь тест
    has_test = await TestService.has_completed_test(user_id)

    # Также проверяем состояние на всякий случай
    state_data = await state.get_data()
    has_test_in_state = state_data.get('test_completed', False)

    if not has_test and not has_test_in_state:
        await message.answer(
            "❌ Сначала пройди психологический тест!\n"
            "Это нужно для точного подбора анкет.",
            reply_markup=main_menu_kb()
        )
        return
    elif has_test and not state_data.get('test_completed'):
        # Обновляем состояние, если тест есть в БД, но не в состоянии
        await state.update_data(test_completed=True)

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
        f"Анкета {current_index + 1} из {len(recommendations)}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="❤️ Лайк", callback_data=f"like_{profile['id']}")
    builder.button(text="❌ Дизлайк", callback_data=f"dislike_{profile['id']}")
    builder.button(text="⏭️ Следующая", callback_data="next_profile")
    builder.button(text="⏹️ Стоп", callback_data="stop_browsing")
    builder.adjust(2)  # 2 кнопки в ряду

    photo_id = profile.get("photo_id")

    if not photo_id:
        await message.answer(
            f"🖼️ {profile_text}",
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )
    else:
        try:
            await message.answer_photo(
                photo=photo_id,
                caption=profile_text,
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка отправки фото: {e}")
            await message.answer(
                f"🖼️ {profile_text}\n\n"
                f"_Фото временно недоступно_",
                reply_markup=builder.as_markup(),
                parse_mode="Markdown"
            )

    await state.update_data(current_index=current_index + 1)


@router.callback_query(F.data == "next_profile")
async def next_profile_handler(callback: CallbackQuery, state: FSMContext):
    """Показать следующую анкету"""
    await callback.answer("Загружаю следующую анкету...", show_alert=False)
    await show_next_profile(callback.message, state)


@router.callback_query(F.data.startswith("like_"))
async def process_like(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик лайка с уведомлением второго пользователя"""
    try:
        await callback.answer("❤️ Лайк отправлен!", show_alert=False)

        # Извлекаем ID профиля
        profile_id = int(callback.data.split("_")[1])

        # Обновляем кнопку
        builder = InlineKeyboardBuilder()
        builder.button(text="❤️ Вы лайкнули", callback_data="already_liked")
        builder.button(text="❌ Дизлайк", callback_data=f"dislike_{profile_id}")
        builder.button(text="⏭️ Следующая", callback_data="next_profile")
        builder.adjust(2)

        try:
            await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
        except Exception:
            pass

        # Сохраняем лайк в БД
        match_result = await recommendation_service.like_profile(
            callback.from_user.id,
            profile_id
        )

        print(f"📥 Результат лайка: {match_result}")

        if match_result.get("is_mutual"):
            # 1. Уведомляем текущего пользователя
            await callback.message.answer(
                f"🎉 {match_result['message']}",
                parse_mode="Markdown"
            )

            # 2. Уведомляем второго пользователя (если есть telegram_id)
            matched_with = match_result.get("matched_with", {})
            second_user_telegram_id = matched_with.get("telegram_id")

            if second_user_telegram_id:
                try:
                    # Находим информацию о первом пользователе
                    from src.dating_bot.services.user_service import UserService
                    first_user_profile = await UserService.get_user_profile(str(callback.from_user.id))

                    if first_user_profile and first_user_profile.get('user'):
                        first_user = first_user_profile['user']

                        # Отправляем уведомление второму пользователю
                        await bot.send_message(
                            chat_id=int(second_user_telegram_id),
                            text=f"🎉 У вас взаимная симпатия с {first_user.name}! Начнем Speed Dating?\n\n"
                                 f"💞 Посмотреть все мэтчи можно в главном меню!",
                            reply_markup=main_menu_kb()
                        )
                        print(f"✅ Уведомление отправлено пользователю {second_user_telegram_id}")
                except Exception as e:
                    print(f"❌ Ошибка отправки уведомления: {e}")

            # Показываем меню
            await callback.message.answer(
                "Что хочешь сделать дальше?",
                reply_markup=main_menu_kb()
            )
            await state.clear()
            return

        # Показываем следующую анкету
        await asyncio.sleep(1)
        await show_next_profile(callback, state)

    except Exception as e:
        print(f"❌ Ошибка в process_like: {e}")
        import traceback
        traceback.print_exc()
        await callback.answer("❌ Ошибка при обработке лайка", show_alert=True)


@router.callback_query(F.data.startswith("dislike_"))
async def process_dislike(callback: CallbackQuery, state: FSMContext):
    """Обработчик дизлайка"""
    try:
        print(f"DEBUG: Нажата кнопка дизлайка, данные: {callback.data}")

        # Сразу отвечаем Telegram
        await callback.answer("❌ Дизлайк отправлен", show_alert=False)

        # Извлекаем ID профиля
        profile_id = int(callback.data.split("_")[1])
        print(f"DEBUG: Profile ID из callback: {profile_id}")
        print(f"DEBUG: User ID (Telegram): {callback.from_user.id}")

        # Обновляем кнопку
        builder = InlineKeyboardBuilder()
        builder.button(text="❤️ Лайк", callback_data=f"like_{profile_id}")
        builder.button(text="❌ Пропущено", callback_data="already_disliked")
        builder.button(text="⏭️ Следующая", callback_data="next_profile")
        builder.adjust(2)

        # Редактируем сообщение
        try:
            await callback.message.edit_reply_markup(
                reply_markup=builder.as_markup()
            )
        except Exception as e:
            print(f"DEBUG: Ошибка редактирования сообщения: {e}")
            pass

        # Сохраняем дизлайк в БД
        result = await recommendation_service.dislike_profile(
            callback.from_user.id,
            profile_id
        )

        print(f"DEBUG: Результат dislike_profile: {result}")

        if not result.get("success"):
            await callback.answer(f"Ошибка: {result.get('message', 'Неизвестная ошибка')}", show_alert=True)

        # Показываем следующую анкету
        await asyncio.sleep(1)
        await show_next_profile(callback, state)

    except Exception as e:
        print(f"Ошибка в process_dislike: {e}")
        import traceback
        traceback.print_exc()
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

@router.callback_query(F.data == "stop_browsing")
async def stop_browsing(callback: CallbackQuery, state: FSMContext):
    """Остановить просмотр анкет"""
    await callback.answer("Просмотр остановлен", show_alert=False)
    await callback.message.answer(
        "Просмотр анкет остановлен. Что хочешь сделать дальше?",
        reply_markup=main_menu_kb()
    )
    await state.clear()