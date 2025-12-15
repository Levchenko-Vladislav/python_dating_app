"""
Психологический тест из 30 вопросов с категориями для расчета совместимости
Шкала ответов: 1-5 (1 - совсем не согласен, 5 - полностью согласен)
"""

PSYCHOLOGICAL_TEST_QUESTIONS = [
    {
        "id": 1,
        "text": "Мне легко говорить о своих чувствах",
        "category": "communication_emotions",
        "reverse_scored": False  
    },
    {
        "id": 2,
        "text": "Я быстро замечаю, когда собеседнику неинтересно",
        "category": "communication_emotions",
        "reverse_scored": False
    },
    {
        "id": 3,
        "text": "В конфликтах я стараюсь найти компромисс",
        "category": "communication_emotions",
        "reverse_scored": False
    },
    {
        "id": 4,
        "text": "Мне важно ежедневно общаться с близким человеком",
        "category": "communication_emotions",
        "reverse_scored": False
    },
    {
        "id": 5,
        "text": "Я ценю честность больше, чем комфорт",
        "category": "communication_emotions",
        "reverse_scored": False
    },
    {
        "id": 6,
        "text": "Мне нравится обсуждать глубокие темы",
        "category": "communication_emotions",
        "reverse_scored": False
    },
    
    {
        "id": 7,
        "text": "Я планирую свои дела на неделю вперед",
        "category": "lifestyle_values",
        "reverse_scored": False
    },
    {
        "id": 8,
        "text": "Для меня важна карьера и самореализация",
        "category": "lifestyle_values",
        "reverse_scored": False
    },
    {
        "id": 9,
        "text": "Я люблю спонтанные поступки и сюрпризы",
        "category": "lifestyle_values",
        "reverse_scored": False
    },
    {
        "id": 10,
        "text": "Деньги для меня - средство, а не цель",
        "category": "lifestyle_values",
        "reverse_scored": False
    },
    {
        "id": 11,
        "text": "Я соблюдаю баланс работы и отдыха",
        "category": "lifestyle_values",
        "reverse_scored": False
    },
    {
        "id": 12,
        "text": "Мне нравится пробовать новое в жизни",
        "category": "lifestyle_values",
        "reverse_scored": False
    },
    
    {
        "id": 13,
        "text": "Мне важно сохранять личное пространство в отношениях",
        "category": "relationship_intimacy",
        "reverse_scored": False
    },
    {
        "id": 14,
        "text": "Совместные увлечения важнее похожих взглядов",
        "category": "relationship_intimacy",
        "reverse_scored": False
    },
    {
        "id": 15,
        "text": "Я верю в любовь с первого взгляда",
        "category": "relationship_intimacy",
        "reverse_scored": False
    },
    {
        "id": 16,
        "text": "Доверие нужно заслужить со временем",
        "category": "relationship_intimacy",
        "reverse_scored": False
    },
    {
        "id": 17,
        "text": "Романтические жесты важны для отношений",
        "category": "relationship_intimacy",
        "reverse_scored": False
    },
    {
        "id": 18,
        "text": "Я легко прощаю обиды",
        "category": "relationship_intimacy",
        "reverse_scored": False
    },
    
    {
        "id": 19,
        "text": "Я люблю шумные компании и вечеринки",
        "category": "social_activity",
        "reverse_scored": False
    },
    {
        "id": 20,
        "text": "Мне комфортнее в небольшом кругу друзей",
        "category": "social_activity",
        "reverse_scored": True
    },
    {
        "id": 21,
        "text": "Я часто знакомлюсь с новыми людьми",
        "category": "social_activity",
        "reverse_scored": False
    },
    {
        "id": 22,
        "text": "Социальные сети - важная часть моей жизни",
        "category": "social_activity",
        "reverse_scored": False
    },
    {
        "id": 23,
        "text": "Я участвую в волонтерстве или социальных проектах",
        "category": "social_activity",
        "reverse_scored": False
    },
    {
        "id": 24,
        "text": "Мне важно мнение окружающих о моих решениях",
        "category": "social_activity",
        "reverse_scored": False
    },
    
    {
        "id": 25,
        "text": "Я принимаю решения, опираясь на логику, а не эмоции",
        "category": "personal_qualities",
        "reverse_scored": False
    },
    {
        "id": 26,
        "text": "Мне нравится помогать другим, даже в ущерб себе",
        "category": "personal_qualities",
        "reverse_scored": False
    },
    {
        "id": 27,
        "text": "Я часто мечтаю и фантазирую",
        "category": "personal_qualities",
        "reverse_scored": False
    },
    {
        "id": 28,
        "text": "Критика помогает мне стать лучше",
        "category": "personal_qualities",
        "reverse_scored": False
    },
    {
        "id": 29,
        "text": "Я следую своим принципам, даже когда это сложно",
        "category": "personal_qualities",
        "reverse_scored": False
    },
    {
        "id": 30,
        "text": "Мне нужно время, чтобы привыкнуть к переменам",
        "category": "personal_qualities",
        "reverse_scored": False
    }
]

QUESTION_CATEGORIES = {
    "communication_emotions": "Общение и эмоции",
    "lifestyle_values": "Образ жизни и ценности",
    "relationship_intimacy": "Отношения и близость",
    "social_activity": "Социальная активность",
    "personal_qualities": "Личностные качества"
}