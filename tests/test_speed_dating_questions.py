from src.dating_bot.data.speed_dating_questions import get_random_questions, SPEED_DATING_QUESTIONS

def test_get_random_questions_count(monkeypatch):
    def fake_sample(seq, k):
        return list(seq)[:k]

    monkeypatch.setattr("src.dating_bot.data.speed_dating_questions.random.sample", fake_sample)

    qs = get_random_questions(5)
    assert len(qs) == 5
    assert qs == SPEED_DATING_QUESTIONS[:5]

def test_get_random_questions_caps_at_pool(monkeypatch):
    def fake_sample(seq, k):
        return list(seq)[:k]

    monkeypatch.setattr("src.dating_bot.data.speed_dating_questions.random.sample", fake_sample)

    qs = get_random_questions(10_000)
    assert len(qs) == len(SPEED_DATING_QUESTIONS)
