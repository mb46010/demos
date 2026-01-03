"""Unit tests for PromptLoader."""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from demo.prompt_loader import PromptLoader, MockPromptLoader


class TestPromptLoader:
    """Tests for PromptLoader class."""
    
    @pytest.fixture
    def temp_prompts_dir(self):
        """Create a temporary directory with test prompts."""
        with TemporaryDirectory() as tmpdir:
            prompts_dir = Path(tmpdir) / "prompts"
            prompts_dir.mkdir()
            
            # Create test prompt files
            (prompts_dir / "simple.json").write_text(json.dumps({
                "prompt": "Simple prompt"
            }))
            
            (prompts_dir / "with_list.json").write_text(json.dumps({
                "prompt": ["Line 1", "Line 2", "Line 3"]
            }))
            
            (prompts_dir / "with_template.json").write_text(json.dumps({
                "prompt": "Hello {name}, your score is {score}"
            }))
            
            (prompts_dir / "custom_field.json").write_text(json.dumps({
                "custom": "Custom field prompt"
            }))
            
            (prompts_dir / "invalid.json").write_text("not valid json{")
            
            yield prompts_dir
    
    def test_load_simple_prompt(self, temp_prompts_dir):
        """Test loading a simple string prompt."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        prompt = loader.load("simple")
        
        assert prompt == "Simple prompt"
        assert isinstance(prompt, str)
    
    def test_load_list_prompt(self, temp_prompts_dir):
        """Test loading a prompt that's a list."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        prompt = loader.load("with_list")
        
        assert prompt == ["Line 1", "Line 2", "Line 3"]
        assert isinstance(prompt, list)
    
    def test_load_with_custom_field(self, temp_prompts_dir):
        """Test loading with a custom field name."""
        loader = PromptLoader(
            prompts_dir=temp_prompts_dir,
            field_name="custom"
        )
        prompt = loader.load("custom_field")
        
        assert prompt == "Custom field prompt"
    
    def test_load_missing_file(self, temp_prompts_dir):
        """Test loading a non-existent prompt raises error."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load("nonexistent")
        
        assert "not found" in str(exc_info.value).lower()
        assert "Available prompts:" in str(exc_info.value)
    
    def test_load_missing_with_allow_missing(self, temp_prompts_dir):
        """Test loading missing prompt with allow_missing=True."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        prompt = loader.load("nonexistent", allow_missing=True)
        
        assert prompt is None
    
    def test_load_invalid_json(self, temp_prompts_dir):
        """Test loading invalid JSON raises error."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        with pytest.raises(ValueError) as exc_info:
            loader.load("invalid")
        
        assert "Invalid JSON" in str(exc_info.value)
    
    def test_load_missing_field(self, temp_prompts_dir):
        """Test loading prompt without required field."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        with pytest.raises(ValueError) as exc_info:
            loader.load("custom_field")  # Expects 'prompt' field
        
        assert "not found" in str(exc_info.value)
        assert "Available fields:" in str(exc_info.value)
    
    def test_caching_enabled(self, temp_prompts_dir):
        """Test that caching works when enabled."""
        loader = PromptLoader(
            prompts_dir=temp_prompts_dir,
            enable_cache=True
        )
        
        # First load
        prompt1 = loader.load("simple")
        
        # Delete the file
        (temp_prompts_dir / "simple.json").unlink()
        
        # Second load should still work (cached)
        prompt2 = loader.load("simple")
        
        assert prompt1 == prompt2 == "Simple prompt"
    
    def test_caching_disabled(self, temp_prompts_dir):
        """Test that caching can be disabled."""
        loader = PromptLoader(
            prompts_dir=temp_prompts_dir,
            enable_cache=False
        )
        
        # First load
        prompt1 = loader.load("simple")
        
        # Delete the file
        (temp_prompts_dir / "simple.json").unlink()
        
        # Second load should fail (no cache)
        with pytest.raises(FileNotFoundError):
            loader.load("simple")
    
    def test_reload_single_prompt(self, temp_prompts_dir):
        """Test reloading a single prompt bypasses cache."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        # Load and cache
        prompt1 = loader.load("simple")
        assert prompt1 == "Simple prompt"
        
        # Modify file
        (temp_prompts_dir / "simple.json").write_text(json.dumps({
            "prompt": "Modified prompt"
        }))
        
        # Should still get cached version
        prompt2 = loader.load("simple")
        assert prompt2 == "Simple prompt"
        
        # Reload
        loader.reload("simple")
        
        # Should get new version
        prompt3 = loader.load("simple")
        assert prompt3 == "Modified prompt"
    
    def test_reload_all(self, temp_prompts_dir):
        """Test reloading all prompts clears entire cache."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        # Load multiple prompts
        loader.load("simple")
        loader.load("with_list")
        
        assert len(loader._cache) == 2
        
        # Clear all cache
        loader.reload()
        
        assert len(loader._cache) == 0
    
    def test_get_formatted_string(self, temp_prompts_dir):
        """Test formatting a string prompt."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        formatted = loader.get_formatted(
            "with_template",
            name="Alice",
            score=95
        )
        
        assert formatted == "Hello Alice, your score is 95"
    
    def test_get_formatted_list(self, temp_prompts_dir):
        """Test formatting a list prompt joins it."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        formatted = loader.get_formatted("with_list")
        
        assert formatted == "Line 1\nLine 2\nLine 3"
    
    def test_get_formatted_custom_join(self, temp_prompts_dir):
        """Test formatting with custom join string."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        formatted = loader.get_formatted(
            "with_list",
            join_with=" | "
        )
        
        assert formatted == "Line 1 | Line 2 | Line 3"
    
    def test_get_formatted_missing_variable(self, temp_prompts_dir):
        """Test formatting with missing variable raises error."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        
        with pytest.raises(ValueError) as exc_info:
            loader.get_formatted(
                "with_template",
                name="Alice"
                # Missing 'score'
            )
        
        assert "Missing required variable" in str(exc_info.value)
    
    def test_list_available(self, temp_prompts_dir):
        """Test listing available prompts."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        available = loader.list_available()
        
        assert "simple" in available
        assert "with_list" in available
        assert "with_template" in available
        assert len(available) >= 3
    
    def test_load_all(self, temp_prompts_dir):
        """Test loading all prompts at once."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        prompts = loader.load_all()
        
        assert "simple" in prompts
        assert "with_list" in prompts
        assert prompts["simple"] == "Simple prompt"
        assert prompts["with_list"] == ["Line 1", "Line 2", "Line 3"]
    
    def test_validate_all(self, temp_prompts_dir):
        """Test validating all prompts."""
        loader = PromptLoader(prompts_dir=temp_prompts_dir)
        results = loader.validate_all()
        
        # Valid prompts should have None
        assert results["simple"] is None
        assert results["with_list"] is None
        
        # Invalid prompts should have error messages
        assert results["invalid"] is not None
        assert "Invalid JSON" in results["invalid"]
    
    def test_validation_empty_prompt(self, temp_prompts_dir):
        """Test validation catches empty prompts."""
        (temp_prompts_dir / "empty.json").write_text(json.dumps({
            "prompt": ""
        }))
        
        loader = PromptLoader(
            prompts_dir=temp_prompts_dir,
            validate_on_load=True
        )
        
        with pytest.raises(ValueError) as exc_info:
            loader.load("empty")
        
        assert "empty" in str(exc_info.value).lower()
    
    def test_validation_disabled(self, temp_prompts_dir):
        """Test that validation can be disabled."""
        (temp_prompts_dir / "empty.json").write_text(json.dumps({
            "prompt": ""
        }))
        
        loader = PromptLoader(
            prompts_dir=temp_prompts_dir,
            validate_on_load=False
        )
        
        # Should not raise even though empty
        prompt = loader.load("empty")
        assert prompt == ""


class TestMockPromptLoader:
    """Tests for MockPromptLoader."""
    
    def test_mock_load_simple(self):
        """Test loading from mock prompts."""
        mock = MockPromptLoader(prompts={
            "test": "Test prompt"
        })
        
        prompt = mock.load("test")
        assert prompt == "Test prompt"
    
    def test_mock_load_missing(self):
        """Test loading missing mock prompt."""
        mock = MockPromptLoader(prompts={"test": "Test prompt"})
        
        with pytest.raises(FileNotFoundError) as exc_info:
            mock.load("missing")
        
        assert "Mock prompt" in str(exc_info.value)
        assert "Available:" in str(exc_info.value)
    
    def test_mock_list_available(self):
        """Test listing available mock prompts."""
        mock = MockPromptLoader(prompts={
            "test1": "Prompt 1",
            "test2": "Prompt 2"
        })
        
        available = mock.list_available()
        assert set(available) == {"test1", "test2"}
    
    def test_mock_get_formatted(self):
        """Test formatting mock prompts."""
        mock = MockPromptLoader(prompts={
            "template": "Hello {name}"
        })
        
        formatted = mock.get_formatted("template", name="World")
        assert formatted == "Hello World"


class TestPromptLoaderIntegration:
    """Integration tests with actual project structure."""
    
    def test_load_real_prompts(self):
        """Test loading actual prompts from the project."""
        # This would use the real prompts directory
        prompts_dir = Path("src/prompts")
        
        if not prompts_dir.exists():
            pytest.skip("Prompts directory not found")
        
        loader = PromptLoader(prompts_dir=prompts_dir)
        
        # Try to load actual prompts
        try:
            draft_prompt = loader.load("n_draft")
            assert draft_prompt is not None
        except FileNotFoundError:
            pytest.skip("n_draft.json not found")
    
    def test_factory_pattern(self):
        """Test using PromptLoader in factory pattern."""
        from unittest.mock import Mock
        
        # Mock LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(model_dump=lambda: {"draft": "Test"})
        
        # Mock prompt loader
        mock_loader = MockPromptLoader(prompts={
            "n_draft": ["You are a test.", "Input: {manager_input}"]
        })
        
        # Create factory
        def create_node(llm, prompt_loader):
            def node(state):
                prompt = prompt_loader.get_formatted(
                    "n_draft",
                    manager_input=str(state["input"])
                )
                response = llm.invoke(prompt)
                return {"draft": response.model_dump()["draft"]}
            return node
        
        # Test it
        node = create_node(mock_llm, mock_loader)
        result = node({"input": {"test": "data"}})
        
        assert result["draft"] == "Test"
        mock_llm.invoke.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
