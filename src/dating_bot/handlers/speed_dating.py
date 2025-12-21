from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
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

router = Router()
logger = logging.getLogger(__name__)


async def get_user_db_id(telegram_id: int) -> Optional[int]:
    """Получить ID пользователя в БД по telegram_id"""
    profile = await UserService.get_user_profile(str(telegram_id))
    if profile and profile.get('user'):
        return profile['user'].id
    return None


@router.message(F.text == "💞 Мои мэтчи")
async def show_matches_with_speed_dating(message: Message, state: FSMContext):
    """Показать мэтчи с возможностью начать спиддейтинг"""
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
        # match['user'] - это другой пользователь в мэтче
        if match['user']['id'] != user_db_id:  # Пропускаем себя
            filtered_matches.append(match)
    
    if not filtered_matches:
        await message.answer(
            "😔 Нет доступных мэтчей для спиддейтинга.",
            reply_markup=main_menu_kb()
        )
        return

    # Используем HTML разметку
    header = f"💞 <b>Твои взаимные симпатии ({len(matches)})</b>\n\n"
    header += "Вот люди, которые тоже заинтересовались тобой:\n\n"
    
    await message.answer(header, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    
    for i, match in enumerate(matches[:5], 1):  # ← enumerate с 1
        user = match['user']
        
        match_text = (
            f"<b>{i}.</b> 👤 <b>{user['name']}</b>, {user['age']} лет\n"  # ← Добавили номер
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
    
    # Предлагаем начать спиддейтинг
    await message.answer(
        "💬 Хочешь начать Speed Dating с одним из твоих мэтчей?\n"
        "Введите номер мэтча (1, 2, 3...):",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Сохраняем мэтчи в состояние
    await state.update_data(matches=filtered_matches)
    await state.set_state(SpeedDatingState.waiting_start)

@router.message(SpeedDatingState.waiting_start, F.text.regexp(r'^\d+$'))
async def select_match_for_speed_dating(message: Message, state: FSMContext):
    """Выбрать мэтч для спиддейтинга"""
    data = await state.get_data()
    matches = data.get('matches', [])
    
    try:
        match_num = int(message.text) - 1
        if 0 <= match_num < len(matches):
            selected_match = matches[match_num]
            
            # Сохраняем выбранный мэтч
            await state.update_data(selected_match=selected_match)
            partner_name = selected_match['user']['name']
            partner_id = selected_match['user']['id']
            await message.answer(
                f"Выбран мэтч с <b>{partner_name}</b>!\n\n"
                "Хотите начать Speed Dating?\n"
                "Вы будете отвечать на 5 случайных вопросов по очереди.",
                parse_mode="HTML",
                reply_markup=speed_dating_start_kb()
            )
            # ⭐ ВАЖНО: Меняем состояние!
            await state.set_state(SpeedDatingState.waiting_confirmation)  # <-- НОВОЕ СОСТОЯНИЕ
        else:
            await message.answer(
                f"Пожалуйста, введите число от 1 до {len(matches)}"
            )
    except ValueError:
        await message.answer("Пожалуйста, введите номер мэтча (число)")



@router.message(SpeedDatingState.waiting_confirmation, F.text == "🚀 Начать спиддейтинг")
async def start_speed_dating_handler(message: Message, state: FSMContext, bot: Bot):
    """Начать спиддейтинг"""
    data = await state.get_data()
    selected_match = data.get('selected_match')
    
    if not selected_match:
        await message.answer("Мэтч не выбран", reply_markup=main_menu_kb())
        await state.clear()
        return
    
    # Получаем ID пользователя в БД
    user_db_id = await get_user_db_id(message.from_user.id)
    if not user_db_id:
        await message.answer("Ошибка: пользователь не найден")
        return
    
    # Начинаем спиддейтинг
    result = await SpeedDatingService.start_speed_dating(selected_match['match_id'])
    
    if not result.get('success'):
        await message.answer(
            f"Не удалось начать спиддейтинг: {result.get('message', 'Ошибка')}",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return
    
    session = result['session']
    users = result.get('users', {})
    
    # Определяем, кто второй пользователь (ПАРТНЕР)
    # Получаем информацию о текущем пользователе и партнере
    if user_db_id == users['user1']['id']:
        current_user_info = users['user1']  # Это ТЕКУЩИЙ пользователь
        other_user = users['user2']         # Это ПАРТНЕР
    else:
        current_user_info = users['user2']  # Это ТЕКУЩИЙ пользователь
        other_user = users['user1']         # Это ПАРТНЕР
    
    # Уведомляем ПАРТНЕРА о начале спиддейтинга
    try:
        await bot.send_message(
            chat_id=int(other_user['telegram_id']),
            text=f"🎉 <b>{current_user_info['name']}</b> хочет начать Speed Dating с тобой!\n\n"
                 "Вы будете отвечать на 5 случайных вопросов по очереди.",
            parse_mode="HTML",
            reply_markup=speed_dating_start_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка уведомления второго пользователя: {e}")
    
    # Сохраняем данные сессии
    await state.update_data(
        session_id=session.id,
        partner_id=other_user['id'],
        partner_telegram_id=other_user['telegram_id'],
        partner_name=other_user['name'],
        current_user_name=current_user_info['name'],
        current_user_id=user_db_id
    )
    
    # Проверяем, кто начинает первым
    current_question = await SpeedDatingService.get_current_question(session.id)
    
    if current_question['success']:
        logger.info(f"Начало Speed Dating: пользователь {user_db_id} ({current_user_info['name']})")
        logger.info(f"Партнер: {other_user['id']} ({other_user['name']})")
        logger.info(f"Текущий отвечающий ID: {current_question['current_responder_id']}")
        
        # Определяем имя отвечающего для отображения
        if current_question['current_responder_id'] == user_db_id:
            # Текущий пользователь отвечает первым
            responder_name = current_user_info['name']
            is_current_user_responding = True
        else:
            # Партнер отвечает первым
            responder_name = other_user['name']
            is_current_user_responding = False
        
        logger.info(f"Отвечает первым: {responder_name}")
        
        if is_current_user_responding:
            # Текущий пользователь отвечает первым
            await message.answer(
                f"🚀 <b>Начинаем Speed Dating!</b>\n\n"
                f"💬 <b>Вопрос 1 из 5:</b>\n"
                f"<i>{current_question['question']}</i>\n\n"
                f"<b>Вы отвечаете первым.</b>\n"
                f"Напишите свой ответ ниже ⬇️",
                parse_mode="HTML",
                reply_markup=speed_dating_question_kb()
            )
            await state.set_state(SpeedDatingState.waiting_answer)
        else:
            # Партнер отвечает первым
            await message.answer(
                f"🚀 <b>Начинаем Speed Dating!</b>\n\n"
                f"💬 <b>Вопрос 1 из 5:</b>\n"
                f"<i>{current_question['question']}</i>\n\n"
                f"<b>Сейчас отвечает {other_user['name']}.</b>\n"
                f"Пожалуйста, подождите...",
                parse_mode="HTML",
                reply_markup=speed_dating_session_kb()
            )
            await state.set_state(SpeedDatingState.partner_waiting)
    else:
        await message.answer(
            "Ошибка при получении вопроса",
            reply_markup=main_menu_kb()
        )
        await state.clear()


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
    """Отправить ответ на вопрос"""
    data = await state.get_data()
    session_id = data.get('session_id')
    user_answer = data.get('current_answer')
    
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
    
    # Получаем ID пользователя в БД
    user_db_id = await get_user_db_id(message.from_user.id)
    if not user_db_id:
        await message.answer("Ошибка: пользователь не найден")
        return
    
    # Сохраняем ответ
    result = await SpeedDatingService.submit_answer(session_id, user_db_id, user_answer)
    
    if not result.get('success'):
        await message.answer(
            f"Ошибка при отправке ответа: {result.get('message', 'Неизвестная ошибка')}",
            reply_markup=main_menu_kb()
        )
        await state.clear()
        return
    
    # Получаем партнера
    partner_telegram_id = data.get('partner_telegram_id')
    partner_name = data.get('partner_name')
    
    # Уведомляем партнера
    if partner_telegram_id:
        try:
            await bot.send_message(
                chat_id=int(partner_telegram_id),
                text=f"✅ {message.from_user.first_name} ответил(а) на вопрос!\n\n"
                     "Теперь ваша очередь отвечать.",
                reply_markup=speed_dating_question_kb()
            )
        except Exception as e:
            print(f"Ошибка уведомления партнера: {e}")
    
    # Проверяем, завершена ли сессия
    if result.get('is_completed'):
        await message.answer(
            "🎉 <b>Speed Dating завершен успешно!</b>\n\n"
            f"Теперь вы можете общаться с {partner_name} напрямую!\n"
            f"Telegram: @{partner_name}",
            parse_mode="HTML",
            reply_markup=main_menu_kb()
        )
        
        # Отправляем никнеймы обоим пользователям
        try:
            await bot.send_message(
                chat_id=int(partner_telegram_id),
                text=f"🎉 <b>Speed Dating завершен успешно!</b>\n\n"
                     f"Теперь вы можете общаться с {message.from_user.first_name} напрямую!\n"
                     f"Telegram: @{message.from_user.username}",
                parse_mode="HTML",
                reply_markup=main_menu_kb()
            )
        except Exception as e:
            print(f"Ошибка отправки финального сообщения: {e}")
        
        await state.clear()
        return
    
    # Получаем следующий вопрос
    next_question = await SpeedDatingService.get_current_question(session_id)
    
    if not next_question.get('success'):
        await message.answer("Ошибка при получении следующего вопроса")
        return
    
    # Проверяем, кто отвечает следующим
    if next_question['current_responder_id'] == user_db_id:
        # Пользователь снова отвечает
        await message.answer(
            f"✅ Ответ сохранен!\n\n"
            f"Вопрос {next_question['question_number']} из {next_question['total_questions']}:\n"
            f"<i>{next_question['question']}</i>\n\n"
            f"Вы отвечаете снова. Напишите свой ответ ниже ⬇️",
            parse_mode="HTML",
            reply_markup=speed_dating_question_kb()
        )
        await state.set_state(SpeedDatingState.waiting_answer)
    else:
        # Партнер отвечает
        await message.answer(
            f"✅ Ответ сохранен!\n\n"
            f"Вопрос {next_question['question_number']} из {next_question['total_questions']}:\n"
            f"<i>{next_question['question']}</i>\n\n"
            f"Сейчас отвечает {partner_name}. Пожалуйста, подождите...",
            parse_mode="HTML",
            reply_markup=speed_dating_session_kb()
        )
        await state.set_state(SpeedDatingState.partner_waiting)
    
    # Очищаем текущий ответ
    await state.update_data(current_answer=None)


@router.message(SpeedDatingState.waiting_answer, F.text)
async def save_answer_text(message: Message, state: FSMContext):
    """Сохранить текст ответа перед отправкой"""
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
        # Отменяем сессию
        await SpeedDatingService.cancel_session(session_id)
        
        # Уведомляем партнера
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
    """Партнер отвечает, нужно ждать"""
    # Игнорируем другие сообщения кроме команды отмены
    if message.text != "⏹ Приостановить знакомство":
        await message.answer(
            "Пожалуйста, подождите, пока партнер ответит на вопрос.",
            reply_markup=speed_dating_session_kb()
        )