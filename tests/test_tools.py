"""
Tests for the security tools implementations.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from tools.nmap_tool import NmapTool
from tools.whois_tool import WhoisTool
from tools.shodan_tool import ShodanTool


@pytest.mark.asyncio
async def test_nmap_tool_basic_scan():
    """Test NmapTool basic scan functionality."""
    # Arrange
    tool = NmapTool(timeout=10)
    target = "localhost"
    
    # Act
    result = await tool.execute(target=target, scan_type="basic")
    
    # Assert
    assert isinstance(result, dict)
    assert "command" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_whois_tool_valid_domain():
    """Test WhoisTool with a valid domain."""
    # Arrange
    tool = WhoisTool()
    target = "example.com"
    
    with patch('whois.whois') as mock_whois:
        # Setup mock response
        mock_whois.return_value = Mock(
            domain_name="example.com",
            registrar="Test Registrar",
            creation_date=datetime.now(),
            expiration_date=datetime.now(),
            updated_date=datetime.now(),
            status="active",
            name_servers=["ns1.example.com"],
            emails=["admin@example.com"]
        )
        
        # Act
        result = await tool.execute(target=target)
        
        # Assert
        assert isinstance(result, dict)
        assert result["domain_name"] == "example.com"
        assert "registrar" in result


@pytest.mark.asyncio
async def test_shodan_tool_search():
    """Test ShodanTool search functionality."""
    # Arrange
    tool = ShodanTool(api_key="test_key", timeout=10)
    query = "port:80 org:example"
    
    with patch('shodan.Shodan') as mock_shodan:
        # Setup mock response
        mock_api = Mock()
        mock_api.search.return_value = {
            'total': 1,
            'matches': [{
                'ip_str': '93.184.216.34',
                'port': 80,
                'hostnames': ['example.com'],
                'org': 'Example Org',
                'location': {
                    'country_name': 'United States',
                    'city': 'Los Angeles'
                },
                'last_update': '2023-05-11T00:00:00.000000'
            }]
        }
        mock_shodan.return_value = mock_api
        
        # Act
        result = await tool.execute(query=query)
        
        # Assert
        assert isinstance(result, dict)
        assert result["total"] == 1
        assert len(result["matches"]) == 1
        assert "ip" in result["matches"][0]


@pytest.mark.asyncio
async def test_tool_input_validation():
    """Test input validation for all tools."""
    # Arrange
    nmap_tool = NmapTool()
    whois_tool = WhoisTool()
    shodan_tool = ShodanTool(api_key="test_key")
    
    # Act & Assert
    with pytest.raises(ValueError):
        await nmap_tool.execute(target="invalid;input")
    
    with pytest.raises(ValueError):
        await whois_tool.execute(target="invalid_domain")
    
    with pytest.raises(ValueError):
        await shodan_tool.execute(query="")
