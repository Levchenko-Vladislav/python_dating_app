import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.dating_bot.services.recommendations import RecommendationService

class TestRecommendationService:
    @pytest.fixture
    def service(self):
        return RecommendationService()

    @pytest.mark.asyncio
    async def test_like_profile_success(self, service):
        mock_user_service_module = MagicMock()
        mock_user_service_module.UserService.get_user_profile = AsyncMock()

        with patch.dict('sys.modules', {'src.dating_bot.services.user_service': mock_user_service_module}):
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user_profile = {'user': mock_user}
            mock_user_service_module.UserService.get_user_profile.return_value = mock_user_profile

            with patch('src.dating_bot.services.recommendations.AsyncSessionLocal'):
                with patch('src.dating_bot.services.recommendations.UserRepository') as mock_user_repo:
                    mock_user_repo_instance = AsyncMock()
                    mock_user_repo_instance.get_user_by_id.return_value = MagicMock(id=2, name="Test", telegram_id=456)
                    mock_user_repo.return_value.__aenter__.return_value = mock_user_repo_instance

                    mock_like_service_module = MagicMock()
                    mock_like_service_module.LikeService.like_profile = AsyncMock(return_value={
                        "is_mutual": True,
                        "match_created": True,
                        "message": "Success"
                    })

                    with patch.dict('sys.modules', {'src.dating_bot.services.like_service': mock_like_service_module}):
                        result = await service.like_profile(123, 2)
                        assert result["is_mutual"] is True
                        mock_like_service_module.LikeService.like_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_dislike_profile_success(self, service):
        mock_user_service_module = MagicMock()
        mock_user_service_module.UserService.get_user_profile = AsyncMock()

        with patch.dict('sys.modules', {'src.dating_bot.services.user_service': mock_user_service_module}):
            mock_user = MagicMock()
            mock_user.id = 1
            mock_user_service_module.UserService.get_user_profile.side_effect = [
                {'user': mock_user}, 
                {'user': MagicMock(id=2)}  
            ]

            mock_like_service_module = MagicMock()
            mock_like_service_module.LikeService.dislike_profile = AsyncMock(return_value={
                "success": True,
                "message": "Disliked"
            })

            with patch.dict('sys.modules', {'src.dating_bot.services.like_service': mock_like_service_module}):
                result = await service.dislike_profile(123, 456)
                assert result["success"] is True
                mock_like_service_module.LikeService.dislike_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recommendations_user_not_found(self, service):
        with patch('src.dating_bot.services.recommendations.AsyncSessionLocal') as mock_session:
            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_telegram_id.return_value = None

            with patch('src.dating_bot.services.recommendations.UserRepository', return_value=mock_user_repo):
                result = await service.get_recommendations(123, 10)
                assert result == []

    @pytest.mark.asyncio
    async def test_get_recommendations_with_test_results(self, service):
        with patch('src.dating_bot.services.recommendations.AsyncSessionLocal') as mock_session:
            current_user = MagicMock()
            current_user.id = 1
            current_user.name = "Alice"
            current_user.sex = "female"
            current_user.search_sex = "male"
            current_user.goal = "relationship"
            
            other_user = MagicMock()
            other_user.id = 2
            other_user.name = "Bob"
            other_user.age = 25
            other_user.city = "Moscow"
            other_user.photo_id = "photo123"
            other_user.sex = "male"
            other_user.goal = "relationship"
            other_user.search_sex = "female"
            other_user.username = None
            other_user.telegram_id = "456"

            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_telegram_id.return_value = current_user
            mock_user_repo.get_all_active_users.return_value = [other_user]

            mock_test_repo = AsyncMock()
            current_test = MagicMock()
            current_test.is_completed = True
            current_test.answers = {1: 5}
            other_test = MagicMock()
            other_test.is_completed = True
            other_test.answers = {1: 4}
            mock_test_repo.get_test_result_by_user_id.side_effect = [current_test, other_test]

            mock_like_repo = AsyncMock()
            mock_like_repo.get_like.return_value = None
            mock_match_repo = AsyncMock()
            mock_match_repo.get_match.return_value = None
            mock_compatibility = MagicMock()
            mock_compatibility.calculate_compatibility.return_value = 85.5

            with patch.multiple('src.dating_bot.services.recommendations',
                                UserRepository=MagicMock(return_value=mock_user_repo),
                                TestResultRepository=MagicMock(return_value=mock_test_repo),
                                LikeRepository=MagicMock(return_value=mock_like_repo),
                                MatchRepository=MagicMock(return_value=mock_match_repo)):
                with patch.object(service, 'compatibility_calculator', mock_compatibility):
                    result = await service.get_recommendations(123, 10)
                    assert len(result) == 1
                    assert result[0]["id"] == 2
                    assert result[0]["name"] == "Bob"
                    assert result[0]["compatibility"] == 85.5

    @pytest.mark.asyncio
    async def test_get_recommendations_without_test_results(self, service):
        with patch('src.dating_bot.services.recommendations.AsyncSessionLocal') as mock_session:
            current_user = MagicMock()
            current_user.id = 1
            current_user.sex = "male"
            current_user.search_sex = "female"
            current_user.goal = "friendship"
            
            other_user = MagicMock()
            other_user.id = 2
            other_user.name = "Bob"
            other_user.age = 25
            other_user.city = "Moscow"
            other_user.photo_id = "photo123"
            other_user.sex = "female"
            other_user.goal = "friendship"
            other_user.search_sex = "male"
            other_user.username = None
            other_user.telegram_id = "456"

            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_telegram_id.return_value = current_user
            mock_user_repo.get_all_active_users.return_value = [other_user]

            mock_test_repo = AsyncMock()
            mock_test_repo.get_test_result_by_user_id.side_effect = [None, None]

            mock_like_repo = AsyncMock()
            mock_like_repo.get_like.return_value = None
            mock_match_repo = AsyncMock()
            mock_match_repo.get_match.return_value = None

            with patch.multiple('src.dating_bot.services.recommendations',
                                UserRepository=MagicMock(return_value=mock_user_repo),
                                TestResultRepository=MagicMock(return_value=mock_test_repo),
                                LikeRepository=MagicMock(return_value=mock_like_repo),
                                MatchRepository=MagicMock(return_value=mock_match_repo)):
                result = await service.get_recommendations(123, 10)
                assert len(result) == 1
                assert result[0]["id"] == 2

    @pytest.mark.asyncio
    async def test_get_recommendations_skip_liked(self, service):
        with patch('src.dating_bot.services.recommendations.AsyncSessionLocal') as mock_session:
            current_user = MagicMock()
            current_user.id = 1
            other_user = MagicMock()
            other_user.id = 2

            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_telegram_id.return_value = current_user
            mock_user_repo.get_all_active_users.return_value = [other_user]

            mock_test_repo = AsyncMock()
            mock_test_repo.get_test_result_by_user_id.return_value = None

            mock_like_repo = AsyncMock()
            mock_like = MagicMock()
            mock_like_repo.get_like.return_value = mock_like

            with patch.multiple('src.dating_bot.services.recommendations',
                                UserRepository=MagicMock(return_value=mock_user_repo),
                                TestResultRepository=MagicMock(return_value=mock_test_repo),
                                LikeRepository=MagicMock(return_value=mock_like_repo)):
                result = await service.get_recommendations(123, 10)
                assert len(result) == 0