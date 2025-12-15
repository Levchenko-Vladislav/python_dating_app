from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from dating_bot.bot.states import Profile, PsychologicalTest
from dating_bot.bot.keyboards import gender_kb, goal_kb, target_gender_kb,confirm_kb,test_ready_kb, edit_menu_kb, main_menu_kb

router = Router()

async def send_profile_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer_photo(
        photo=data["photo_id"],
        caption=(
            "Проверь анкету 🙂\n\n"
            f"👤 Имя: {data.get('name','')}\n"
            f"🎂 Возраст: {data.get('age','')}\n"
            f"⚧ Пол: {data.get('gender','')}\n"
            f"📍 Город: {data.get('city','')}\n"
            f"🎯 Цель: {data.get('goal','')}\n"
            f"🔍 Кого ищешь: {data.get('target_gender','')}\n"
            f"💬 Ник: {data.get('username','')}\n\n"
            "Всё верно? 🙂"
        ),
        reply_markup=confirm_kb()
    )

@router.message(Profile.name, F.text)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)
    data = await state.get_data()
    if data.get("is_edit"):
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
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    await message.answer("Укажи свой пол:🚺️🚹", reply_markup=gender_kb())
    await state.set_state(Profile.gender)

@router.message(
    Profile.gender,
    F.text.in_(["Женщина 👩", "Мужчина 🧑"])
)
async def get_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    data = await state.get_data()
    if data.get("is_edit"):
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    await message.answer(
        "Из какого ты города?🏙️",
        reply_markup= ReplyKeyboardRemove()
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
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    await message.answer("Что ты ищешь?", reply_markup=goal_kb())
    await state.set_state(Profile.goal)

@router.message(Profile.goal, F.text.in_(["💘 Отношения", "🫂 Дружба"]))
async def get_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    data = await state.get_data()
    if data.get("is_edit"):
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    await message.answer("Кого ты ищешь?", reply_markup=target_gender_kb())
    await state.set_state(Profile.target_gender)

@router.message(
    Profile.target_gender,
    F.text.in_(["Мужчину 👱‍♂️", "Женщину 👩", "Не важно 👩👱‍♂️"])
)
async def get_target_gender(message: Message, state: FSMContext):
    await state.update_data(target_gender=message.text)
    data = await state.get_data()
    if data.get("is_edit"):
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    await message.answer("Ещё чуть-чуть! Напиши свой ник в Telegram\n (например: @username)")
    await state.set_state(Profile.username)

@router.message(Profile.username, F.text)
async def get_username(message: Message, state: FSMContext):
    username = message.text.strip()
    if not username.startswith("@"):
        await message.answer(
            "Ник должен начинаться с @ 🙂\n"
            "Например: @mindy_user"
        )
        return

    if len(username) < 6:
        await message.answer(
            "Ник слишком короткий 🙂\n"
        )
        return
    await state.update_data(username=username)
    data = await state.get_data()
    if data.get("is_edit"):
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    await message.answer("Отправь своё фото 📸")
    await state.set_state(Profile.photo)


@router.message(Profile.photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    data = await state.get_data()
    if data.get("is_edit"):
        await send_profile_preview(message, state)
        await state.set_state(Profile.confirm)
        return
    data = await state.get_data()
    await message.answer_photo(
        photo=photo_id,

        caption=(
            "Готово! Анкета заполнена ✅\n\n"
            f"👤Имя: {data['name']}\n"
            f"🎂Возраст: {data['age']}\n"
            f"⚧ Пол: {data['gender']}\n"
            f"📍Город: {data['city']}\n"
            f"🎯Цель: {data['goal']}\n"
            f"🔍Кого ищешь: {data['target_gender']}\n"
            f"💬Ник: {data['username']}\n\n"
            "Всё верно? 🙂"),
        reply_markup=confirm_kb()
    )
    await state.set_state(Profile.confirm)


@router.message(Profile.photo)
async def photo_expected(message: Message):
    await message.answer(
        "Нужно отправить фото как картинку 🙂(не файл)"
    )

@router.message(Profile.confirm, F.text == "✅ Всё верно")
async def confirm_profile(message: Message, state: FSMContext):
    data = await state.get_data()

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
        from src.dating_bot.bot.keyboards import main_menu_kb
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


@router.message(Profile.edit_field, F.text.in_([
    "👤 Имя", "🎂 Возраст", "📍 Город", "⚧ Пол",
    "🎯 Цель", "🔍 Кого ищешь", "💬 Ник", "📸 Фото"
]))
async def edit_choose_field(message: Message, state: FSMContext):
    await state.update_data(is_edit=True)
    choice = message.text

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
        await message.answer("Напиши ник в Telegram (например: @username)", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Profile.username)

    elif choice == "📸 Фото":
        await message.answer("Отправь новое фото 📸 (картинкой)", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Profile.photo)