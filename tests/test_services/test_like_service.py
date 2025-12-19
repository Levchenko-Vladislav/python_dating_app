import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.dating_bot.services.like_service import LikeService


class TestLikeService:

    @pytest.mark.asyncio
    async def test_like_profile_users_not_found(self):
        """Тест лайка профиля, когда пользователи не найдены"""
        with patch('src.dating_bot.services.like_service.AsyncSessionLocal') as mock_session:
            mock_repo = AsyncMock()
            mock_repo.get_user_by_id.return_value = None

            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_id.side_effect = [None, None]

            with patch('src.dating_bot.services.like_service.UserRepository', return_value=mock_user_repo):
                result = await LikeService.like_profile(1, 2)

                assert result["is_mutual"] == False
                assert result["match_created"] == False
                assert "не найден" in result["message"]

    @pytest.mark.asyncio
    async def test_like_profile_success_no_mutual(self):
        """Тест успешного лайка без взаимности"""
        with patch('src.dating_bot.services.like_service.AsyncSessionLocal') as mock_session:
            mock_user_repo = AsyncMock()
            mock_user1 = MagicMock()
            mock_user1.id = 1
            mock_user2 = MagicMock()
            mock_user2.id = 2
            mock_user_repo.get_user_by_id.side_effect = [mock_user1, mock_user2]

            mock_like_repo = AsyncMock()
            mock_like = MagicMock()
            mock_like_repo.create_like.return_value = mock_like
            mock_like_repo.check_mutual_like.return_value = False

            with patch.multiple('src.dating_bot.services.like_service',
                                UserRepository=MagicMock(return_value=mock_user_repo),
                                LikeRepository=MagicMock(return_value=mock_like_repo),
                                MatchRepository=MagicMock()):
                result = await LikeService.like_profile(1, 2)

                assert result["is_mutual"] == False
                assert result["match_created"] == False
                assert "отправлен" in result["message"]

    @pytest.mark.asyncio
    async def test_like_profile_success_with_mutual(self):
        """Тест успешного лайка с взаимностью и созданием мэтча"""
        with patch('src.dating_bot.services.like_service.AsyncSessionLocal') as mock_session:
            mock_user_repo = AsyncMock()
            mock_user1 = MagicMock()
            mock_user1.id = 1
            mock_user1.name = "Alice"
            mock_user1.username = "alice"
            mock_user1.telegram_id = 123
            mock_user2 = MagicMock()
            mock_user2.id = 2
            mock_user2.name = "Bob"
            mock_user2.username = "bob"
            mock_user2.telegram_id = 456
            mock_user_repo.get_user_by_id.side_effect = [mock_user1, mock_user2]

            mock_like_repo = AsyncMock()
            mock_like = MagicMock()
            mock_like_repo.create_like.return_value = mock_like
            mock_like_repo.check_mutual_like.return_value = True

            mock_match_repo = AsyncMock()
            mock_match = MagicMock()
            mock_match_repo.create_match.return_value = mock_match

            with patch.multiple('src.dating_bot.services.like_service',
                                UserRepository=MagicMock(return_value=mock_user_repo),
                                LikeRepository=MagicMock(return_value=mock_like_repo),
                                MatchRepository=MagicMock(return_value=mock_match_repo)):
                result = await LikeService.like_profile(1, 2)

                assert result["is_mutual"] == True
                assert result["match_created"] == True
                assert "взаимная симпатия" in result["message"]
                assert result["matched_with"]["id"] == 2
                assert result["matched_with"]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_dislike_profile_success(self):
        """Тест успешного дизлайка"""
        with patch('src.dating_bot.services.like_service.AsyncSessionLocal') as mock_session:
            mock_user_repo = AsyncMock()
            mock_user1 = MagicMock()
            mock_user2 = MagicMock()
            mock_user_repo.get_user_by_id.side_effect = [mock_user1, mock_user2]

            mock_like_repo = AsyncMock()
            mock_like = MagicMock()
            mock_like_repo.create_like.return_value = mock_like

            with patch.multiple('src.dating_bot.services.like_service',
                                UserRepository=MagicMock(return_value=mock_user_repo),
                                LikeRepository=MagicMock(return_value=mock_like_repo)):
                result = await LikeService.dislike_profile(1, 2)

                assert result["success"] == True
                assert "пропущен" in result["message"]

    @pytest.mark.asyncio
    async def test_get_user_matches_user_not_found(self):
        """Тест получения мэтчей пользователя, который не найден"""
        with patch('src.dating_bot.services.like_service.AsyncSessionLocal') as mock_session:
            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_telegram_id.return_value = None

            with patch('src.dating_bot.services.like_service.UserRepository', return_value=mock_user_repo):
                result = await LikeService.get_user_matches(123)

                assert result == []

    @pytest.mark.asyncio
    async def test_get_user_matches_success(self):
        """Тест успешного получения мэтчей"""
        with patch('src.dating_bot.services.like_service.AsyncSessionLocal') as mock_session:
            mock_user = MagicMock()
            mock_user.id = 1

            mock_other_user = MagicMock()
            mock_other_user.id = 2
            mock_other_user.name = "Test"
            mock_other_user.age = 25
            mock_other_user.city = "Moscow"
            mock_other_user.photo_id = "photo123"
            mock_other_user.username = "testuser"

            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_telegram_id.return_value = mock_user
            mock_user_repo.get_user_by_id.return_value = mock_other_user

            mock_match_repo = AsyncMock()
            mock_match = MagicMock()
            mock_match.id = 1
            mock_match.user1_id = 1
            mock_match.user2_id = 2
            mock_match.matched_at = "2024-01-01"
            mock_match_repo.get_user_matches.return_value = [mock_match]

            with patch.multiple('src.dating_bot.services.like_service',
                                UserRepository=MagicMock(return_value=mock_user_repo),
                                MatchRepository=MagicMock(return_value=mock_match_repo)):
                result = await LikeService.get_user_matches(123)

                assert len(result) == 1
                assert result[0]["match_id"] == 1
                assert result[0]["user"]["id"] == 2
                assert result[0]["user"]["name"] == "Test"

    @pytest.mark.asyncio
    async def test_get_likes_received_user_not_found(self):
        """Тест получения полученных лайков, когда пользователь не найден"""
        with patch('src.dating_bot.services.like_service.AsyncSessionLocal') as mock_session:
            mock_user_repo = AsyncMock()
            mock_user_repo.get_user_by_telegram_id.return_value = None

            with patch('src.dating_bot.services.like_service.UserRepository', return_value=mock_user_repo):
                result = await LikeService.get_likes_received(123)

                assert result == []