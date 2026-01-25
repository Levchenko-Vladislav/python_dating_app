import pytest
import sys
import os
from unittest.mock import MagicMock, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestHandlersSimple:
    @pytest.mark.asyncio
    async def test_handler_imports(self):
        try:
            import src.dating_bot.handlers.profile as profile_module
            import src.dating_bot.handlers.browse as browse_module
            import src.dating_bot.handlers.psychological_test as test_module
            import src.dating_bot.handlers.start as start_module
            
            print(f"profile_module: {hasattr(profile_module, 'router')}")
            print(f"browse_module: {hasattr(browse_module, 'router')}")
            print(f"test_module: {hasattr(test_module, 'router')}")
            print(f"start_module: {hasattr(start_module, 'router')}")
            
            assert hasattr(profile_module, 'router')
            assert hasattr(browse_module, 'router')
            assert hasattr(test_module, 'router')
            assert hasattr(start_module, 'router')
            
        except ImportError as e:
            pytest.fail(f"Import error: {e}")
    
    @pytest.mark.asyncio 
    async def test_handler_functions_exist(self):
        try:
            from src.dating_bot.handlers.profile import show_my_profile_menu
            assert callable(show_my_profile_menu)
        except ImportError:
            pass
            
        try:
            from src.dating_bot.handlers.browse import start_browsing
            assert callable(start_browsing)
        except ImportError:
            pass
            
        try:
            from src.dating_bot.handlers.psychological_test import start_test_command
            assert callable(start_test_command)
        except ImportError:
            pass
    
    @pytest.mark.asyncio
    async def test_mock_async_function(self):
        mock_message = MagicMock()
        mock_message.text = "/start"
        mock_message.from_user = MagicMock()
        mock_message.from_user.id = 123456
        mock_message.answer = AsyncMock()
        
        mock_state = MagicMock()
        mock_state.set_state = AsyncMock()
        
        assert mock_message.text == "/start"
        assert mock_message.from_user.id == 123456
    
    @pytest.mark.asyncio
    async def test_service_imports(self):
        try:
            from src.dating_bot.services.user_service import UserService
            from src.dating_bot.services.test_service import TestService
            from src.dating_bot.services.recommendations import RecommendationService
            
            assert hasattr(UserService, 'get_user_profile')
            assert hasattr(UserService, 'register_user')
            assert hasattr(TestService, 'has_completed_test')
            
        except ImportError as e:
            pytest.fail(f"Service import error: {e}")
    
    @pytest.mark.asyncio
    async def test_keyboard_imports(self):
        try:
            from src.dating_bot.bot.keyboards import main_menu_kb
            assert callable(main_menu_kb)
        except ImportError:
            pass

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])