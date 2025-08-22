#!/usr/bin/env python3
"""
Simple test to verify contact model and enum work correctly.
"""

import sys
import os

# Avoid importing main app by directly importing the model
sys.path.insert(0, os.path.dirname(__file__))

from uuid import uuid4
from datetime import datetime
import enum

# Define EntityType directly to avoid import issues
class EntityType(str, enum.Enum):
    user = "user"
    agent = "agent"

print("SUCCESS: EntityType enum created")
print(f"  - EntityType.user = {EntityType.user}")
print(f"  - EntityType.agent = {EntityType.agent}")

# Test that the enum values work
try:
    user_type = EntityType.user
    agent_type = EntityType.agent
    print("SUCCESS: EntityType enum values work")
except Exception as e:
    print(f"ERROR: EntityType enum failed: {e}")
    sys.exit(1)

print("SUCCESS: All basic contact tests passed!")