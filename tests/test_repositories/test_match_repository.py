from sqlalchemy.exc import IntegrityError
from src.dating_bot.database.models import Match
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.dating_bot.database.repositories.match_repository import MatchRepository


class TestMatchRepository:

    @pytest.fixture
    def mock_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        return MatchRepository(mock_session)

    @pytest.mark.asyncio
    async def test_create_match_exists(self, repository, mock_session):
        existing_match = MagicMock(spec=Match)
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=existing_match))

        result = await repository.create_match(1, 2)

        assert result == existing_match

    @pytest.mark.asyncio
    async def test_create_match_integrity_error(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_session.commit = AsyncMock(side_effect=IntegrityError("test", "test", "test"))
        mock_session.rollback = AsyncMock()

        result = await repository.create_match(1, 2)

        assert result is None
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_match_success(self, repository, mock_session):
        mock_match = MagicMock(spec=Match)
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=mock_match))

        result = await repository.get_match(1, 2)

        assert result == mock_match


    @pytest.mark.asyncio
    async def test_archive_match_success(self, repository, mock_session):
        mock_match = MagicMock(spec=Match)
        mock_match.status = "active"
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=mock_match))
        mock_session.commit = AsyncMock()

        result = await repository.archive_match(1, 2)

        assert result is True
        assert mock_match.status == "archived"
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_archive_match_not_found(self, repository, mock_session):
        mock_session.execute.return_value = AsyncMock(scalar_one_or_none=MagicMock(return_value=None))

        result = await repository.archive_match(1, 2)

        assert result is False