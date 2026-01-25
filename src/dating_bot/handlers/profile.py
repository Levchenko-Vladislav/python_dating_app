from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from src.dating_bot.bot.states import Profile, PsychologicalTest
from src.dating_bot.bot.keyboards import (gender_kb, goal_kb, target_gender_kb, confirm_kb, test_ready_kb,
                                      edit_menu_kb, username_kb, main_menu_kb, confirmation_kb)
from src.dating_bot.services.user_service import UserService, delete_user_completely
from src.dating_bot.utils.data_mappers import map_gender_to_db, map_target_gender_to_db
from src.dating_bot.utils.data_mappers import map_goal_to_db, map_goal_to_ui
from src.dating_bot.handlers.psychological_test import start_test_command

router = Router()

async def send_profile_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer_photo(
        photo=data["photo_id"],
        caption=(
            "Проверь анкету 🙂\n\n"
            f"👤 Имя: {data.get('name', '')}\n"
            f"🎂 Возраст: {data.get('age', '')}\n"
            f"⚧ Пол: {data.get('gender', '')}\n"
            f"📍 Город: {data.get('city', '')}\n"
            f"🎯 Цель: {data.get('goal', '')}\n"
            f"🔍 Кого ищешь: {data.get('target_gender', '')}\n"
            f"💬 Ник: {data.get('username', '')}\n\n"
            "Всё верно? 🙂"
        ),
        reply_markup=confirm_kb()
    )

async def update_user_in_db(message: Message, state: FSMContext, field: str, value):
    data = await state.get_data()
    telegram_id = data.get('telegram_id')

    if not telegram_id:
        telegram_id = str(message.from_user.id)
        await state.update_data(telegram_id=telegram_id)

    field_mapping = {
        'name': 'name',
        'age': 'age',
        'city': 'city',
        'gender': 'sex',
        'target_gender': 'search_sex',
        'photo_id': 'photo_id',
        'goal': 'goal',
        'username': 'username'
    }

    db_field = field_mapping.get(field)
    if db_field:
        if field == 'gender':
            value = map_gender_to_db(value)
        elif field == 'target_gender':
            value = map_target_gender_to_db(value)

        await UserService.update_user_profile(
            telegram_id=telegram_id,
            **{db_field: value}
        )

@router.message(Profile.name, F.text)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    data = await state.get_data()

    if data.get("is_edit"):
        await update_user_in_db(message, state, 'name', name)
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return

    await message.answer("Сколько тебе лет?")
    await state.set_state(Profile.age)

@router.message(Profile.age, F.text)
async def get_age(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer(
            "Возраст нужно ввести цифрами 🙃\n"
            "Например: 19"
        )
        return

    age = int(text)
    await state.update_data(age=age)
    data = await state.get_data()

    if data.get("is_edit"):
        await update_user_in_db(message, state, 'age', age)
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return

    await message.answer("Укажи свой пол:🚺️🚹", reply_markup=gender_kb())
    await state.set_state(Profile.gender)

@router.message(Profile.gender, F.text.in_(["Женщина 👩", "Мужчина 🧑"]))
async def get_gender(message: Message, state: FSMContext):
    gender = message.text
    await state.update_data(gender=gender)
    data = await state.get_data()

    if data.get("is_edit"):
        await update_user_in_db(message, state, 'gender', gender)
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return

    await message.answer(
        "Из какого ты города?🏙️",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Profile.city)

@router.message(Profile.city, F.text)
async def get_city(message: Message, state: FSMContext):
    city = message.text.strip()
    if len(city) < 2:
        await message.answer("Такого города не существует, напиши ещё раз 🙂")
        return

    await state.update_data(city=city)
    data = await state.get_data()

    if data.get("is_edit"):
        await update_user_in_db(message, state, 'city', city)
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return

    await message.answer("Что ты ищешь?", reply_markup=goal_kb())
    await state.set_state(Profile.goal)

@router.message(Profile.goal, F.text.in_(["💘 Отношения", "🫂 Дружба"]))
async def get_goal(message: Message, state: FSMContext):
    goal = message.text
    await state.update_data(goal=goal)
    data = await state.get_data()

    if data.get("is_edit"):
        telegram_id = data.get('telegram_id')
        if data.get("telegram_id"):
            await UserService.update_user_profile(
                telegram_id=data["telegram_id"],
                goal=map_goal_to_db(goal)
            )
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return

    await message.answer("Кого ты ищешь?", reply_markup=target_gender_kb())
    await state.set_state(Profile.target_gender)

@router.message(Profile.target_gender, F.text.in_(["Мужчину 👱‍♂️", "Женщину 👩", "Не важно 👩👱‍♂️"]))
async def get_target_gender(message: Message, state: FSMContext):
    target_gender = message.text
    await state.update_data(target_gender=target_gender)
    data = await state.get_data()

    if data.get("is_edit"):
        await update_user_in_db(message, state, 'target_gender', target_gender)
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return

    await message.answer("Нажми кнопку - и я автоматически возьму твой username из профиля!",
                         reply_markup=username_kb())
    await state.set_state(Profile.username)

@router.message(Profile.username, F.text)
async def get_username(message: Message, state: FSMContext):
    if message.text == "📨 Отправить мой username":
        telegram_username = message.from_user.username
        if not telegram_username:
            await message.answer(
                "У тебя не задан username в Telegram 🥲\n"
                "Зайди в настройки Telegram → Username и установи его, потом нажми кнопку ещё раз.",
                reply_markup=username_kb(),
            )
            return
        username = f"@{telegram_username}"
    else:
        username = message.text.strip()
        
        if not username.startswith("@"):
            await message.answer(
                "Ник должен начинаться с @ 🙂\n"
                "Например: @mindy_user\n"
                "Или нажми кнопку «📨 Отправить мой username»",
                reply_markup=username_kb()
            )
            return
        
        if len(username) < 3:
            await message.answer("Ник слишком короткий 🙂", reply_markup=username_kb())
            return
    
    await state.update_data(username=username)
    data = await state.get_data()

    if data.get("is_edit"):
        telegram_id = data.get('telegram_id') or str(message.from_user.id)
        await UserService.update_user_profile(
            telegram_id=telegram_id,
            username=username
        )
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    
    await message.answer("Ещё чуть-чуть! Отправь своё фото 📸")
    await state.set_state(Profile.photo)

@router.message(Profile.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    
    data = await state.get_data()
    data['photo_id'] = photo_id
    await state.set_data(data)
    
    if data.get("is_edit"):
        await update_user_in_db(message, state, 'photo_id', photo_id)
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return

    await message.answer_photo(
        photo=photo_id,
        caption=(
            "Готово! Анкета заполнена ✅\n\n"
            f"👤 Имя: {data.get('name', '—')}\n"
            f"🎂 Возраст: {data.get('age', '—')}\n"
            f"⚧ Пол: {data.get('gender', '—')}\n"
            f"📍 Город: {data.get('city', '—')}\n"
            f"🎯 Цель: {data.get('goal', '—')}\n"
            f"🔍 Кого ищешь: {data.get('target_gender', '—')}\n"
            f"💬 Ник: {data.get('username', '—')}\n\n"
            "Всё верно? 🙂"
        ),
        reply_markup=confirm_kb()
    )
    await state.set_state(Profile.confirm)

@router.message(Profile.photo)
async def photo_expected(message: Message):
    await message.answer("Нужно отправить фото как картинку 🙂(не файл)")

@router.message(Profile.confirm, F.text == "✅ Всё верно")
async def confirm_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    is_edit = data.get('is_edit', False)

    required_fields = ['name', 'age', 'city', 'gender', 'goal', 'photo_id']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        # Если нет каких-то полей, пытаемся получить их из БД
        user_profile = await UserService.get_user_profile(str(message.from_user.id))
        
        if user_profile and user_profile.get('user'):
            user = user_profile['user']
            # Дополняем данные из БД
            if 'gender' not in data:
                data['gender'] = "Женщина 👩" if user.sex == "female" else "Мужчина 🧑" if user.sex == "male" else ""
            if 'goal' not in data:
                data['goal'] = "💘 Отношения" if user.goal == "relationship" else "🫂 Дружба" if user.goal == "friendship" else ""
            if 'photo_id' not in data:
                data['photo_id'] = user.photo_id
            if 'target_gender' not in data:
                # Преобразуем search_sex в UI формат
                if user.search_sex == "male":
                    data['target_gender'] = "Мужчину 👱♂️"
                elif user.search_sex == "female":
                    data['target_gender'] = "Женщину 👩"
                elif user.search_sex == "any":
                    data['target_gender'] = "Не важно 👩👱♂️"
                else:
                    data['target_gender'] = "Не важно 👩👱♂️"
        else:
            await message.answer("❌ Не все данные заполнены. Попробуйте заполнить анкету заново.")
            return

    telegram_id = str(message.from_user.id)
    telegram_username = data.get('username')

    result = await UserService.register_user(
        telegram_id=telegram_id,
        username=telegram_username,
        name=data['name'],
        age=data['age'],
        city=data['city'],
        sex=map_gender_to_db(data['gender']),
        photo_id=data['photo_id'],
        goal=map_goal_to_db(data.get('goal', '💘 Отношения'))
    )

    if result['success']:
        await UserService.update_user_profile(
            telegram_id=telegram_id,
            search_sex=map_target_gender_to_db(data.get('target_gender', 'Не важно 👩👱♂️'))
        )
        await state.update_data(is_registered=True, telegram_id=telegram_id)

    card_text = (
        "Вот так твою анкету будут видеть другие пользователи 👀\n\n"
        f"👤 Имя: {data['name']}\n"
        f"🎂 Возраст: {data['age']}\n"
        f"📍 Город: {data['city']}\n\n"
    )

    await message.answer_photo(
        photo=data["photo_id"],
        caption=card_text,
        reply_markup=ReplyKeyboardRemove()
    )
    if is_edit:
            # При редактировании - сразу в главное меню
            await message.answer(
                "✅ Анкета успешно обновлена!\n\n"
                "Что хочешь сделать дальше?",
                reply_markup=main_menu_kb()
            )
    else:
        await message.answer(
            "Далее — короткий психологический тест ✨\n"
            "Он поможет мне посчитать процент твоей совместимости с другими людьми и\n"
            "максимально точно найти того, кто видит и чувствует этот мир так же, как ты!\n"
            "Готов(а) начать 🙂?",
            reply_markup=test_ready_kb()
        )
    await state.update_data(is_edit=False, test_completed=False)

@router.message(Profile.confirm, F.text == "📝 Да!")
async def start_test_from_confirm(message: Message, state: FSMContext):
    from src.dating_bot.handlers.psychological_test import start_test_command
    await start_test_command(message, state)

@router.message(PsychologicalTest.welcome, F.text == "⏳ Не сейчас")
@router.message(F.text.in_(["⏳ Позже"]))
async def postpone_test(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get("name"):
        await message.answer(
            "✅ Твой профиль сохранен!\n\n"
            "Что хочешь сделать?",
            reply_markup=main_menu_kb()
        )
    else:
        await message.answer(
            "Хорошо 🙂 Когда будешь готов(а) — напиши /start",
            reply_markup=ReplyKeyboardRemove()
        )

@router.message(F.text == "✏️ Редактировать профиль")
@router.message(Profile.confirm, F.text == "✏️ Изменить")
async def edit_start(message: Message, state: FSMContext):
    await state.update_data(is_edit=True)
    await message.answer(
        "Что хочешь изменить?",
        reply_markup=edit_menu_kb()
    )
    await state.set_state(Profile.edit_field)

@router.message(Profile.edit_field, F.text == "↩️ Назад")
async def edit_back(message: Message, state: FSMContext):
    await send_profile_preview(message, state)
    await state.set_state(Profile.confirm)

@router.message(Profile.edit_field, F.text == "🔄 Обновить username")
async def refresh_username(message: Message, state: FSMContext):
    telegram_id = message.from_user.username

    if not telegram_id:
        await message.answer(
            "У тебя не задан username в Telegram 🥲\n"
            "Зайди в настройки Telegram → Username и попробуй ещё раз."
        )
        return

    await state.update_data(username=f"@{telegram_id}")

    await message.answer("Username обновлён ✅")
    await send_profile_preview(message, state)
    await state.set_state(Profile.confirm)

@router.message(Profile.edit_field, F.text.in_([
    "👤 Имя", "🎂 Возраст", "📍 Город", "⚧ Пол",
    "🎯 Цель", "🔍 Кого ищешь", "💬 Ник", "📸 Фото"
]))
async def edit_choose_field(message: Message, state: FSMContext):
    choice = message.text
    from src.dating_bot.services.user_service import UserService
    user_profile = await UserService.get_user_profile(str(message.from_user.id))
    
    if not user_profile or not user_profile.get('user'):
        await message.answer("❌ Не удалось загрузить ваш профиль")
        return
    
    user = user_profile['user']
    
    # Преобразуем данные из БД в UI формат
    gender_ui = "Женщина 👩" if user.sex == "female" else "Мужчина 🧑" if user.sex == "male" else ""
    goal_ui = "💘 Отношения" if user.goal == "relationship" else "🫂 Дружба" if user.goal == "friendship" else ""
    
    target_gender_ui = ""
    if user.search_sex == "male":
        target_gender_ui = "Мужчину 👱♂️"
    elif user.search_sex == "female":
        target_gender_ui = "Женщину 👩"
    elif user.search_sex == "any":
        target_gender_ui = "Не важно 👩👱♂️"
    
    # Сохраняем ВСЕ данные в состоянии
    await state.set_data({
        'name': user.name,
        'age': user.age,
        'city': user.city,
        'gender': gender_ui,
        'goal': goal_ui,
        'target_gender': target_gender_ui,
        'username': user.username or f"@{message.from_user.username}",
        'photo_id': user.photo_id,
        'telegram_id': str(message.from_user.id),
        'is_edit': True
    })
    
    if choice == "👤 Имя":
        await message.answer("Напиши имя:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Profile.name)

    elif choice == "🎂 Возраст":
        await message.answer("Сколько тебе лет?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Profile.age)

    elif choice == "📍 Город":
        await message.answer("Из какого ты города? 🏙️", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Profile.city)

    elif choice == "⚧ Пол":
        await message.answer("Укажи свой пол:", reply_markup=gender_kb())
        await state.set_state(Profile.gender)

    elif choice == "🎯 Цель":
        await message.answer("Что ты ищешь?", reply_markup=goal_kb())
        await state.set_state(Profile.goal)

    elif choice == "🔍 Кого ищешь":
        await message.answer("Кого ты ищешь?", reply_markup=target_gender_kb())
        await state.set_state(Profile.target_gender)

    elif choice == "💬 Ник":
        await message.answer("Нажми кнопку чтобы обновить username:", reply_markup=username_kb())
        await state.set_state(Profile.username)

    elif choice == "📸 Фото":
        from src.dating_bot.database.session import AsyncSessionLocal
        from src.dating_bot.database.repositories.user_repository import UserRepository
        
        async with AsyncSessionLocal() as session:
            repo = UserRepository(session)
            user = await repo.get_user_by_telegram_id(str(message.from_user.id))
            
            if user:
                gender_ui = ""
                if user.sex == "female":
                    gender_ui = "Женщина 👩"
                elif user.sex == "male":
                    gender_ui = "Мужчина 🧑"
                
                goal_ui = user.goal
                if user.goal == "relationship":
                    goal_ui = "💘 Отношения"
                elif user.goal == "friendship":
                    goal_ui = "🫂 Дружба"
                
                target_gender_ui = user.search_sex
                if user.search_sex == "male":
                    target_gender_ui = "Мужчину 👱♂️"
                elif user.search_sex == "female":
                    target_gender_ui = "Женщину 👩"
                elif user.search_sex == "any":
                    target_gender_ui = "Не важно 👩👱♂️"
                
                await state.set_data({
                    'name': user.name,
                    'age': user.age,
                    'gender': gender_ui,
                    'city': user.city,
                    'goal': goal_ui,
                    'target_gender': target_gender_ui,
                    'username': user.username if user.username else f"@{message.from_user.username}",
                    'photo_id': user.photo_id,
                    'telegram_id': str(message.from_user.id),
                    'is_edit': True
                })
            else:
                await state.update_data(is_edit=True)
        
        await message.answer("Отправь новое фото 📸 (картинкой)", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Profile.photo)

@router.message(F.text == "🗑️ Удалить анкету")
async def delete_profile_command(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ <b>ВНИМАНИЕ!</b>\n\n"
        "Вы собираетесь УДАЛИТЬ свою анкету и ВСЕ данные:\n"
        "• Ваш профиль\n"
        "• Результаты теста\n"
        "• Все лайки и мэтчи\n"
        "• Историю Speed Dating\n\n"
        "Это действие НЕЛЬЗЯ отменить!\n\n"
        "Вы уверены?",
        parse_mode="HTML",
        reply_markup=confirmation_kb()
    )
    await state.set_state("waiting_delete_confirmation")

@router.message(F.text == "✅ Да, удалить всё", StateFilter("waiting_delete_confirmation"))
async def confirm_delete_profile(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)
    loading_msg = await message.answer("🗑️ Удаляем ваши данные...")
    result = await delete_user_completely(telegram_id)
    if result:
        await loading_msg.edit_text(
            "✅ Ваша анкета и все данные успешно удалены!\n\n"
            "Если захотите вернуться, просто нажмите /start\n"
            "Спасибо, что были с нами! 👋"
        )
    else:
        await loading_msg.edit_text(
            "❌ Не удалось удалить анкету. Возможно, она уже удалена.\n"
            "Обратитесь к администратору."
        )
    await state.clear()

@router.message(F.text == "❌ Нет, отменить", StateFilter("waiting_delete_confirmation"))
async def cancel_delete_profile(message: Message, state: FSMContext):
    await message.answer(
        "Удаление анкеты отменено.\n"
        "Ваши данные сохранены.",
        reply_markup=main_menu_kb()
    )
    await state.clear()
