from src.dating_bot.services.test_calculator import (
    calculate_category_scores,
    format_results_for_display,
    calculate_test_completion_percentage,
    get_min_required_answers,
    is_test_complete
)

def test_calculate_category_scores_reverse_scored():
    answers = {
        19: 5,
        20: 5,
    }
    scores = calculate_category_scores(answers)
    assert "social_activity" in scores
    assert scores["social_activity"] == 3.0

def test_format_results_for_display_nonempty():
    text = format_results_for_display({"social_activity": 4.2})
    assert "Твои результаты теста" in text
    assert "Социальная активность" in text

def test_completion_percentage():
    assert calculate_test_completion_percentage(0) == 0.0
    assert calculate_test_completion_percentage(15) > 0

def test_min_required_and_is_complete():
    m = get_min_required_answers()
    assert is_test_complete(m) is True
    assert is_test_complete(m - 1) is False
