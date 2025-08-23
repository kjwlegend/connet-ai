"""
Tool Registry

Registry for managing available tools, their configurations, and validation.
Provides centralized management of all tools available to LangGraph workflows.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ToolType(str, Enum):
    """Available tool types"""
    
    # Built-in system tools
    BUILTIN_CODE = "builtin_code"
    BUILTIN_SEARCH = "builtin_search"
    BUILTIN_FILE = "builtin_file"
    BUILTIN_WEB = "builtin_web"
    BUILTIN_DATABASE = "builtin_database"
    
    # External API tools
    EXTERNAL_API = "external_api"
    EXTERNAL_SERVICE = "external_service"
    
    # Custom user tools
    CUSTOM_FUNCTION = "custom_function"
    CUSTOM_SCRIPT = "custom_script"
    
    # AI/ML tools
    AI_MODEL = "ai_model"
    AI_AGENT = "ai_agent"


class ParameterType(str, Enum):
    """Parameter types for tool validation"""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    ANY = "any"


@dataclass
class ParameterDefinition:
    """Definition of a tool parameter"""
    
    name: str
    param_type: ParameterType
    description: str
    required: bool = True
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    
    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate parameter value"""
        
        # Check required
        if self.required and value is None:
            return False, f"Parameter '{self.name}' is required"
        
        # Use default if not provided
        if value is None:
            value = self.default_value
        
        # Type validation
        if value is not None:
            if not self._validate_type(value):
                return False, f"Parameter '{self.name}' must be of type {self.param_type}"
            
            # Additional validation rules
            if not self._validate_rules(value):
                return False, f"Parameter '{self.name}' failed validation rules"
        
        return True, None
    
    def _validate_type(self, value: Any) -> bool:
        """Validate parameter type"""
        
        if self.param_type == ParameterType.ANY:
            return True
        elif self.param_type == ParameterType.STRING:
            return isinstance(value, str)
        elif self.param_type == ParameterType.INTEGER:
            return isinstance(value, int)
        elif self.param_type == ParameterType.FLOAT:
            return isinstance(value, (int, float))
        elif self.param_type == ParameterType.BOOLEAN:
            return isinstance(value, bool)
        elif self.param_type == ParameterType.ARRAY:
            return isinstance(value, list)
        elif self.param_type == ParameterType.OBJECT:
            return isinstance(value, dict)
        
        return False
    
    def _validate_rules(self, value: Any) -> bool:
        """Validate against additional rules"""
        
        # String length validation
        if self.param_type == ParameterType.STRING and isinstance(value, str):
            if "min_length" in self.validation_rules:
                if len(value) < self.validation_rules["min_length"]:
                    return False
            if "max_length" in self.validation_rules:
                if len(value) > self.validation_rules["max_length"]:
                    return False
        
        # Numeric range validation
        if self.param_type in [ParameterType.INTEGER, ParameterType.FLOAT]:
            if "min_value" in self.validation_rules:
                if value < self.validation_rules["min_value"]:
                    return False
            if "max_value" in self.validation_rules:
                if value > self.validation_rules["max_value"]:
                    return False
        
        # Array validation
        if self.param_type == ParameterType.ARRAY and isinstance(value, list):
            if "min_items" in self.validation_rules:
                if len(value) < self.validation_rules["min_items"]:
                    return False
            if "max_items" in self.validation_rules:
                if len(value) > self.validation_rules["max_items"]:
                    return False
        
        return True


@dataclass
class ToolDefinition:
    """Definition of a tool"""
    
    name: str
    tool_type: ToolType
    description: str
    version: str
    handler: Callable
    parameters: List[ParameterDefinition]
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Execution settings
    timeout_seconds: int = 30
    max_retries: int = 0
    requires_context: bool = False
    
    # Permissions and access
    requires_permission: Optional[str] = None
    allowed_users: Optional[List[str]] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    documentation_url: Optional[str] = None
    
    def get_parameter(self, name: str) -> Optional[ParameterDefinition]:
        """Get parameter definition by name"""
        return next((p for p in self.parameters if p.name == name), None)
    
    def get_required_parameters(self) -> List[ParameterDefinition]:
        """Get all required parameters"""
        return [p for p in self.parameters if p.required]
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """Get JSON schema for parameters"""
        
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in self.parameters:
            schema["properties"][param.name] = {
                "type": param.param_type.value,
                "description": param.description
            }
            
            if param.default_value is not None:
                schema["properties"][param.name]["default"] = param.default_value
            
            if param.required:
                schema["required"].append(param.name)
            
            # Add validation rules to schema
            if param.validation_rules:
                schema["properties"][param.name].update(param.validation_rules)
        
        return schema


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.tool_types: Dict[ToolType, List[str]] = {}
        self._initialize_builtin_tools()
    
    def _initialize_builtin_tools(self):
        """Initialize built-in tools"""
        
        # Code execution tools
        self.register_tool(ToolDefinition(
            name="execute_python",
            tool_type=ToolType.BUILTIN_CODE,
            description="Execute Python code safely",
            version="1.0.0",
            handler=self._execute_python_handler,
            parameters=[
                ParameterDefinition(
                    name="code",
                    param_type=ParameterType.STRING,
                    description="Python code to execute",
                    validation_rules={"max_length": 10000}
                ),
                ParameterDefinition(
                    name="timeout",
                    param_type=ParameterType.INTEGER,
                    description="Execution timeout in seconds",
                    required=False,
                    default_value=10,
                    validation_rules={"min_value": 1, "max_value": 60}
                )
            ],
            timeout_seconds=15,
            tags=["code", "python", "execution"]
        ))
        
        # File system tools
        self.register_tool(ToolDefinition(
            name="read_file",
            tool_type=ToolType.BUILTIN_FILE,
            description="Read contents of a file",
            version="1.0.0",
            handler=self._read_file_handler,
            parameters=[
                ParameterDefinition(
                    name="file_path",
                    param_type=ParameterType.STRING,
                    description="Path to file to read",
                    validation_rules={"max_length": 1000}
                ),
                ParameterDefinition(
                    name="encoding",
                    param_type=ParameterType.STRING,
                    description="File encoding",
                    required=False,
                    default_value="utf-8"
                )
            ],
            tags=["file", "io", "read"]
        ))
        
        self.register_tool(ToolDefinition(
            name="write_file",
            tool_type=ToolType.BUILTIN_FILE,
            description="Write content to a file",
            version="1.0.0",
            handler=self._write_file_handler,
            parameters=[
                ParameterDefinition(
                    name="file_path",
                    param_type=ParameterType.STRING,
                    description="Path to file to write",
                    validation_rules={"max_length": 1000}
                ),
                ParameterDefinition(
                    name="content",
                    param_type=ParameterType.STRING,
                    description="Content to write to file"
                ),
                ParameterDefinition(
                    name="encoding",
                    param_type=ParameterType.STRING,
                    description="File encoding",
                    required=False,
                    default_value="utf-8"
                )
            ],
            tags=["file", "io", "write"]
        ))
        
        # Search tools
        self.register_tool(ToolDefinition(
            name="search_web",
            tool_type=ToolType.BUILTIN_SEARCH,
            description="Search the web for information",
            version="1.0.0",
            handler=self._search_web_handler,
            parameters=[
                ParameterDefinition(
                    name="query",
                    param_type=ParameterType.STRING,
                    description="Search query",
                    validation_rules={"max_length": 500}
                ),
                ParameterDefinition(
                    name="max_results",
                    param_type=ParameterType.INTEGER,
                    description="Maximum number of results",
                    required=False,
                    default_value=5,
                    validation_rules={"min_value": 1, "max_value": 20}
                )
            ],
            timeout_seconds=10,
            tags=["search", "web", "information"]
        ))
    
    def register_tool(self, tool_def: ToolDefinition) -> None:
        """Register a new tool"""
        
        if tool_def.name in self.tools:
            logger.warning(f"Tool {tool_def.name} already registered, overriding")
        
        self.tools[tool_def.name] = tool_def
        
        # Index by tool type
        if tool_def.tool_type not in self.tool_types:
            self.tool_types[tool_def.tool_type] = []
        
        if tool_def.name not in self.tool_types[tool_def.tool_type]:
            self.tool_types[tool_def.tool_type].append(tool_def.name)
        
        logger.info(f"Registered tool: {tool_def.name} ({tool_def.tool_type})")
    
    def unregister_tool(self, tool_name: str) -> bool:
        """Unregister a tool"""
        
        if tool_name not in self.tools:
            return False
        
        tool_def = self.tools[tool_name]
        del self.tools[tool_name]
        
        # Remove from type index
        if tool_def.tool_type in self.tool_types:
            self.tool_types[tool_def.tool_type].remove(tool_name)
        
        logger.info(f"Unregistered tool: {tool_name}")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get tool definition by name"""
        return self.tools.get(tool_name)
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[ToolDefinition]:
        """Get all tools of a specific type"""
        tool_names = self.tool_types.get(tool_type, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tool names"""
        return list(self.tools.keys())
    
    def search_tools(self, query: str) -> List[ToolDefinition]:
        """Search tools by name, description, or tags"""
        
        query_lower = query.lower()
        matches = []
        
        for tool in self.tools.values():
            # Check name
            if query_lower in tool.name.lower():
                matches.append(tool)
                continue
            
            # Check description
            if query_lower in tool.description.lower():
                matches.append(tool)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in tool.tags):
                matches.append(tool)
                continue
        
        return matches
    
    def validate_tool_parameters(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate parameters for a tool"""
        
        tool = self.get_tool(tool_name)
        if not tool:
            return {"valid": False, "errors": [f"Tool '{tool_name}' not found"]}
        
        errors = []
        validated_params = {}
        
        # Check each parameter
        for param_def in tool.parameters:
            value = parameters.get(param_def.name)
            valid, error = param_def.validate_value(value)
            
            if not valid:
                errors.append(error)
            else:
                # Use default if not provided
                validated_params[param_def.name] = value if value is not None else param_def.default_value
        
        # Check for unexpected parameters
        expected_params = {p.name for p in tool.parameters}
        unexpected_params = set(parameters.keys()) - expected_params
        
        if unexpected_params:
            errors.append(f"Unexpected parameters: {', '.join(unexpected_params)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "validated_parameters": validated_params if len(errors) == 0 else None
        }
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get JSON schema for tool"""
        
        tool = self.get_tool(tool_name)
        if not tool:
            return None
        
        return {
            "name": tool.name,
            "type": tool.tool_type.value,
            "description": tool.description,
            "version": tool.version,
            "parameters": tool.get_parameter_schema(),
            "timeout_seconds": tool.timeout_seconds,
            "max_retries": tool.max_retries,
            "tags": tool.tags
        }
    
    def export_registry(self) -> Dict[str, Any]:
        """Export registry as JSON-serializable dict"""
        
        return {
            "tools": {
                name: {
                    "name": tool.name,
                    "type": tool.tool_type.value,
                    "description": tool.description,
                    "version": tool.version,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.param_type.value,
                            "description": p.description,
                            "required": p.required,
                            "default_value": p.default_value,
                            "validation_rules": p.validation_rules
                        }
                        for p in tool.parameters
                    ],
                    "config": tool.config,
                    "timeout_seconds": tool.timeout_seconds,
                    "max_retries": tool.max_retries,
                    "tags": tool.tags,
                    "author": tool.author
                }
                for name, tool in self.tools.items()
            },
            "tool_types": {
                tool_type.value: tools 
                for tool_type, tools in self.tool_types.items()
            }
        }
    
    # Built-in tool handlers (placeholders - implement based on needs)
    
    def _execute_python_handler(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code (placeholder implementation)"""
        return {
            "success": True,
            "output": f"Executed code: {parameters['code'][:100]}...",
            "execution_time": 0.1
        }
    
    def _read_file_handler(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Read file handler (placeholder implementation)"""
        return {
            "success": True,
            "content": f"Content of {parameters['file_path']}",
            "file_size": 1024
        }
    
    def _write_file_handler(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Write file handler (placeholder implementation)"""
        return {
            "success": True,
            "bytes_written": len(parameters['content']),
            "file_path": parameters['file_path']
        }
    
    def _search_web_handler(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search web handler (placeholder implementation)"""
        return {
            "success": True,
            "results": [
                {
                    "title": f"Result for {parameters['query']}",
                    "url": "https://example.com",
                    "snippet": f"This is a search result for {parameters['query']}"
                }
            ],
            "total_results": 1
        }


# Global registry instance
tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    return tool_registry