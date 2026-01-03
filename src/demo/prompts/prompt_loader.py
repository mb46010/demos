"""Prompt loader for managing prompt templates with caching and validation."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class PromptLoader:
    """Loads and manages prompt templates from JSON files.
    
    Features:
    - Caching for performance
    - Validation of prompt structure
    - Clear error messages
    - Support for both single prompts and batch loading
    - Easy to mock for testing
    
    Example:
        >>> loader = PromptLoader(prompts_dir=Path("src/prompts"))
        >>> prompt = loader.load("n_draft")
        >>> prompts = loader.load_all()
    """
    
    def __init__(
        self,
        prompts_dir: Union[str, Path] = Path("src/prompts"),
        field_name: str = "prompt",
        enable_cache: bool = True,
        validate_on_load: bool = True,
    ):
        """Initialize the PromptLoader.
        
        Args:
            prompts_dir: Directory containing prompt JSON files
            field_name: Field name in JSON to extract (default: "prompt")
            enable_cache: Whether to cache loaded prompts
            validate_on_load: Whether to validate prompt structure on load
        """
        self.prompts_dir = Path(prompts_dir)
        self.field_name = field_name
        self.enable_cache = enable_cache
        self.validate_on_load = validate_on_load
        
        # Cache storage
        self._cache: Dict[str, Union[str, List[str]]] = {}
        
        # Verify prompts directory exists
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory does not exist: {self.prompts_dir}")
    
    def load(
        self, 
        prompt_name: str,
        allow_missing: bool = False,
    ) -> Union[str, List[str]]:
        """Load a single prompt by name.
        
        Args:
            prompt_name: Name of the prompt file (without .json extension)
            allow_missing: If True, return None instead of raising error
            
        Returns:
            Prompt template as string or list of strings
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist and allow_missing=False
            ValueError: If prompt field is missing in JSON
        
        Example:
            >>> loader.load("n_draft")
            "You are a performance review assistant..."
        """
        # Check cache first
        if self.enable_cache and prompt_name in self._cache:
            logger.debug(f"Loading prompt '{prompt_name}' from cache")
            return self._cache[prompt_name]
        
        # Build file path
        prompt_path = self._get_prompt_path(prompt_name)
        
        # Check if file exists
        if not prompt_path.exists():
            if allow_missing:
                logger.warning(f"Prompt file not found: {prompt_path}")
                return None
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}\n"
                f"Available prompts: {', '.join(self.list_available())}"
            )
        
        # Load JSON
        try:
            with open(prompt_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {prompt_path}: {e}")
        
        # Extract prompt field
        if self.field_name not in data:
            raise ValueError(
                f"Prompt field '{self.field_name}' not found in {prompt_path}.\n"
                f"Available fields: {', '.join(data.keys())}"
            )
        
        prompt = data[self.field_name]
        
        # Validate if enabled
        if self.validate_on_load:
            self._validate_prompt(prompt, prompt_name)
        
        # Cache result
        if self.enable_cache:
            self._cache[prompt_name] = prompt
        
        logger.debug(f"Loaded prompt '{prompt_name}' from {prompt_path}")
        return prompt
    
    def load_all(self) -> Dict[str, Union[str, List[str]]]:
        """Load all prompts from the prompts directory.
        
        Returns:
            Dictionary mapping prompt names to their templates
            
        Example:
            >>> loader.load_all()
            {'n_draft': '...', 'n_input': '...', 'n_rewriter': '...'}
        """
        prompts = {}
        
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return prompts
        
        for file_path in self.prompts_dir.glob("*.json"):
            prompt_name = file_path.stem
            try:
                prompts[prompt_name] = self.load(prompt_name)
            except Exception as e:
                logger.error(f"Failed to load prompt '{prompt_name}': {e}")
        
        return prompts
    
    def get_formatted(
        self,
        prompt_name: str,
        join_with: str = "\n",
        **kwargs: Any
    ) -> str:
        """Load and format a prompt template.
        
        Args:
            prompt_name: Name of the prompt
            join_with: String to join list prompts (default: newline)
            **kwargs: Variables to format into the template
            
        Returns:
            Formatted prompt string
            
        Example:
            >>> loader.get_formatted(
            ...     "n_draft",
            ...     manager_input='{"rating": "exceeds"}',
            ...     review_template_structure='{"sections": [...]}'
            ... )
            "You are a performance review assistant...\n\nManager input:\n{...}"
        """
        prompt = self.load(prompt_name)
        
        # Join if it's a list
        if isinstance(prompt, list):
            prompt = join_with.join(prompt)
        
        # Format with kwargs if provided
        if kwargs:
            try:
                prompt = prompt.format(**kwargs)
            except KeyError as e:
                raise ValueError(
                    f"Missing required variable in prompt '{prompt_name}': {e}"
                )
        
        return prompt
    
    def reload(self, prompt_name: Optional[str] = None) -> None:
        """Reload prompts, bypassing cache.
        
        Args:
            prompt_name: Specific prompt to reload, or None to clear entire cache
            
        Example:
            >>> loader.reload("n_draft")  # Reload one prompt
            >>> loader.reload()  # Clear all cache
        """
        if prompt_name:
            if prompt_name in self._cache:
                del self._cache[prompt_name]
                logger.info(f"Cleared cache for prompt '{prompt_name}'")
        else:
            self._cache.clear()
            logger.info("Cleared entire prompt cache")
    
    def list_available(self) -> List[str]:
        """List all available prompt names.
        
        Returns:
            List of prompt names (without .json extension)
            
        Example:
            >>> loader.list_available()
            ['n_draft', 'n_fact_extractor', 'n_input', 'n_rewriter']
        """
        if not self.prompts_dir.exists():
            return []
        
        return [f.stem for f in self.prompts_dir.glob("*.json")]
    
    def validate_all(self) -> Dict[str, Optional[str]]:
        """Validate all prompts in the directory.
        
        Returns:
            Dictionary mapping prompt names to error messages (None if valid)
            
        Example:
            >>> loader.validate_all()
            {'n_draft': None, 'n_input': None, 'broken_prompt': 'Missing field...'}
        """
        results = {}
        
        for prompt_name in self.list_available():
            try:
                prompt = self.load(prompt_name)
                self._validate_prompt(prompt, prompt_name)
                results[prompt_name] = None  # No error
            except Exception as e:
                results[prompt_name] = str(e)
        
        return results
    
    def _get_prompt_path(self, prompt_name: str) -> Path:
        """Get the full path for a prompt file.
        
        Args:
            prompt_name: Name without extension or with .json
            
        Returns:
            Full path to the prompt file
        """
        # Remove .json if provided
        if prompt_name.endswith(".json"):
            prompt_name = prompt_name[:-5]
        
        return self.prompts_dir / f"{prompt_name}.json"
    
    def _validate_prompt(
        self,
        prompt: Union[str, List[str]],
        prompt_name: str
    ) -> None:
        """Validate prompt structure.
        
        Args:
            prompt: The prompt content
            prompt_name: Name for error messages
            
        Raises:
            ValueError: If prompt is invalid
        """
        # Check if empty
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' is empty")
        
        # If it's a list, check each item
        if isinstance(prompt, list):
            if not all(isinstance(item, str) for item in prompt):
                raise ValueError(
                    f"Prompt '{prompt_name}' list contains non-string items"
                )
            if any(not item.strip() for item in prompt):
                raise ValueError(
                    f"Prompt '{prompt_name}' list contains empty strings"
                )
        
        # If it's a string, check it's not just whitespace
        elif isinstance(prompt, str):
            if not prompt.strip():
                raise ValueError(f"Prompt '{prompt_name}' is only whitespace")
        else:
            raise ValueError(
                f"Prompt '{prompt_name}' must be string or list, "
                f"got {type(prompt).__name__}"
            )


class MockPromptLoader(PromptLoader):
    """Mock prompt loader for testing.
    
    Example:
        >>> mock = MockPromptLoader(prompts={
        ...     "n_draft": "Mock draft prompt with {variable}",
        ...     "n_input": ["Line 1", "Line 2"]
        ... })
        >>> mock.load("n_draft")
        "Mock draft prompt with {variable}"
    """
    
    def __init__(
        self,
        prompts: Optional[Dict[str, Union[str, List[str]]]] = None,
        field_name: str = "prompt",
    ):
        """Initialize mock loader with predefined prompts.
        
        Args:
            prompts: Dictionary of prompt_name -> prompt_content
            field_name: Field name to maintain compatibility
        """
        # Don't call parent __init__ to avoid file system checks
        self.prompts_dir = Path("/mock/prompts")
        self.field_name = field_name
        self.enable_cache = True
        self.validate_on_load = False
        
        self._cache = prompts or {}
    
    def load(
        self,
        prompt_name: str,
        allow_missing: bool = False,
    ) -> Union[str, List[str]]:
        """Load from mock prompts."""
        if prompt_name not in self._cache:
            if allow_missing:
                return None
            raise FileNotFoundError(
                f"Mock prompt '{prompt_name}' not found. "
                f"Available: {', '.join(self._cache.keys())}"
            )
        
        return self._cache[prompt_name]
    
    def list_available(self) -> List[str]:
        """List mock prompts."""
        return list(self._cache.keys())
