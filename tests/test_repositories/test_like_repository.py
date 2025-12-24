from sqlalchemy.exc import IntegrityError
from datetime import datetime
from src.dating_bot.database.models import Like
from unittest.mock import patch
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.dating_bot.database.repositories.like_repository import LikeRepository


class TestLikeRepository:

    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        return LikeRepository(mock_session)

    @pytest.mark.asyncio
    async def test_get_likes_received(self, repository, mock_session):
        mock_like1 = MagicMock()
        mock_like2 = MagicMock()

        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = [mock_like1, mock_like2]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars_result

        mock_session.execute.return_value = mock_result

        result = await repository.get_likes_received(1, only_likes=True)

        assert len(result) == 2
        assert result[0] == mock_like1
        assert result[1] == mock_like2

    @pytest.mark.asyncio
    async def test_get_likes_given(self, repository, mock_session):
        mock_like = MagicMock()

        mock_scalars_result = MagicMock()
        mock_scalars_result.all.return_value = [mock_like]

        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars_result

        mock_session.execute.return_value = mock_result

        result = await repository.get_likes_given(1, only_likes=True)

        assert len(result) == 1
        assert result[0] == mock_like

    @pytest.mark.asyncio
    async def test_create_like_new(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await repository.create_like(1, 2, is_like=True)

        assert result is not None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_like_update(self, repository, mock_session):
        existing_like = MagicMock(spec=Like)
        existing_like.is_like = False
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=existing_like))
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await repository.create_like(1, 2, is_like=True)

        assert result == existing_like
        assert existing_like.is_like == True
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_like_integrity_error(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_session.commit = AsyncMock(side_effect=IntegrityError("test", "test", "test"))
        mock_session.rollback = AsyncMock()

        result = await repository.create_like(1, 2, is_like=True)

        assert result is None
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_like_found(self, repository, mock_session):
        mock_like = MagicMock(spec=Like)
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=mock_like))

        result = await repository.get_like(1, 2)

        assert result == mock_like

    @pytest.mark.asyncio
    async def test_get_like_not_found(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))

        result = await repository.get_like(1, 2)

        assert result is None

    @pytest.mark.asyncio
    async def test_check_mutual_like_true(self, repository, mock_session):
        like1 = MagicMock(spec=Like)
        like1.is_like = True
        like2 = MagicMock(spec=Like)
        like2.is_like = True

        with patch.object(repository, 'get_like') as mock_get_like:
            mock_get_like.side_effect = [like1, like2]

            result = await repository.check_mutual_like(1, 2)

            assert result is True

    @pytest.mark.asyncio
    async def test_check_mutual_like_false(self, repository, mock_session):
        with patch.object(repository, 'get_like') as mock_get_like:
            mock_get_like.side_effect = [None, MagicMock()]

            result = await repository.check_mutual_like(1, 2)

            assert result is False

        like1 = MagicMock(spec=Like)
        like1.is_like = False
        with patch.object(repository, 'get_like') as mock_get_like:
            mock_get_like.side_effect = [like1, MagicMock()]

            result = await repository.check_mutual_like(1, 2)

            assert result is False

    @pytest.mark.asyncio
    async def test_delete_like_success(self, repository, mock_session):
        mock_like = MagicMock(spec=Like)
        with patch.object(repository, 'get_like', return_value=mock_like):
            mock_session.delete = AsyncMock()
            mock_session.commit = AsyncMock()

            result = await repository.delete_like(1, 2)

            assert result is True
            mock_session.delete.assert_called_once_with(mock_like)
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_like_not_found(self, repository, mock_session):
        with patch.object(repository, 'get_like', return_value=None):
            result = await repository.delete_like(1, 2)

            assert result is False

    @pytest.mark.asyncio
    async def test_get_mutual_likes_for_user(self, repository, mock_session):
        mock_like = MagicMock(spec=Like)
        mock_like.user_to_id = 2
        mock_like.created_at = datetime.now()

        reverse_like = MagicMock(spec=Like)
        reverse_like.is_like = True
        reverse_like.created_at = datetime.now()

        with patch.object(repository, 'get_likes_given', return_value=[mock_like]):
            with patch.object(repository, 'get_like', return_value=reverse_like):
                result = await repository.get_mutual_likes_for_user(1)

                assert len(result) == 1
                assert result[0]['user_id'] == 2