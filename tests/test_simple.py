"""
Test simple pour vérifier que le système de tests fonctionne
"""
import pytest
from unittest.mock import MagicMock


def test_simple_assertion():
    """Test basique pour vérifier que pytest fonctionne"""
    assert 1 + 1 == 2


def test_string_operations():
    """Test basique des opérations sur strings"""
    assert "aegis".upper() == "AEGIS"
    assert len("test") == 4


@pytest.mark.asyncio
async def test_async_simple():
    """Test asynchrone simple"""
    async def async_func():
        return "success"
    
    result = await async_func()
    assert result == "success"


def test_mock_usage():
    """Test basique des mocks"""
    mock_obj = MagicMock()
    mock_obj.return_value = "mocked"
    
    assert mock_obj() == "mocked"
    mock_obj.assert_called_once()


class TestSimpleClass:
    """Classe de tests simple"""
    
    def test_class_method(self):
        """Test dans une classe"""
        assert True
    
    @pytest.mark.asyncio 
    async def test_async_class_method(self):
        """Test asynchrone dans une classe"""
        assert True