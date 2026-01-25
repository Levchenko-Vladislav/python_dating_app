from typing import Dict, List
from src.dating_bot.data.test_questions import PSYCHOLOGICAL_TEST_QUESTIONS, QUESTION_CATEGORIES

def get_total_questions() -> int:
    return len(PSYCHOLOGICAL_TEST_QUESTIONS)

def get_question_by_id(question_id: int) -> Dict:
    for question in PSYCHOLOGICAL_TEST_QUESTIONS:
        if question["id"] == question_id:
            return question
    return None

def get_questions_by_category(category: str) -> List[Dict]:
    return [q for q in PSYCHOLOGICAL_TEST_QUESTIONS if q["category"] == category]

def calculate_category_scores(answers_dict: Dict[int, int]) -> Dict[str, float]:
    category_scores = {}
    category_counts = {}
    for question_id, answer in answers_dict.items():
        question = get_question_by_id(question_id)
        if not question:
            continue
        category = question["category"]
        score = answer
        if question.get("reverse_scored", False):
            score = 6 - score
        if category not in category_scores:
            category_scores[category] = 0
            category_counts[category] = 0
        category_scores[category] += score
        category_counts[category] += 1
    for category in category_scores:
        if category_counts[category] > 0:
            category_scores[category] = round(category_scores[category] / category_counts[category], 2)
    return category_scores

def format_results_for_display(category_scores: Dict[str, float]) -> str:
    if not category_scores:
        return "Результаты теста не найдены."
    result_text = "✨ *Твои результаты теста* ✨\n\n"
    for category, score in category_scores.items():
        category_name = QUESTION_CATEGORIES.get(category, category)
        filled = int(score)
        result_text += f"{category_name}: {score}/5 {'⭐' * filled}\n"
    return result_text

def calculate_test_completion_percentage(answers_count: int) -> float:
    total = get_total_questions()
    return round((answers_count / total) * 100, 1)

def get_min_required_answers() -> int:
    return 20

def is_test_complete(answers_count: int) -> bool:
    return answers_count >= get_min_required_answers()