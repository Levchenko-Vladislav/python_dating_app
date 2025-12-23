from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
import asyncio
from typing import Optional
import logging
from src.dating_bot.bot.states import SpeedDatingState
from src.dating_bot.bot.keyboards import (
    speed_dating_start_kb, 
    speed_dating_session_kb,
    speed_dating_question_kb,
    main_menu_kb
)
from src.dating_bot.services.speed_dating_service import SpeedDatingService
from src.dating_bot.services.user_service import UserService
from src.dating_bot.services.like_service import LikeService
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

router = Router()
logger = logging.getLogger(__name__)


async def get_user_db_id(telegram_id: int) -> Optional[int]:
    profile = await UserService.get_user_profile(str(telegram_id))
    if profile and profile.get('user'):
        return profile['user'].id
    return None


@router.message(F.text == "💞 Мои мэтчи")
async def show_matches_with_speed_dating(message: Message, state: FSMContext):
    user_db_id = await get_user_db_id(message.from_user.id)
    if not user_db_id:
        await message.answer("Ошибка: пользователь не найден")
        return
    matches = await LikeService.get_user_matches(message.from_user.id)
    
    if not matches:
        await message.answer(
            "😔 У тебя пока нет взаимных симпатий.\n"
            "Продолжай смотреть анкеты — твой идеальный партнер где-то рядом!",
            reply_markup=main_menu_kb()
        )
        return

    filtered_matches = []
    for match in matches:
        if match['user']['id'] != user_db_id:  # Пропускаем себя
            filtered_matches.append(match)
    
    if not filtered_matches:
        await message.answer(
            "😔 Нет доступных мэтчей для спиддейтинга.",
            reply_markup=main_menu_kb()
        )
        return

    header = f"💞 <b>Твои взаимные симпатии ({len(filtered_matches)})</b>\n\n"
    header += "Вот люди, которые тоже заинтересовались тобой:\n\n"
    
    await message.answer(header, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())

    for i, match in enumerate(filtered_matches[:5], 1):
        user = match['user']
        
        match_text = (
            f"<b>{i}.</b> 👤 <b>{user['name']}</b>, {user['age']} лет\n" 
            f"📍 {user['city']}\n"
            f"💬 {user['username'] if user['username'] else 'Без username'}\n"
            f"💘 Совпали: {match['matched_at'].strftime('%d.%m.%Y')}"
        )
        
        if user.get('photo_id'):
            try:
                await message.answer_photo(
                    photo=user['photo_id'],
                    caption=match_text,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Ошибка отправки фото: {e}")
                await message.answer(match_text, parse_mode="HTML")
        else:
            await message.answer(match_text, parse_mode="HTML")

    await message.answer(
        "💬 Хочешь начать Speed Dating с одним из твоих мэтчей?\n"
        "Введите номер мэтча (1, 2, 3...):",
        reply_markup=ReplyKeyboardRemove()
    )
    
    await state.update_data(matches=filtered_matches)
    await state.set_state(SpeedDatingState.waiting_start)

@router.message(SpeedDatingState.waiting_start, F.text.regexp(r'^\d+$'))
async def select_match_for_speed_dating(message: Message, state: FSMContext):

    data = await state.get_data()
    matches = data.get('matches', [])
    
    try:
        match_num = int(message.text) - 1
        if 0 <= match_num < len(matches):
            selected_match = matches[match_num]
            

            await state.update_data(selected_match=selected_match)
            partner_name = selected_match['user']['name']
            partner_id = selected_match['user']['id']
            await message.answer(
                f"Выбран мэтч с <b>{partner_name}</b>!\n\n"
                "Хотите начать Speed Dating?\n"
                "Вы будете отвечать на 5 случайных вопросов по очереди 🙃",
                parse_mode="HTML",
                reply_markup=speed_dating_start_kb()
            )

            await state.set_state(SpeedDatingState.waiting_confirmation)  
        else:
            await message.answer(
                f"Пожалуйста, введите число от 1 до {len(matches)}"
            )
    except ValueError:
        await message.answer("Пожалуйста, введите номер мэтча (число)")


@router.message(F.text == "🚀 Начать спиддейтинг")
async def start_or_join_speed_dating(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()
    selected_match = data.get("selected_match")

    user_db_id = await get_user_db_id(message.from_user.id)
    if not user_db_id:
        await message.answer("Ошибка: пользователь не найден")
        return

    if selected_match:
        result = await SpeedDatingService.start_speed_dating(
            selected_match["match_id"]
        )
    else:
        result = await SpeedDatingService.join_active_session(user_db_id)

    if not result.get("success"):
        await message.answer(
            "Не удалось начать Speed Dating. Попробуй заново из мэтчей.",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return

    session = result["session"]
    users = result["users"]

    if user_db_id == users["user1"]["id"]:
        current_user = users["user1"]
        other_user = users["user2"]
    else:
        current_user = users["user2"]
        other_user = users["user1"]

    await state.update_data(
            session_id=session.id,
            partner_id=other_user["id"],
            partner_telegram_id=other_user["telegram_id"],
            partner_name=other_user["name"],
            partner_username=other_user.get("username"),
            my_username=message.from_user.username,
            current_user_name=current_user["name"],
            current_user_id=user_db_id
        )


    current_question = await SpeedDatingService.get_current_question(session.id)
    if not current_question.get("success"):
        await message.answer("Ошибка: не удалось получить вопрос", reply_markup=main_menu_kb())
        await state.clear()
        return

    text = (
        f"🚀 <b>Speed Dating начался!</b>\n\n"
        f"💬 <b>Вопрос {current_question['question_number']} из 5:</b>\n"
        f"<i>{current_question['question']}</i>\n\n"
        f"✍️ <b>Я покажу ответы, когда ответят двое!</b>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=speed_dating_question_kb())
    await state.set_state(SpeedDatingState.waiting_answer)
    partner_telegram_id = other_user["telegram_id"]
    partner_state = FSMContext(
        storage=state.storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=int(partner_telegram_id),
            user_id=int(partner_telegram_id)
        )
    )
    await partner_state.update_data(
        session_id=session.id,
        partner_id=user_db_id,
        partner_telegram_id=message.from_user.id,
        partner_name=current_user["name"],
        current_user_name=other_user["name"],
        current_user_id=other_user["id"],
    )

    await bot.send_message(int(partner_telegram_id), text, parse_mode="HTML", reply_markup=speed_dating_question_kb())
    await partner_state.set_state(SpeedDatingState.waiting_answer)

@router.message(SpeedDatingState.waiting_start, F.text == "⏳ Позже")
async def postpone_speed_dating(message: Message, state: FSMContext):
    """Отложить спиддейтинг"""
    await message.answer(
        "Хорошо, Speed Dating можно начать позже из раздела 'Мои мэтчи' 💞",
        reply_markup=main_menu_kb()
    )
    await state.clear()


@router.message(SpeedDatingState.waiting_answer, F.text == "📝 Написать ответ")
async def prompt_for_answer(message: Message, state: FSMContext):
    """Пользователь хочет написать ответ"""
    await message.answer(
        "Напишите свой ответ в чат, затем нажмите '📤 Отправить ответ'",
        reply_markup=speed_dating_session_kb(show_send_button=True)
    )


@router.message(SpeedDatingState.waiting_answer, F.text == "📤 Отправить ответ")
async def submit_answer_handler(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    session_id = data.get("session_id")
    user_answer = data.get("current_answer")

    if not user_answer:
        await message.answer(
            "Сначала напишите ответ в чат, затем нажмите '📤 Отправить ответ'",
            reply_markup=speed_dating_session_kb(show_send_button=True)
        )
        return

    if not session_id:
        await message.answer("Сессия не найдена", reply_markup=main_menu_kb())
        await state.clear()
        return

    user_db_id = await get_user_db_id(message.from_user.id)
    if not user_db_id:
        await message.answer("Ошибка: пользователь не найден")
        return

    result = await SpeedDatingService.submit_answer(session_id, user_db_id, user_answer)

    if not result.get("success"):
        await message.answer(
            f"Ошибка при отправке ответа: {result.get('message', 'Неизвестная ошибка')}",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return

    await state.update_data(current_answer=None)

    question_completed = result.get("question_completed")
    q_idx = result.get("completed_question_index")

    if not question_completed:
        await message.answer(
            "✅ Ответ сохранён! Ждём, пока партнёр тоже ответит…",
            reply_markup=speed_dating_session_kb()
        )
        await state.set_state(SpeedDatingState.partner_waiting)
        return

    data = await state.get_data()
    partner_telegram_id = data.get("partner_telegram_id")
    partner_id = data.get("partner_id")

    info = await SpeedDatingService.get_session_info(session_id)
    if info.get("success") and q_idx is not None and partner_telegram_id:
        session_obj = info["session"]

        answers_pair = (session_obj.answers or {}).get(str(q_idx), {})
        real_partner_id = session_obj.user2_id if session_obj.user1_id == user_db_id else session_obj.user1_id

        my_text = answers_pair.get(str(user_db_id))
        partner_text = answers_pair.get(str(real_partner_id))

        if partner_text:
            await message.answer(
                f"💬 Ответ партнёра:\n<i>{partner_text}</i>",
                parse_mode="HTML"
            )

        if my_text:
            await bot.send_message(
                chat_id=int(partner_telegram_id),
                text=f"💬 Ответ партнёра:\n<i>{my_text}</i>",
                parse_mode="HTML"
            )
    if result.get("is_completed"):
        info = await SpeedDatingService.get_session_info(session_id)
        if info.get("success"):
            user1 = info["users"]["user1"]
            user2 = info["users"]["user2"]

            if user1.id == user_db_id:
                me = user1
                partner = user2
            else:
                me = user2
                partner = user1

            partner_tag = f"{partner.username}" if getattr(partner, "username", None) else "ник не указан"
            my_tag = f"{me.username}" if getattr(me, "username", None) else "ник не указан"

            text_me = (
                "🎉 <b>Speed Dating завершён!</b>\n\n"
                f"✨ Ваш собеседник: {partner_tag}\n\n"
                "Теперь вы можете задавать друг другу любые вопросы и продолжать общение 💬\n"
                "Приятного вам общения! Надеюсь, у вас всё сложится 🤍"
            )

            text_partner = (
                "🎉 <b>Speed Dating завершён!</b>\n\n"
                f"✨ Ваш собеседник: {my_tag}\n\n"
                "Теперь вы можете задавать друг другу любые вопросы и продолжать общение 💬\n"
                "Приятного вам общения! Надеюсь, у вас всё сложится 🤍"
            )

            await message.answer(text_me, parse_mode="HTML", reply_markup=main_menu_kb())

            if partner_telegram_id:
                await bot.send_message(
                    chat_id=int(partner_telegram_id),
                    text=text_partner,
                    parse_mode="HTML",
                    reply_markup=main_menu_kb()
                )

        await state.clear()
        return

    next_question = await SpeedDatingService.get_current_question(session_id)

    next_text = (
        f"💬 <b>Вопрос {next_question['question_number']} из {next_question['total_questions']}:</b>\n"
        f"<i>{next_question['question']}</i>\n\n"
        f"✍️ <b>Ответьте оба. Я покажу ответы, когда ответят двое.</b>"
    )

    await message.answer(next_text, parse_mode="HTML", reply_markup=speed_dating_question_kb())
    await state.set_state(SpeedDatingState.waiting_answer)

    if partner_telegram_id:
        await bot.send_message(
            chat_id=int(partner_telegram_id),
            text=next_text,
            parse_mode="HTML",
            reply_markup=speed_dating_question_kb()
        )

        partner_state = FSMContext(
            storage=state.storage,
            key=StorageKey(
                bot_id=bot.id,
                chat_id=int(partner_telegram_id),
                user_id=int(partner_telegram_id)
            )
        )
        await partner_state.set_state(SpeedDatingState.waiting_answer)
        await partner_state.update_data(current_answer=None)



@router.message(
    SpeedDatingState.waiting_answer,
    F.text,
    ~F.text.in_(["📝 Написать ответ", "📤 Отправить ответ", "⏹ Приостановить знакомство"])
)
async def save_answer_text(message: Message, state: FSMContext):
    await state.update_data(current_answer=message.text)
    await message.answer(
        f"✅ Ответ сохранен!\n\n"
        f"Ваш ответ: <i>{message.text}</i>\n\n"
        f"Нажмите '📤 Отправить ответ' чтобы отправить его партнеру.",
        parse_mode="HTML",
        reply_markup=speed_dating_session_kb(show_send_button=True)
    )


@router.message(
    StateFilter(SpeedDatingState.waiting_answer, SpeedDatingState.partner_waiting, SpeedDatingState.in_session),
    F.text == "⏹ Приостановить знакомство"
)
async def cancel_speed_dating(message: Message, state: FSMContext, bot: Bot):
    """Приостановить знакомство"""
    data = await state.get_data()
    session_id = data.get('session_id')
    partner_telegram_id = data.get('partner_telegram_id')
    partner_name = data.get('partner_name')
    
    if session_id:
        await SpeedDatingService.cancel_session(session_id)

        if partner_telegram_id:
            try:
                await bot.send_message(
                    chat_id=int(partner_telegram_id),
                    text=f"❌ {message.from_user.first_name} приостановил(а) знакомство.\n"
                         "Speed Dating завершен.",
                    reply_markup=main_menu_kb()
                )
            except Exception as e:
                print(f"Ошибка уведомления партнера: {e}")
    
    await message.answer(
        "❌ Знакомство приостановлено.\n"
        "Вы вернулись в главное меню.",
        reply_markup=main_menu_kb()
    )
    await state.clear()


@router.message(SpeedDatingState.partner_waiting)
async def partner_is_answering(message: Message, state: FSMContext):
    if message.text != "⏹ Приостановить знакомство":
        await message.answer(
            "Пожалуйста, подождите, пока партнер ответит на вопрос.",
            reply_markup=speed_dating_session_kb()
        )