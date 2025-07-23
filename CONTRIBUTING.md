# 🤝 Contributing to codeobit

Thank you for your interest in contributing to codeobit! This document provides guidelines for contributing to our AI-powered development environment.

## 🎯 How to Contribute

### 🐛 Bug Reports
1. **Check existing issues** before creating a new one
2. **Use the bug report template** and provide:
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Error logs or screenshots

### ✨ Feature Requests
1. **Check if the feature already exists** or is planned
2. **Use the feature request template** and provide:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach
   - Any relevant examples or mockups

### 🔧 Code Contributions

#### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/codeobit-v1.git
cd codeobit-v1

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks (optional)
pre-commit install
```

#### Development Guidelines
1. **Code Style**: Follow PEP 8 and use `black` for formatting
2. **Type Hints**: Add type hints for all functions and methods
3. **Documentation**: Update docstrings and comments
4. **Testing**: Add tests for new features
5. **Commit Messages**: Use conventional commit format

#### Pull Request Process
1. **Create a feature branch**: `git checkout -b feature/your-feature-name`
2. **Make your changes** following the guidelines above
3. **Run tests**: `pytest tests/`
4. **Format code**: `black . && flake8`
5. **Update documentation** if needed
6. **Create pull request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots/examples if applicable

## 🏗️ Project Structure

```
codeobit-v1/
├── cli/                    # Core CLI components
│   ├── ai/                # AI client implementations
│   ├── commands/          # Command handlers
│   ├── utils/             # Utilities and helpers
│   └── web/               # Web search components
├── config/                # Configuration files
├── templates/             # Project templates
├── tests/                 # Test files
├── docs/                  # Documentation
├── main.py               # Entry point
├── gemini                # Quick launcher
└── requirements.txt      # Dependencies
```

## 🎨 Code Style

### Python Code
- Use `black` for code formatting
- Follow PEP 8 naming conventions
- Add type hints using Python 3.11+ syntax
- Write docstrings for all public functions/classes

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(cli): add code generation command
fix(ai): resolve gemini client connection issue
docs(readme): update installation instructions
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cli tests/

# Run specific test file
pytest tests/test_interactive.py
```

### Writing Tests
- Place tests in `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (AI API calls, web requests)

## 📝 Documentation

### Code Documentation
- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful

### User Documentation
- Update README.md for user-facing changes
- Add examples for new features
- Update command reference if needed

## 🐛 Beta Testing

As this is a **public beta**, we especially welcome:

### High Priority
- **Bug reports** with detailed reproduction steps
- **Performance issues** and optimization suggestions
- **User experience feedback** on the interactive interface
- **AI response quality** feedback and improvements

### Medium Priority
- **Feature requests** aligned with the project vision
- **Documentation improvements** and clarifications
- **Cross-platform compatibility** testing

### Low Priority
- **Code refactoring** (unless it fixes bugs or improves performance)
- **Aesthetic changes** to the UI

## 🔒 Security

If you discover a security vulnerability, please:
1. **Do NOT** open a public issue
2. **Email us directly** at security@codeobit.dev
3. **Provide details** about the vulnerability
4. **Allow reasonable time** for us to fix the issue

## 📞 Getting Help

- **Discord**: Join our [Discord server](https://discord.gg/codeobit)
- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Use GitHub Issues for bugs and feature requests
- **Email**: Contact us at developers@codeobit.dev

## 🏷️ Beta Release Notes

### Current Beta Status: v1.0.0-beta

**Stable Features**:
- ✅ Interactive AI conversation
- ✅ Code generation (files, functions, classes)
- ✅ Basic code analysis
- ✅ Project management

**Beta Features** (feedback needed):
- 🧪 Advanced code analysis
- 🧪 Test generation and execution
- 🧪 Multi-language support
- 🧪 Web resource collection

**Known Issues**:
- Large file analysis may be slow
- Some edge cases in code generation
- Limited error recovery in some scenarios

## 🙏 Recognition

Contributors will be:
- **Listed** in our contributors file
- **Mentioned** in release notes
- **Invited** to our contributors channel
- **Considered** for beta tester rewards

---

Thank you for helping make codeobit better! 🚀

**Questions?** Join our [Discord](https://discord.gg/codeobit) or open a discussion!
