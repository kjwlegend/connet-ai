#!/usr/bin/env python3
"""
Validation script for migrated agent data.
This script validates that the migrated data matches the AIAgentModel structure.
"""

import json
import sys
from pathlib import Path
from uuid import UUID
from datetime import datetime
from typing import Dict, List, Any

def validate_agent_data(agent: Dict[str, Any]) -> List[str]:
    """Validate a single agent against AIAgentModel structure."""
    errors = []
    
    # Required fields from AIAgentModel
    required_fields = {
        'id': str,
        'name': str,
        'display_name': str,
        'description': str,
        'agent_type': str,
        'version': str,
        'status': str,
        'is_public': bool,
        'is_active': bool,
        'conversation_style': str,
        'system_prompt': str,
        'personality_config': dict,
        'model_preferences': dict,
        'capabilities': list,
        'required_permissions': list,
        'tags': list,
        'usage_count': int,
        'follower_count': int,
        'created_by': str,
        'created_at': str,
        'updated_at': str
    }
    
    optional_fields = {
        'avatar_url': (str, type(None)),
        'avatar_style': (str, type(None)),
        'color_theme': (str, type(None)),
        'category': (str, type(None)),
        'agent_metadata': (dict, type(None)),
        'description_embedding': (list, type(None)),
        'capabilities_embedding': (list, type(None)),
        'last_used_at': (str, type(None))
    }
    
    # Check required fields
    for field, expected_type in required_fields.items():
        if field not in agent:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(agent[field], expected_type):
            errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(agent[field]).__name__}")
    
    # Check optional fields
    for field, expected_types in optional_fields.items():
        if field in agent:
            if not isinstance(agent[field], expected_types):
                type_names = " or ".join([t.__name__ for t in expected_types if t is not type(None)])
                errors.append(f"Field '{field}' should be {type_names}, got {type(agent[field]).__name__}")
    
    # Check for extra fields
    all_expected_fields = set(required_fields.keys()) | set(optional_fields.keys())
    extra_fields = set(agent.keys()) - all_expected_fields
    if extra_fields:
        errors.append(f"Extra fields found: {', '.join(extra_fields)}")
    
    # Validate specific field constraints
    if 'name' in agent and len(agent['name']) > 50:
        errors.append(f"Field 'name' exceeds max length of 50: {len(agent['name'])}")
    
    if 'display_name' in agent and len(agent['display_name']) > 100:
        errors.append(f"Field 'display_name' exceeds max length of 100: {len(agent['display_name'])}")
    
    if 'description' in agent and len(agent['description']) > 500:
        errors.append(f"Field 'description' exceeds max length of 500: {len(agent['description'])}")
    
    # Validate UUID fields
    uuid_fields = ['id', 'created_by']
    for field in uuid_fields:
        if field in agent:
            try:
                UUID(agent[field])
            except ValueError:
                errors.append(f"Field '{field}' is not a valid UUID: {agent[field]}")
    
    # Validate datetime fields
    datetime_fields = ['created_at', 'updated_at']
    for field in datetime_fields:
        if field in agent and agent[field]:
            try:
                datetime.fromisoformat(agent[field])
            except ValueError:
                errors.append(f"Field '{field}' is not a valid ISO datetime: {agent[field]}")
    
    return errors

def main():
    """Main validation function."""
    input_file = Path("scripts/migrated_agents.json")
    
    if not input_file.exists():
        print(f"Error: Migrated data file not found: {input_file}")
        return
    
    print("Agent Data Validation Script")
    print("=" * 50)
    
    # Load migrated data
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading migrated data: {e}")
        return
    
    migration_info = data.get("migration_info", {})
    agents = data.get("agents", [])
    
    print(f"Migration date: {migration_info.get('migration_date')}")
    print(f"Total agents: {len(agents)}")
    print(f"Validating agent data structure...")
    print()
    
    # Validate each agent
    total_errors = 0
    agents_with_errors = 0
    
    for i, agent in enumerate(agents):
        errors = validate_agent_data(agent)
        if errors:
            agents_with_errors += 1
            total_errors += len(errors)
            print(f"Agent {i+1} ('{agent.get('display_name', 'Unknown')}'): {len(errors)} errors")
            for error in errors:
                print(f"  - {error}")
            print()
    
    # Summary
    print("Validation Summary:")
    print(f"Total agents: {len(agents)}")
    print(f"Agents with errors: {agents_with_errors}")
    print(f"Agents valid: {len(agents) - agents_with_errors}")
    print(f"Total errors: {total_errors}")
    
    if total_errors == 0:
        print("\n✅ All agents passed validation!")
        print("The migrated data is ready for database import.")
    else:
        print("\n❌ Validation failed!")
        print("Please fix the errors above before importing to database.")
        return False
    
    # Check sample data structure
    if agents:
        print("\nSample agent structure:")
        sample_agent = agents[0]
        print("Fields present:")
        for field in sorted(sample_agent.keys()):
            value = sample_agent[field]
            if isinstance(value, str) and len(value) > 50:
                display_value = value[:50] + "..."
            else:
                display_value = value
            print(f"  {field}: {type(value).__name__} = {display_value}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)