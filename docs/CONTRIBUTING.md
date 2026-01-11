# Contributing to SECI

Thank you for your interest in contributing to SECI! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submission Guidelines](#submission-guidelines)
- [Review Process](#review-process)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. We pledge to:

- Be respectful and inclusive
- Welcome diverse perspectives
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Public or private harassment
- Publishing others' private information
- Any conduct that could reasonably be considered inappropriate

## How Can I Contribute?

### Reporting Bugs

**Before Submitting:**
- Check existing issues to avoid duplicates
- Verify the bug in the latest version
- Collect relevant information (OS, Python version, logs)

**Bug Report Template:**
```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Run '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.10.5]
- SECI Version: [e.g., 0.1.0]

**Additional Context**
Logs, screenshots, etc.
```

### Suggesting Enhancements

**Before Suggesting:**
- Check if it's already on the roadmap
- Search existing feature requests
- Consider if it fits SECI's vision

**Feature Request Template:**
```markdown
**Problem Statement**
What problem does this solve?

**Proposed Solution**
How would this feature work?

**Alternatives Considered**
What other solutions did you consider?

**Additional Context**
Mockups, examples, etc.
```

### Contributing Code

**Types of Contributions:**

1. **Bug Fixes**
   - Fix reported issues
   - Add tests to prevent regression
   - Update documentation if needed

2. **New Features**
   - Implement roadmap items
   - Add requested features
   - Propose and implement new ideas

3. **Documentation**
   - Improve existing docs
   - Add missing documentation
   - Fix typos and errors
   - Add examples

4. **Tests**
   - Increase test coverage
   - Add integration tests
   - Improve test quality

5. **Performance**
   - Optimize slow code
   - Reduce memory usage
   - Improve scalability

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/ai.git
cd ai

# Add upstream remote
git remote add upstream https://github.com/AkshatNaruka/ai.git
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Install development dependencies
pip install pytest black isort flake8 mypy pre-commit
```

### 3. Install Pre-commit Hooks

```bash
# Set up pre-commit hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

### 4. Create a Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# Or: git checkout -b fix/bug-description
```

## Coding Standards

### Python Style Guide

**Follow PEP 8** with these specifics:

- **Line Length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Group and sort (use isort)

### Code Formatting

**Use Black for formatting:**
```bash
# Format code
black seci/

# Check without modifying
black --check seci/
```

**Use isort for imports:**
```bash
# Sort imports
isort seci/

# Check without modifying
isort --check-only seci/
```

### Type Hints

**Always use type hints:**
```python
from typing import List, Dict, Optional

def process_data(
    input_data: List[str],
    config: Dict[str, any],
    verbose: bool = False
) -> Optional[str]:
    """
    Process input data according to config
    
    Args:
        input_data: List of strings to process
        config: Configuration dictionary
        verbose: Enable verbose output
    
    Returns:
        Processed result or None if error
    """
    pass
```

### Documentation

**Docstring Format:**
```python
def complex_function(param1: int, param2: str) -> List[str]:
    """
    One-line summary
    
    Detailed description of what the function does. Can span
    multiple lines to explain behavior, algorithms, or important
    implementation details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is negative
        TypeError: When param2 is not a string
    
    Example:
        >>> result = complex_function(5, "test")
        >>> print(result)
        ['output1', 'output2']
    """
    pass
```

### Testing

**Write tests for all new code:**

```python
import pytest
from seci.core.model import CompactTransformer

class TestCompactTransformer:
    @pytest.fixture
    def model(self):
        return CompactTransformer(
            vocab_size=1000,
            hidden_size=128,
            num_layers=2
        )
    
    def test_forward_pass(self, model):
        """Test basic forward pass"""
        input_ids = torch.randint(0, 1000, (2, 10))
        outputs = model(input_ids)
        
        assert 'logits' in outputs
        assert outputs['logits'].shape == (2, 10, 1000)
    
    def test_parameter_count(self, model):
        """Test parameter count is reasonable"""
        params = sum(p.numel() for p in model.parameters())
        assert params < 10_000_000  # Less than 10M params
```

**Run tests:**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_model.py

# Run with coverage
pytest --cov=seci --cov-report=html

# Run and show print statements
pytest -s
```

### Code Review Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] Commit messages are clear
- [ ] Code is well-commented
- [ ] No debugging code left in

## Submission Guidelines

### Commit Messages

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(search): Add Bing search provider

Implement BingSearchProvider to support Bing API for web search.
Includes error handling and rate limiting.

Closes #123
```

```
fix(memory): Fix memory leak in external memory

The memory module was not properly releasing old memories,
causing a gradual memory leak. This fix implements proper
cleanup in the LRU eviction logic.

Fixes #456
```

### Pull Request Process

**1. Update Your Branch**
```bash
# Fetch latest changes
git fetch upstream

# Rebase your branch
git rebase upstream/main
```

**2. Push to Your Fork**
```bash
git push origin feature/your-feature-name
```

**3. Create Pull Request**

Go to GitHub and create a PR with this template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings

## Related Issues
Closes #XXX
```

**4. Respond to Feedback**
- Address all review comments
- Push changes to the same branch
- Request re-review when ready

## Review Process

### What Reviewers Look For

1. **Correctness**: Does it work as intended?
2. **Style**: Follows coding standards?
3. **Tests**: Adequate test coverage?
4. **Documentation**: Is it documented?
5. **Performance**: Any performance issues?
6. **Security**: Any security concerns?
7. **Breaking Changes**: Backward compatible?

### Timeline

- **Initial Review**: Within 2-3 days
- **Follow-up Reviews**: Within 1-2 days
- **Merge**: After approval from 1-2 maintainers

### After Approval

Once approved:
1. Maintainer will merge your PR
2. Your changes will be in the next release
3. You'll be added to contributors list
4. Credit given in release notes

## Recognition

### Contributors

All contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- GitHub contributors page

### Significant Contributions

Major contributions may earn:
- Maintainer status
- Decision-making authority
- Name in credits
- Conference speaking opportunities

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Discord**: Real-time chat (coming soon)
- **Monthly Calls**: Video meetings (coming soon)

### Getting Help

**Stuck? Ask for help!**

- Comment on your PR
- Ask in GitHub Discussions
- Reach out to maintainers
- Join community calls

### Mentorship

**New to open source?**

We offer mentorship for:
- First-time contributors
- Students and researchers
- Underrepresented groups

Contact maintainers to request a mentor.

## Development Tips

### Local Testing

```bash
# Test your changes locally
python jarvis.py --interactive

# Run specific examples
python examples/basic_training.py

# Check for common issues
black --check seci/
isort --check seci/
flake8 seci/
mypy seci/
```

### Debugging

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pdb for debugging
import pdb; pdb.set_trace()

# Or ipdb (better interface)
import ipdb; ipdb.set_trace()
```

### Performance Profiling

```python
# Profile your code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(10)  # Top 10 functions
```

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

## Questions?

- Read the [Developer Guide](DEVELOPER_GUIDE.md)
- Check [FAQ](FAQ.md)
- Ask in GitHub Discussions
- Email maintainers

---

**Thank you for contributing to SECI! Together we're making AI accessible to everyone! 🎉**
