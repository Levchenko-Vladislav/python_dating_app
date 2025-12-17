"""
Модуль для преобразования данных между FSM и БД
"""


def map_gender_to_db(gender_text: str) -> str:
    """Преобразует текст пола из FSM в значение для БД"""
    if not gender_text:
        return "other"

    mapping = {
        "Женщина 👩": "female",
        "Мужчина 🧑": "male",
        "Женщина": "female",
        "Мужчина": "male",
        "female": "female",
        "male": "male"
    }
    return mapping.get(gender_text.strip(), "other")

def map_goal_to_db(goal_text: str) -> str:
    """Преобразует цель из FSM в значение для БД"""
    mapping = {
        "💘 Отношения": "relationship",
        "🫂 Дружба": "friendship",
        "Отношения": "relationship",
        "Дружба": "friendship",
        "relationship": "relationship",
        "friendship": "friendship"
    }
    return mapping.get(goal_text.strip(), "relationship")

def map_goal_to_ui(goal_db: str) -> str:
    """Преобразует цель из БД в текст для UI"""
    mapping = {
        "relationship": "💘 Отношения",
        "friendship": "🫂 Дружба"
    }
    return mapping.get(goal_db, "💘 Отношения")
def map_gender_to_ui(gender_db: str) -> str:
    """Преобразует пол из БД в текст для UI"""
    if not gender_db:
        return "Не указано"

    mapping = {
        "female": "Женщина 👩",
        "male": "Мужчина 🧑",
        "other": "Другое"
    }
    return mapping.get(gender_db, "Не указано")


def map_target_gender_to_db(target_text: str) -> str:
    """Преобразует искомый пол из FSM в значение для БД"""
    if not target_text:
        return "any"

    mapping = {
        "Мужчину 👱‍♂️": "male",
        "Женщину 👩": "female",
        "Не важно 👩👱‍♂️": "any",
        "male": "male",
        "female": "female",
        "any": "any"
    }
    return mapping.get(target_text.strip(), "any")


def map_target_gender_to_ui(target_db: str) -> str:
    """Преобразует искомый пол из БД в текст для UI"""
    if not target_db:
        return "Не важно 👩👱‍♂️"

    mapping = {
        "male": "Мужчину 👱‍♂️",
        "female": "Женщину 👩",
        "any": "Не важно 👩👱‍♂️"
    }
    return mapping.get(target_db, "Не важно 👩👱‍♂️")


def map_goal_to_db(goal_text: str) -> str:
    """Преобразует цель из FSM в значение для БД"""
    if not goal_text:
        return "friendship"

    mapping = {
        "💘 Отношения": "relationship",
        "🫂 Дружба": "friendship",
        "Отношения": "relationship",
        "Дружба": "friendship"
    }
    return mapping.get(goal_text.strip(), "friendship")


def prepare_user_data_for_db(fsm_data: dict) -> dict:
    """Подготавливает данные из FSM для сохранения в БД"""
    return {
        "name": fsm_data.get("name", "").strip(),
        "age": fsm_data.get("age"),
        "city": fsm_data.get("city", "").strip(),
        "sex": map_gender_to_db(fsm_data.get("gender", "")),
        "photo_id": fsm_data.get("photo_id", ""),
        "search_sex": map_target_gender_to_db(fsm_data.get("target_gender", "")),
        "goal": map_goal_to_db(fsm_data.get("goal", ""))
    }