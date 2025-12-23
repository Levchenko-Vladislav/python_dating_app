import asyncio 
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime

from src.dating_bot.bot.states import PsychologicalTest, Profile
from src.dating_bot.bot.keyboards import (
    test_answer_kb, 
    start_test_kb,
    test_results_kb,
    confirm_retake_kb,
    edit_menu_kb,
    test_results_kb
)
from src.dating_bot.data.test_questions import PSYCHOLOGICAL_TEST_QUESTIONS
from src.dating_bot.services.test_calculator import (
    get_total_questions,
    calculate_category_scores,
    format_results_for_display,
    calculate_test_completion_percentage,
    get_min_required_answers
)

router = Router()
TOTAL_QUESTIONS = get_total_questions()


@router.message(F.text == "📝 Да!")
@router.message(Command("start_test"))
async def start_test_command(message: Message, state: FSMContext):
    profile_data = await state.get_data()
    if not profile_data.get("name"):
        await message.answer(
            "❌ Сначала заполни профиль через /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    await message.answer(
        "✨ *Психологический тест для MINDY*\n\n"
        "30 утверждений, ответы от 1 до 5:\n\n"
        "1️⃣ — Совсем не согласен\n"
        "2️⃣ — Скорее не согласен\n"
        "3️⃣ — Иногда/Нейтрально\n"
        "4️⃣ — Скорее согласен\n"
        "5️⃣ — Полностью согласен\n\n"
        "Готов(а) начать?",
        reply_markup=start_test_kb(),
        parse_mode="Markdown"
    )
    await state.set_state(PsychologicalTest.welcome)


@router.message(PsychologicalTest.welcome, F.text == "📝 Начать тест")
async def begin_test(message: Message, state: FSMContext):
    await state.update_data(
        test_started_at=datetime.now().isoformat(),
        test_answers={},
        current_question=1,
        test_completed=False
    )
    await show_question(message, state)


async def show_question(message: Message, state: FSMContext):
    data = await state.get_data()
    current_q = data.get("current_question", 1)
    if current_q > TOTAL_QUESTIONS:
        await finish_test(message, state)
        return
    question = PSYCHOLOGICAL_TEST_QUESTIONS[current_q - 1]
    await message.answer(
        f"*Вопрос {current_q} из {TOTAL_QUESTIONS}*\n\n"
        f"*{question['text']}*\n\n"
        "Выбери вариант:",
        reply_markup=test_answer_kb(),
        parse_mode="Markdown"
    )
    await state.set_state(PsychologicalTest.in_progress)


@router.message(PsychologicalTest.in_progress, F.text.startswith(("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣")))
async def process_test_answer(message: Message, state: FSMContext):
    answer_map = {
        "1️⃣ - Совсем не согласен": 1,
        "2️⃣ - Скорее не согласен": 2,
        "3️⃣ - Иногда/Нейтрально": 3,
        "4️⃣ - Скорее согласен": 4,
        "5️⃣ - Полностью согласен": 5
    }
    answer_value = answer_map.get(message.text)
    if not answer_value:
        return
    data = await state.get_data()
    current_q = data.get("current_question", 1)
    answers = data.get("test_answers", {})
    answers[current_q] = answer_value
    await state.update_data(test_answers=answers, current_question=current_q + 1)
    
    await show_question(message, state)

@router.message(PsychologicalTest.in_progress, F.text == "⏭️ Пропустить вопрос")
async def skip_question(message: Message, state: FSMContext):
    data = await state.get_data()
    current_q = data.get("current_question", 1)
    await message.answer(f"❔ Вопрос {current_q} пропущен")
    await state.update_data(current_question=current_q + 1)
    await asyncio.sleep(0.5)
    await show_question(message, state)


async def finish_test(message: Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("test_answers", {})
    answered_count = len(answers)
    skipped_count = TOTAL_QUESTIONS - answered_count
    min_required = get_min_required_answers()

    if answered_count < min_required:
        completion = calculate_test_completion_percentage(answered_count)
        await message.answer(
            f"Ты ответил(а) на {answered_count} из {TOTAL_QUESTIONS} вопросов ({completion}%)\n"
            f"Нужно минимум {min_required} для точных результатов.\n"
            "Хочешь продолжить с того же места?",
            reply_markup=start_test_kb()
        )
        await state.set_state(PsychologicalTest.welcome)
        return

    category_scores = calculate_category_scores(answers)

    from src.dating_bot.services.test_service import TestService
    from src.dating_bot.services.user_service import UserService

    telegram_id = str(message.from_user.id)
    user_profile = await UserService.get_user_profile(telegram_id)

    if user_profile and user_profile.get('user'):
        user_id = user_profile['user'].id

        test_result = await TestService.save_test_results(
            user_id=user_id,
            answers=answers,
            is_completed=True
        )

    await state.update_data(
        test_completed=True,
        test_completed_at=datetime.now().isoformat(),
        category_scores=category_scores
    )

    results_text = format_results_for_display(category_scores)
    if skipped_count > 0:
        results_text += f"\nℹ️ *Пропущено вопросов:* {skipped_count}"

    results_text += "\n✅ *Тест пройден! Теперь я смогу подбирать тебе идеальную пару! 💫*\n\n"
    results_text += "🎯 *Что дальше?*"

    await message.answer(
        results_text,
        reply_markup=test_results_kb(),
        parse_mode="Markdown"
    )
    await state.set_state(PsychologicalTest.results)

@router.message(PsychologicalTest.results, F.text == "🔄 Перепройти тест")
async def retake_test_handler(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ *Внимание!*\n\n"
        "Если перепройти тест, предыдущие ответы будут удалены.\n"
        "Точно хочешь начать заново?",
        reply_markup=confirm_retake_kb(),
        parse_mode="Markdown"
    )
    await state.set_state(PsychologicalTest.confirm_retake)


@router.message(PsychologicalTest.confirm_retake, F.text == "✅ Да, начать заново")
async def confirm_retake(message: Message, state: FSMContext):
    await state.update_data(
        test_answers={},
        current_question=1,
        test_completed=False,
        category_scores={},
        test_started_at=None,
        test_completed_at=None
    )
    await message.answer(
        "Начинаем тест заново! ✨",
        reply_markup=ReplyKeyboardRemove()
    )
    await begin_test(message, state)


@router.message(PsychologicalTest.confirm_retake, F.text == "❌ Нет, отменить")
async def cancel_retake(message: Message, state: FSMContext):
    await message.answer(
        "Хорошо, оставляем предыдущие результаты.",
        reply_markup=test_results_kb()
    )
    await state.set_state(PsychologicalTest.results)

@router.message(PsychologicalTest.results, F.text == "✏️ Изменить профиль")
async def edit_profile_from_results(message: Message, state: FSMContext):
    await state.update_data(is_edit=True)
    from src.dating_bot.bot.keyboards import edit_menu_kb
    await message.answer(
        "Что хочешь изменить в профиле?",
        reply_markup=edit_menu_kb()
    )
    await state.set_state(Profile.edit_field)

@router.message(PsychologicalTest.results, F.text == "👀 Смотреть анкеты")
async def browse_profiles_after_test(message: Message, state: FSMContext):
    from src.dating_bot.handlers.browse import start_browsing
    await state.update_data(test_completed=True)
    await start_browsing(message, state)

@router.message(PsychologicalTest.results, F.text == "📋 Главное меню")
async def back_to_menu_after_test(message: Message, state: FSMContext):
    from src.dating_bot.bot.keyboards import main_menu_kb
    await message.answer(
        "✅ Возвращаю в главное меню:",
        reply_markup=main_menu_kb()
    )

