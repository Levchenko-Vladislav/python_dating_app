from src.dating_bot.services.compatibility import CompatibilityCalculator

def test_calculate_compatibility_identical_answers():
    user1 = {1: 3, 2: 5, 3: 1}
    user2 = {1: 3, 2: 5, 3: 1}
    assert CompatibilityCalculator.calculate_compatibility(user1, user2) == 100.0


def test_calculate_compatibility_with_mocked_scores(monkeypatch):
    def fake_scores(_answers):
        return {"A": 5.0, "B": 1.0}

    monkeypatch.setattr("src.dating_bot.services.compatibility.calculate_category_scores", fake_scores)

    comp = CompatibilityCalculator.calculate_compatibility({"1": 1}, {"2": 2})
    assert comp == 100.0

def test_calculate_compatibility_no_common_categories(monkeypatch):
    def scores1(_): return {"A": 5.0}
    def scores2(_): return {"B": 1.0}

    calls = {"n": 0}
    def fake(_answers):
        calls["n"] += 1
        return scores1(None) if calls["n"] == 1 else scores2(None)

    monkeypatch.setattr("src.dating_bot.services.compatibility.calculate_category_scores", fake)
    comp = CompatibilityCalculator.calculate_compatibility({1: 1}, {2: 2})
    assert comp == 50.0
