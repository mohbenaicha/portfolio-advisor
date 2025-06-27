import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.core import mcp_client


@pytest.mark.asyncio
async def test_validate_prompt_valid(monkeypatch):
    print("test_validate_prompt_valid")
    # Arrange - mock the database
    mock_db = MagicMock()
    monkeypatch.setattr(
        mcp_client,
        "call_provider_endpoint",
        AsyncMock(side_effect=[{"valid": True}, {"valid": True}]),
    )

    # Act - call the validate_prompt function
    result = await mcp_client.validate_prompt("question", 1, 2, mock_db)

    # Assert - check the result
    assert result is None  # None means valid
    print("test_validate_prompt_valid SUCCESS")


@pytest.mark.asyncio
async def test_validate_prompt_invalid_question(monkeypatch):
    print("test_validate_prompt_invalid_question")
    # Arrange - mock the database
    mock_db = MagicMock()
    monkeypatch.setattr(
        mcp_client, "call_provider_endpoint", AsyncMock(side_effect=[{"valid": False}])
    )

    # Act - call the validate_prompt function
    result = await mcp_client.validate_prompt("bad question", 1, 2, mock_db)

    # Assert - check the result
    assert isinstance(result, dict)
    assert result["archived"] is False
    assert "Invalid question" in result["summary"]
    print("test_validate_prompt_invalid_question SUCCESS")


@pytest.mark.asyncio
async def test_validate_prompt_invalid_goal(monkeypatch):
    print("test_validate_prompt_invalid_goal")
    # Arrange - mock the database
    mock_db = MagicMock()
    mock_db.execute = AsyncMock(
        return_value=MagicMock(
            scalar_one_or_none=MagicMock(return_value="Test Portfolio")
        )
    )
    monkeypatch.setattr(
        mcp_client,
        "call_provider_endpoint",
        AsyncMock(side_effect=[{"valid": True}, {"valid": False}]),
    )

    # Act - call the validate_prompt function
    result = await mcp_client.validate_prompt("question", 1, 2, mock_db)

    # Assert - check the result
    assert isinstance(result, dict)
    assert result["archived"] is False
    assert "Test Portfolio" in result["summary"]
    print("test_validate_prompt_invalid_goal SUCCESS")


@pytest.mark.asyncio
async def test_construct_initial_messages(monkeypatch):
    print("test_construct_initial_messages")
    # Arrange
    monkeypatch.setattr(
        mcp_client, "build_system_prompt", AsyncMock(return_value="system prompt")
    )

    # Act
    result = await mcp_client.construct_initial_messages("question", 2, 1)

    # Assert
    assert result[0]["role"] == "system"
    assert result[0]["content"] == "system prompt"
    assert result[1]["role"] == "user"
    assert result[1]["content"] == "question"
    print("test_construct_initial_messages SUCCESS")


@pytest.mark.asyncio
async def test_handle_tool_call(monkeypatch):
    print("test_handle_tool_call")
    # Arrange
    func_mock = MagicMock()
    func_mock.name = 'func'
    func_mock.arguments = '{"foo": "bar"}'
    fake_choice = MagicMock()
    fake_choice.message.tool_calls = [
        MagicMock(function=func_mock, id="id1")
    ]
    messages = []
    tool_outputs = {}
    monkeypatch.setattr(
        mcp_client, "call_provider_endpoint", AsyncMock(return_value={"result": 42})
    )
    monkeypatch.setattr(mcp_client, "endpoint_map", {"func": "/fake-endpoint"})

    # Act
    _, messages_out, tool_outputs_out, stop = await mcp_client.handle_tool_call(
        fake_choice, messages, tool_outputs, 1, 2, False
    )

    # Assert
    assert "func" in tool_outputs_out
    assert messages_out[-1]["name"] == "func"
    assert messages_out[-1]["content"] == '{"result": 42}'
    print("test_handle_tool_call SUCCESS")


@pytest.mark.asyncio
async def test_run_mcp_client_pipeline_prompt_limit(monkeypatch):
    print("test_run_mcp_client_pipeline_prompt_limit")
    # Arrange
    monkeypatch.setattr(
        mcp_client.UserSessionManager,
        "get_total_prompts_used",
        AsyncMock(return_value=3),
    )
    # Act
    result = await mcp_client.run_mcp_client_pipeline("q", 1, 2, MagicMock())
    # Assert
    assert result["archived"] is False
    assert "maximum number of prompts" in result["summary"]
    print("test_run_mcp_client_pipeline_prompt_limit SUCCESS")


# edge case
@pytest.mark.asyncio
async def test_validate_prompt_empty_inputs(monkeypatch):
    # Arrange
    mock_db = MagicMock()
    monkeypatch.setattr(
        mcp_client,
        "call_provider_endpoint",
        AsyncMock(side_effect=[{"valid": True}, {"valid": True}]),
    )
    # Act
    result = await mcp_client.validate_prompt("", 0, 0, mock_db)
    # Assert
    assert result is None


# edge case
@pytest.mark.asyncio
async def test_validate_prompt_malformed_response(monkeypatch):
    # Arrange
    mock_db = MagicMock()
    # call_provider_endpoint returns a string instead of dict
    monkeypatch.setattr(
        mcp_client, "call_provider_endpoint", AsyncMock(side_effect=["notadict"]))
    # Act & Assert
    with pytest.raises(AttributeError):
        await mcp_client.validate_prompt("question", 1, 2, mock_db)


# edge case
@pytest.mark.asyncio
async def test_handle_tool_call_multiple_tools(monkeypatch):
    # Arrange
    func1 = MagicMock(); func1.name = 'func1'; func1.arguments = '{"foo": "bar"}'
    func2 = MagicMock(); func2.name = 'func2'; func2.arguments = '{"baz": "qux"}'
    fake_choice = MagicMock()
    fake_choice.message.tool_calls = [
        MagicMock(function=func1, id="id1"),
        MagicMock(function=func2, id="id2")
    ]
    messages = []
    tool_outputs = {}
    monkeypatch.setattr(
        mcp_client, "call_provider_endpoint", AsyncMock(return_value={"result": 42})
    )
    monkeypatch.setattr(mcp_client, "endpoint_map", {"func1": "/fake1", "func2": "/fake2"})
    # Act
    _, messages_out, tool_outputs_out, stop = await mcp_client.handle_tool_call(
        fake_choice, messages, tool_outputs, 1, 2, False
    )
    # Assert
    assert "func1" in tool_outputs_out
    assert "func2" in tool_outputs_out
    assert messages_out[-1]["name"] == "func2"
    assert messages_out[-1]["content"] == '{"result": 42}'
