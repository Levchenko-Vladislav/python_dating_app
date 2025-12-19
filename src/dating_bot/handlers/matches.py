from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import html  # Для экранирования HTML

from src.dating_bot.services.like_service import LikeService
from src.dating_bot.bot.keyboards import main_menu_kb

router = Router()


@router.message(F.text == "💞 Мои мэтчи")
async def show_matches(message: Message, state: FSMContext):
    """Показать мэтчи пользователя"""
    matches = await LikeService.get_user_matches(message.from_user.id)

    if not matches:
        await message.answer(
            "😔 У тебя пока нет взаимных симпатий.\n"
            "Продолжай смотреть анкеты — твой идеальный партнер где-то рядом!",
            reply_markup=main_menu_kb()
        )
        return

    # Используем HTML разметку - она проще
    header = f"💞 <b>Твои взаимные симпатии ({len(matches)})</b>\n\n"
    header += "Вот люди, которые тоже заинтересовались тобой:"

    await message.answer(header, parse_mode="HTML")

    for match in matches[:10]:
        user = match['user']

        # Экранируем HTML специальные символы
        safe_name = html.escape(user['name'])
        safe_city = html.escape(user['city']) if user['city'] else "Не указан"
        safe_username = html.escape(user['username']) if user['username'] else "Без username"
        match_date = match['matched_at'].strftime('%d.%m.%Y')

        match_text = (
            f"👤 <b>{safe_name}</b>, {user['age']} лет\n"
            f"📍 {safe_city}\n"
            f"💬 {safe_username}\n"
            f"💘 Совпали: {match_date}"
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
        "Что хочешь сделать дальше?",
        reply_markup=main_menu_kb()
    )