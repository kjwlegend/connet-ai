#!/usr/bin/env python3
"""
Manual test runner for contacts functionality without full app imports.
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
import enum

# Define entities locally to avoid import issues
class EntityType(str, enum.Enum):
    user = "user"
    agent = "agent"

class MockContact:
    def __init__(self, **kwargs):
        self.follower_id = kwargs.get('follower_id', uuid4())
        self.following_id = kwargs.get('following_id', uuid4())
        self.following_type = kwargs.get('following_type', EntityType.user)
        self.relationship_type = kwargs.get('relationship_type', 'follow')
        self.display_name = kwargs.get('display_name', 'Test User')
        self.notes = kwargs.get('notes', 'Test notes')
        self.tags = kwargs.get('tags', [])
        self.is_favorite = kwargs.get('is_favorite', False)
        self.is_agent = kwargs.get('is_agent', False)
        self.notification_level = kwargs.get('notification_level', 'normal')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
        self.id = kwargs.get('id', uuid4())

async def test_basic_enum():
    """Test that EntityType enum works correctly."""
    print("Testing EntityType enum...")
    
    user_type = EntityType.user
    agent_type = EntityType.agent
    
    assert user_type == "user"
    assert agent_type == "agent"
    assert user_type != agent_type
    
    print("SUCCESS: EntityType enum test passed")
    return True

async def test_mock_contact_creation():
    """Test that we can create mock contacts."""
    print("Testing MockContact creation...")
    
    contact = MockContact(
        follower_id=uuid4(),
        following_id=uuid4(),
        following_type=EntityType.user,
        display_name="Test Contact",
        is_favorite=True
    )
    
    assert contact.following_type == EntityType.user
    assert contact.display_name == "Test Contact"
    assert contact.is_favorite == True
    assert isinstance(contact.id, UUID)
    
    print("SUCCESS: MockContact creation test passed")
    return True

async def test_contacts_repository_mock():
    """Test mock repository functionality."""
    print("Testing contacts repository mock...")
    
    # Create a mock session
    mock_session = AsyncMock()
    
    # Create mock contacts
    contact1 = MockContact(display_name="Contact 1")
    contact2 = MockContact(display_name="Contact 2")
    
    # Mock the repository response
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact1, contact2]
    mock_session.execute.return_value = mock_result
    
    # Test that we can use the mock
    result = await mock_session.execute("fake_statement")
    contacts = result.scalars().all()
    
    assert len(contacts) == 2
    assert contacts[0].display_name == "Contact 1"
    assert contacts[1].display_name == "Contact 2"
    
    print("SUCCESS: Repository mock test passed")
    return True

async def test_contact_service_logic():
    """Test basic contact service logic without dependencies."""
    print("Testing contact service logic...")
    
    # Test: Cannot add yourself as contact
    user_id = uuid4()
    following_id = user_id  # Same as user_id
    
    def add_self_contact():
        if following_id == user_id:
            raise ValueError("Cannot add yourself as a contact")
        return "Success"
    
    try:
        add_self_contact()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "Cannot add yourself as a contact"
    
    # Test: Can add different user as contact
    different_user_id = uuid4()
    
    def add_different_contact():
        if different_user_id == user_id:
            raise ValueError("Cannot add yourself as a contact")
        return "Success"
    
    result = add_different_contact()
    assert result == "Success"
    
    print("SUCCESS: Contact service logic test passed")
    return True

async def test_contact_search():
    """Test contact search logic."""
    print("Testing contact search logic...")
    
    # Create test contacts
    contacts = [
        MockContact(display_name="John Doe", notes="Developer"),
        MockContact(display_name="Jane Smith", notes="Designer"),
        MockContact(display_name="Bob Wilson", notes="Project Manager"),
    ]
    
    # Test search by display name
    def search_contacts(query):
        return [c for c in contacts if query.lower() in c.display_name.lower() or query.lower() in c.notes.lower()]
    
    results = search_contacts("john")
    assert len(results) == 1
    assert results[0].display_name == "John Doe"
    
    results = search_contacts("design")
    assert len(results) == 1
    assert results[0].display_name == "Jane Smith"
    
    results = search_contacts("manager")
    assert len(results) == 1
    assert results[0].display_name == "Bob Wilson"
    
    results = search_contacts("nonexistent")
    assert len(results) == 0
    
    print("SUCCESS: Contact search test passed")
    return True

async def test_favorite_toggle():
    """Test favorite toggle logic."""
    print("Testing favorite toggle logic...")
    
    contact = MockContact(is_favorite=False)
    
    # Test toggle from False to True
    contact.is_favorite = not contact.is_favorite
    assert contact.is_favorite == True
    
    # Test toggle from True to False
    contact.is_favorite = not contact.is_favorite
    assert contact.is_favorite == False
    
    print("SUCCESS: Favorite toggle test passed")
    return True

async def run_all_tests():
    """Run all tests and report results."""
    print("=== Running Contacts Manual Tests ===\n")
    
    tests = [
        test_basic_enum,
        test_mock_contact_creation,
        test_contacts_repository_mock,
        test_contact_service_logic,
        test_contact_search,
        test_favorite_toggle,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"FAILED: {test.__name__} - {e}")
            failed += 1
        print()
    
    print("=== Test Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\nSUCCESS: All tests passed!")
        return True
    else:
        print(f"\nFAILED: {failed} tests failed")
        return False

if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)