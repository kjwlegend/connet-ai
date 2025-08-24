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

    # Enhanced Mention Parsing for Priority 3

    def parse_mention_with_context(
        self,
        message: str,
        available_contacts: List[ContactInfo]
    ) -> Dict[str, Any]:
        """Parse mentions with enhanced context analysis"""
        
        mentions = self.extract_mentions(message)
        if not mentions:
            return {
                "has_mentions": False,
                "mention_contexts": [],
                "routing_strategy": "no_mention",
                "message_intent": "general"
            }
        
        mention_contexts = []
        for mention in mentions:
            context = self._analyze_mention_context(message, mention, available_contacts)
            mention_contexts.append(context)
        
        # Determine overall routing strategy
        routing_strategy = self._determine_routing_strategy(mention_contexts, message)
        message_intent = self._analyze_message_intent(message)
        
        return {
            "has_mentions": True,
            "mentions": mentions,
            "mention_contexts": mention_contexts,
            "routing_strategy": routing_strategy,
            "message_intent": message_intent,
            "collaboration_mode": self._suggest_collaboration_mode(mention_contexts, message_intent)
        }

    def _analyze_mention_context(
        self,
        message: str,
        mention: str,
        available_contacts: List[ContactInfo]
    ) -> Dict[str, Any]:
        """Analyze the context around a specific mention"""
        
        # Find the contact
        contact = next(
            (c for c in available_contacts if c["agent_name"] == mention),
            None
        )
        
        if not contact:
            return {
                "mention": mention,
                "valid": False,
                "contact_id": None,
                "context_type": "invalid",
                "surrounding_text": self._extract_surrounding_text(message, mention)
            }
        
        # Extract text around the mention
        surrounding_text = self._extract_surrounding_text(message, mention)
        
        # Analyze context type
        context_type = self._classify_mention_context(surrounding_text, message)
        
        # Determine priority based on context
        priority = self._calculate_mention_priority(context_type, surrounding_text, contact)
        
        return {
            "mention": mention,
            "valid": True,
            "contact_id": contact["contact_id"],
            "agent_id": contact["agent_id"],
            "contact_name": contact["display_name"],
            "context_type": context_type,
            "surrounding_text": surrounding_text,
            "priority": priority,
            "capabilities": contact.get("capabilities", []),
            "expertise_match": self._assess_expertise_match(message, contact)
        }

    def _extract_surrounding_text(self, message: str, mention: str, window: int = 10) -> str:
        """Extract text around a mention for context analysis"""
        
        mention_pattern = f"@{mention}"
        match = re.search(re.escape(mention_pattern), message, re.IGNORECASE)
        
        if not match:
            return ""
        
        start = max(0, match.start() - window)
        end = min(len(message), match.end() + window)
        
        return message[start:end].strip()

    def _classify_mention_context(self, surrounding_text: str, full_message: str) -> str:
        """Classify the type of mention context"""
        
        # Direct question patterns
        question_patterns = [
            r"@\w+\s+(what|how|why|when|where|can you|could you|would you)",
            r"@\w+[,:]?\s*(please|help|assist)"
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, surrounding_text, re.IGNORECASE):
                return "direct_question"
        
        # Comparison patterns
        comparison_patterns = [
            r"@\w+\s+(vs|versus|compared to)",
            r"compare\s+@\w+",
            r"@\w+\s+and\s+@\w+\s+(differ|same|similar)"
        ]
        
        for pattern in comparison_patterns:
            if re.search(pattern, full_message, re.IGNORECASE):
                return "comparison_request"
        
        # Collaboration patterns
        collaboration_patterns = [
            r"@\w+\s+and\s+@\w+\s+(work together|collaborate|discuss)",
            r"(all|everyone)\s+@\w+"
        ]
        
        for pattern in collaboration_patterns:
            if re.search(pattern, full_message, re.IGNORECASE):
                return "collaboration_request"
        
        # Debate patterns
        debate_patterns = [
            r"@\w+\s+(debate|argue|discuss)",
            r"(pros and cons|different perspectives).*@\w+"
        ]
        
        for pattern in debate_patterns:
            if re.search(pattern, full_message, re.IGNORECASE):
                return "debate_request"
        
        return "general_mention"

    def _calculate_mention_priority(
        self,
        context_type: str,
        surrounding_text: str,
        contact: ContactInfo
    ) -> int:
        """Calculate priority for mention processing"""
        
        base_priority = 5
        
        # Context type adjustments
        context_priorities = {
            "direct_question": 3,
            "comparison_request": 2,
            "collaboration_request": 1,
            "debate_request": 1,
            "general_mention": 0
        }
        
        priority = base_priority + context_priorities.get(context_type, 0)
        
        # Adjust based on urgency keywords
        urgency_keywords = ["urgent", "immediately", "asap", "quickly", "help"]
        if any(keyword in surrounding_text.lower() for keyword in urgency_keywords):
            priority += 2
        
        return min(priority, 10)  # Cap at 10

    def _assess_expertise_match(self, message: str, contact: ContactInfo) -> float:
        """Assess how well contact's expertise matches the message topic"""
        
        capabilities = contact.get("capabilities", [])
        if not capabilities:
            return 0.5  # Default neutral score
        
        message_lower = message.lower()
        matches = 0
        
        for capability in capabilities:
            if capability.lower() in message_lower:
                matches += 1
        
        # Return match ratio
        return min(matches / len(capabilities) if capabilities else 0, 1.0)

    def _analyze_message_intent(self, message: str) -> str:
        """Analyze the overall intent of the message"""
        
        message_lower = message.lower()
        
        # Question intent
        if any(word in message_lower for word in ["what", "how", "why", "when", "where", "?"]):
            return "question"
        
        # Request intent
        if any(word in message_lower for word in ["please", "can you", "could you", "would you", "help"]):
            return "request"
        
        # Comparison intent
        if any(word in message_lower for word in ["compare", "vs", "versus", "difference", "better"]):
            return "comparison"
        
        # Debate intent
        if any(word in message_lower for word in ["debate", "argue", "discuss", "pros and cons"]):
            return "debate"
        
        # Collaboration intent
        if any(word in message_lower for word in ["work together", "collaborate", "team up"]):
            return "collaboration"
        
        return "general"

    def _determine_routing_strategy(
        self,
        mention_contexts: List[Dict[str, Any]],
        message: str
    ) -> str:
        """Determine the optimal routing strategy based on mention contexts"""
        
        if not mention_contexts:
            return "no_routing"
        
        valid_mentions = [ctx for ctx in mention_contexts if ctx["valid"]]
        
        if len(valid_mentions) == 1:
            context_type = valid_mentions[0]["context_type"]
            if context_type == "direct_question":
                return "single_targeted"
            else:
                return "single_mention"
        
        elif len(valid_mentions) > 1:
            # Check for comparison requests
            if any(ctx["context_type"] == "comparison_request" for ctx in valid_mentions):
                return "comparison_routing"
            
            # Check for debate requests
            if any(ctx["context_type"] == "debate_request" for ctx in valid_mentions):
                return "debate_routing"
            
            # Check for collaboration requests
            if any(ctx["context_type"] == "collaboration_request" for ctx in valid_mentions):
                return "collaborative_routing"
            
            # Default to parallel processing
            return "parallel_routing"
        
        return "fallback_routing"

    def _suggest_collaboration_mode(
        self,
        mention_contexts: List[Dict[str, Any]],
        message_intent: str
    ) -> str:
        """Suggest the best collaboration mode based on context"""
        
        if not mention_contexts or len(mention_contexts) < 2:
            return "single_agent"
        
        # Intent-based suggestions
        if message_intent == "debate":
            return "debate_mode"
        elif message_intent == "comparison":
            return "expert_panel"
        elif message_intent == "collaboration":
            return "parallel_processing"
        
        # Context-based suggestions
        context_types = [ctx.get("context_type", "general") for ctx in mention_contexts if ctx.get("valid")]
        
        if "debate_request" in context_types:
            return "debate_mode"
        elif "comparison_request" in context_types:
            return "expert_panel"
        elif len(set(context_types)) > 1:  # Mixed context types
            return "parallel_processing"
        
        return "default_parallel"

    def build_enhanced_routing_context(
        self,
        message: str,
        available_contacts: List[ContactInfo]
    ) -> Dict[str, Any]:
        """Build enhanced routing context with detailed analysis"""
        
        # Get basic mention analysis
        mention_analysis = self.parse_mention_with_context(message, available_contacts)
        
        # Get mentioned contacts with context
        mentioned_contacts = []
        if mention_analysis["has_mentions"]:
            for ctx in mention_analysis["mention_contexts"]:
                if ctx["valid"]:
                    contact = next(
                        (c for c in available_contacts if c["contact_id"] == ctx["contact_id"]),
                        None
                    )
                    if contact:
                        # Enrich contact info with routing context
                        enriched_contact = {
                            **contact,
                            "mention_context": ctx,
                            "routing_priority": ctx["priority"],
                            "expertise_relevance": ctx["expertise_match"]
                        }
                        mentioned_contacts.append(enriched_contact)
        
        # Sort by priority
        mentioned_contacts.sort(key=lambda x: x["routing_priority"], reverse=True)
        
        return {
            **mention_analysis,
            "mentioned_contacts": mentioned_contacts,
            "routing_metadata": {
                "total_mentions": len(mention_analysis.get("mentions", [])),
                "valid_mentions": len([ctx for ctx in mention_analysis.get("mention_contexts", []) if ctx["valid"]]),
                "avg_expertise_match": sum(ctx["expertise_match"] for ctx in mention_analysis.get("mention_contexts", []) if ctx["valid"]) / max(len([ctx for ctx in mention_analysis.get("mention_contexts", []) if ctx["valid"]]), 1),
                "max_priority": max([ctx["priority"] for ctx in mention_analysis.get("mention_contexts", []) if ctx["valid"]], default=0)
            }
        }