import pytest
from app.db.archive_crud import get_archive_by_id, delete_archive_by_id, save_archive, get_archived_responses
from app.models.sql_models import ArchivedResponse, Portfolio
from app.models.schemas import ArchiveCreate
from app.db.session import get_db, AsyncSessionLocal
from fastapi import Depends
import asyncio

@pytest.mark.asyncio
async def test_get_archive_by_id_found():
    print("test_get_archive_by_id_found")
    # Arrange - get database session using Depends like the endpoints
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # Act - call the get_archive_by_id function
    result = await get_archive_by_id(db=db, archive_id=1, user_id=8)

    # Assert - check the result
    assert result is not None
    assert result.id == 1
    assert result.user_id == 8
    assert result.portfolio_id == 22
    assert result.original_question == "how do I improve this portfolio, i want long term income and short term growth!"
    print("test_get_archive_by_id_found SUCCESS")


@pytest.mark.asyncio
async def test_get_archive_by_id_not_found():
    print("test_get_archive_by_id_not_found")
    # Arrange - get database session using Depends like the endpoints
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # Act - call the get_archive_by_id function
    result = await get_archive_by_id(db=db, archive_id=999, user_id=8)

    # Assert - check the result is None
    assert result is None
    print("test_get_archive_by_id_not_found SUCCESS")


@pytest.mark.asyncio
async def test_get_archive_by_id_wrong_user():
    print("test_get_archive_by_id_wrong_user")
    # Arrange - get database session using Depends like the endpoints
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # Act - call the get_archive_by_id function with wrong user
    result = await get_archive_by_id(db=db, archive_id=1, user_id=999)

    # Assert - check the result is None (archive exists but belongs to different user)
    assert result is None
    print("test_get_archive_by_id_wrong_user SUCCESS")


@pytest.mark.asyncio
async def test_get_archived_responses_user_has_archives():
    print("test_get_archived_responses_user_has_archives")
    # Arrange - get database session using Depends like the endpoints
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # Act - call the get_archived_responses function
    result = await get_archived_responses(user_id=8, db=db)

    # Assert - check the result
    assert result is not None
    assert len(result) >= 2  # User 8 has at least 2 archives
    assert all(archive.user_id == 8 for archive in result)
    print("test_get_archived_responses_user_has_archives SUCCESS")


@pytest.mark.asyncio
async def test_get_archived_responses_user_no_archives():
    print("test_get_archived_responses_user_no_archives")
    # Arrange - get database session using Depends like the endpoints
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # Act - call the get_archived_responses function for user with no archives
    result = await get_archived_responses(user_id=999, db=db)

    # Assert - check the result is empty
    assert result is not None
    assert len(result) == 0
    print("test_get_archived_responses_user_no_archives SUCCESS")


@pytest.mark.asyncio
async def test_save_archive_success():
    print("test_save_archive_success")
    # Arrange - get database session using Depends like the endpoints and create archive data
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    archive_data = ArchiveCreate(
        portfolio_id=22,  # Portfolio that exists for user 8
        original_question="Test question for save",
        openai_response="<p>Test response with <script>alert('xss')</script></p>"
    )

    # Act - call the save_archive function
    result = await save_archive(db=db, archive_data=archive_data, user_id=8)

    # Assert - check the result
    assert result is not None
    assert result.user_id == 8
    assert result.portfolio_id == 22
    assert result.original_question == "Test question for save"
    # Check that HTML is escaped (the exact escaping may vary)
    assert "script" in result.openai_response.lower()
    assert "alert" in result.openai_response.lower()
    print("test_save_archive_success SUCCESS")


@pytest.mark.asyncio
async def test_save_archive_portfolio_not_found():
    print("test_save_archive_portfolio_not_found")
    # Arrange - get database session using Depends like the endpoints and create archive data with non-existent portfolio
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    archive_data = ArchiveCreate(
        portfolio_id=999,  # Portfolio that doesn't exist
        original_question="Test question",
        openai_response="<p>Test response</p>"
    )

    # Act & Assert - call the save_archive function and expect ValueError
    with pytest.raises(ValueError, match="Portfolio with id 999 does not exist"):
        await save_archive(db=db, archive_data=archive_data, user_id=8)
    print("test_save_archive_portfolio_not_found SUCCESS")


@pytest.mark.asyncio
async def test_save_archive_no_data():
    print("test_save_archive_no_data")
    # Arrange - get database session using Depends like the endpoints
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # Act & Assert - call the save_archive function with no data and expect ValueError
    with pytest.raises(ValueError, match="No archive data provided"):
        await save_archive(db=db, archive_data=None, user_id=8)
    print("test_save_archive_no_data SUCCESS")


@pytest.mark.asyncio
async def test_delete_archive_by_id_success():
    print("test_delete_archive_by_id_success")
    # Arrange - get database session using Depends like the endpoints
    db_gen = get_db()
    db = await db_gen.__anext__()
    
    # First create an archive to delete
    archive_data = ArchiveCreate(
        portfolio_id=22,
        original_question="Test question for deletion",
        openai_response="<p>Test response</p>"
    )
    created_archive = await save_archive(db=db, archive_data=archive_data, user_id=8)

    # Act - call the delete_archive_by_id function
    result = await delete_archive_by_id(db=db, archive_id=created_archive.id, user_id=8)

    # Assert - check the result
    assert result is True
    print("test_delete_archive_by_id_success SUCCESS")


@pytest.mark.asyncio
async def test_delete_archive_by_id_not_found_and_wrong_user():
    from tests.test_db_session import AsyncSessionLocal
    print("test_delete_archive_by_id_not_found")
    # Arrange - get database session using AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        # Act - call the delete_archive_by_id function with non-existent archive
        result = await delete_archive_by_id(db=db, archive_id=999, user_id=8)

        # Assert - check the result is False
        assert result is False

        result = await delete_archive_by_id(db=db, archive_id=1, user_id=999)
        assert result is False

        print("test_delete_archive_by_id_not_found SUCCESS")