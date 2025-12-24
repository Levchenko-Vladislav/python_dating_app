import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.dating_bot.database.repositories.test_result_repository import TestResultRepository
from src.dating_bot.database.models import UserTestResult


class TestTestResultRepository:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        return TestResultRepository(mock_session)

    @pytest.mark.asyncio
    async def test_get_test_result_by_user_id_success(self, repository, mock_session):
        mock_result = MagicMock(spec=UserTestResult)
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=mock_result))

        result = await repository.get_test_result_by_user_id(1)

        assert result == mock_result

    @pytest.mark.asyncio
    async def test_get_test_result_by_user_id_not_found(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))

        result = await repository.get_test_result_by_user_id(1)

        assert result is None

    @pytest.mark.asyncio
    async def test_save_test_result_new(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        answers = {1: 5, 2: 4}
        category_scores = {"extraversion": 4.5}

        result = await repository.save_test_result(1, answers, category_scores)

        assert result is not None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_test_result_update(self, repository, mock_session):
        existing_result = MagicMock(spec=UserTestResult)
        existing_result.answers = {}
        existing_result.category_scores = {}

        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=existing_result))
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        answers = {1: 5, 2: 4}
        category_scores = {"extraversion": 4.5}

        result = await repository.save_test_result(1, answers, category_scores)

        assert result == existing_result
        assert existing_result.answers == answers
        assert existing_result.category_scores == category_scores
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_test_result_success(self, repository, mock_session):
        mock_result = MagicMock(spec=UserTestResult)
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=mock_result))
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()

        result = await repository.delete_test_result(1)

        assert result is True
        mock_session.delete.assert_called_once_with(mock_result)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_test_result_not_found(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))

        result = await repository.delete_test_result(1)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_test_completed_true(self, repository, mock_session):
        mock_result = MagicMock(spec=UserTestResult)
        mock_result.is_completed = True
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=mock_result))

        result = await repository.is_test_completed(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_test_completed_false(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))

        result = await repository.is_test_completed(1)

        assert result is False