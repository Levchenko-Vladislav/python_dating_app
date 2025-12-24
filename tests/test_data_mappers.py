import pytest

from src.dating_bot.utils.data_mappers import (
    map_gender_to_db, map_gender_to_ui,
    map_target_gender_to_db, map_target_gender_to_ui,
    prepare_user_data_for_db
)

@pytest.mark.parametrize("text,expected", [
    ("Женщина 👩", "female"),
    ("Мужчина 🧑", "male"),
    ("female", "female"),
    ("male", "male"),
    ("", "other"),
    (None, "other"),
])
def test_map_gender_to_db(text, expected):
    assert map_gender_to_db(text) == expected

@pytest.mark.parametrize("db,expected", [
    ("female", "Женщина 👩"),
    ("male", "Мужчина 🧑"),
    ("other", "Другое"),
    ("", "Не указано"),
    (None, "Не указано"),
])
def test_map_gender_to_ui(db, expected):
    assert map_gender_to_ui(db) == expected

@pytest.mark.parametrize("text,expected", [
    ("Мужчину 👱‍♂️", "male"),
    ("Женщину 👩", "female"),
    ("Не важно 👩👱‍♂️", "any"),
    ("any", "any"),
    (None, "any"),
])
def test_map_target_gender_to_db(text, expected):
    assert map_target_gender_to_db(text) == expected

@pytest.mark.parametrize("db,expected", [
    ("male", "Мужчину 👱‍♂️"),
    ("female", "Женщину 👩"),
    ("any", "Не важно 👩👱‍♂️"),
    (None, "Не важно 👩👱‍♂️"),
])
def test_map_target_gender_to_ui(db, expected):
    assert map_target_gender_to_ui(db) == expected

def test_prepare_user_data_for_db_strips_and_maps():
    data = {
        "name": "  Alice  ",
        "age": 20,
        "city": "  Amsterdam ",
        "gender": "Женщина 👩",
        "photo_id": "ph",
        "target_gender": "Мужчину 👱‍♂️",
        "goal": "💘 Отношения",
    }
    out = prepare_user_data_for_db(data)
    assert out["name"] == "Alice"
    assert out["city"] == "Amsterdam"
    assert out["sex"] == "female"
    assert out["search_sex"] == "male"
    assert out["goal"] == "relationship"
