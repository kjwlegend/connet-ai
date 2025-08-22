"""
Mention Parser

Parses @mentions from messages and routes them to appropriate contacts.
"""

import re
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.services.langgraph.state_models import ContactInfo


class MentionParser:
    """Parser for @mention syntax in messages"""
    
    # Regex pattern for @mentions - supports alphanumeric, underscore, hyphen
    MENTION_PATTERN = r'@([a-zA-Z0-9_-]+)'
    
    def __init__(self):
        pass
    
    def extract_mentions(self, message: str) -> List[str]:
        """Extract all @mentions from a message"""
        
        mentions = re.findall(self.MENTION_PATTERN, message)
        # Remove duplicates while preserving order
        unique_mentions = []
        seen = set()
        
        for mention in mentions:
            if mention not in seen:
                unique_mentions.append(mention)
                seen.add(mention)
        
        return unique_mentions
    
    def has_mentions(self, message: str) -> bool:
        """Check if message contains any @mentions"""
        return bool(re.search(self.MENTION_PATTERN, message))
    
    def remove_mentions(self, message: str) -> str:
        """Remove all @mentions from message, leaving clean text"""
        return re.sub(self.MENTION_PATTERN, '', message).strip()
    
    def replace_mentions_with_names(
        self, 
        message: str, 
        contact_mapping: Dict[str, str]
    ) -> str:
        """Replace @mentions with display names"""
        
        def replace_mention(match):
            agent_name = match.group(1)
            display_name = contact_mapping.get(agent_name, agent_name)
            return f"@{display_name}"
        
        return re.sub(self.MENTION_PATTERN, replace_mention, message)
    
    def find_mentioned_contacts(
        self,
        message: str,
        available_contacts: List[ContactInfo]
    ) -> List[ContactInfo]:
        """Find contacts that are mentioned in the message"""
        
        mentioned_names = self.extract_mentions(message)
        if not mentioned_names:
            return []
        
        mentioned_contacts = []
        
        # Create lookup map by agent name
        agent_name_map = {contact["agent_name"]: contact for contact in available_contacts}
        
        for mentioned_name in mentioned_names:
            if mentioned_name in agent_name_map:
                mentioned_contacts.append(agent_name_map[mentioned_name])
        
        return mentioned_contacts
    
    def build_routing_context(
        self,
        message: str,
        available_contacts: List[ContactInfo]
    ) -> Dict[str, Any]:
        """Build routing context for message with mentions"""
        
        mentions = self.extract_mentions(message)
        mentioned_contacts = self.find_mentioned_contacts(message, available_contacts)
        
        return {
            "original_message": message,
            "mentions_found": mentions,
            "mentioned_contacts": mentioned_contacts,
            "has_mentions": len(mentions) > 0,
            "routing_strategy": "mention_based" if mentions else "default",
            "clean_message": self.remove_mentions(message) if mentions else message
        }
    
    def validate_mentions(
        self,
        message: str,
        available_contacts: List[ContactInfo]
    ) -> Dict[str, Any]:
        """Validate that all mentions in message correspond to available contacts"""
        
        mentions = self.extract_mentions(message)
        available_names = {contact["agent_name"] for contact in available_contacts}
        
        valid_mentions = []
        invalid_mentions = []
        
        for mention in mentions:
            if mention in available_names:
                valid_mentions.append(mention)
            else:
                invalid_mentions.append(mention)
        
        return {
            "all_valid": len(invalid_mentions) == 0,
            "valid_mentions": valid_mentions,
            "invalid_mentions": invalid_mentions,
            "validation_message": self._build_validation_message(invalid_mentions)
        }
    
    def _build_validation_message(self, invalid_mentions: List[str]) -> Optional[str]:
        """Build user-friendly validation message for invalid mentions"""
        
        if not invalid_mentions:
            return None
        
        if len(invalid_mentions) == 1:
            return f"Unknown agent @{invalid_mentions[0]}. Please check the agent name."
        else:
            mentions_str = ", ".join(f"@{mention}" for mention in invalid_mentions)
            return f"Unknown agents: {mentions_str}. Please check the agent names."
    
    def suggest_corrections(
        self,
        invalid_mention: str,
        available_contacts: List[ContactInfo],
        max_suggestions: int = 3
    ) -> List[str]:
        """Suggest corrections for invalid mentions based on similarity"""
        
        available_names = [contact["agent_name"] for contact in available_contacts]
        
        # Simple similarity based on string distance
        suggestions = []
        
        for name in available_names:
            # Simple similarity check - starts with same characters
            if name.lower().startswith(invalid_mention.lower()[:2]) and len(name) >= len(invalid_mention) - 2:
                suggestions.append(name)
            
            if len(suggestions) >= max_suggestions:
                break
        
        return suggestions