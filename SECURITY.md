# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions of CodeObit CLI:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in CodeObit CLI, please report it responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to: [security@codeobit.dev] (replace with actual email)
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Suggested fix (if available)

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Status Update**: Weekly updates on investigation progress
- **Resolution**: Target fix within 30 days for critical issues, 90 days for others

## Security Considerations

### API Key Management

CodeObit CLI handles multiple AI provider API keys. Security measures include:

#### ✅ Current Protections
- API keys stored in environment variables (recommended)
- Configuration files with restricted permissions
- Keys never logged or displayed in plain text
- Support for `.env` files with proper `.gitignore` entries

#### ⚠️ User Responsibilities
- **Never commit API keys to version control**
- Use environment variables or secure config files
- Regularly rotate API keys
- Use least-privilege API keys when available
- Monitor API usage for unauthorized access

#### 🔒 Best Practices
```bash
# Use environment variables
export OPENAI_API_KEY="your-api-key-here"
export GEMINI_API_KEY="your-api-key-here"

# Or use .env file (ensure it's in .gitignore)
echo "OPENAI_API_KEY=your-api-key-here" >> .env
echo "GEMINI_API_KEY=your-api-key-here" >> .env
```

### File System Security

#### Project Data Protection
- Project files stored in user's home directory (`~/CodeObit/Projects`)
- Proper file permissions applied to project directories
- Sensitive project data in `.codeobit` subdirectories

#### File Operations
- All file operations validate paths to prevent directory traversal
- No execution of arbitrary code from project files
- Safe handling of user-provided file paths and names

### Network Security

#### AI Provider Communications
- All API communications use HTTPS/TLS
- Request/response data handled securely
- No sensitive data cached without encryption

#### Web Integration
- URL validation for web scraping features
- Safe handling of external content
- No automatic execution of downloaded content

### Input Validation

#### Command Injection Prevention
- All user inputs sanitized and validated
- No shell command execution with user-provided data
- Safe handling of file names and paths

#### Data Sanitization
- Project names and descriptions validated
- File content properly escaped when displayed
- Prevention of code injection through project data

## Security Features

### Built-in Protections

1. **API Key Masking**: Keys are masked in logs and output
2. **Path Validation**: File paths validated to prevent traversal attacks
3. **Input Sanitization**: All user inputs are sanitized
4. **Secure Defaults**: Conservative security settings by default
5. **Permission Checks**: Proper file permissions on created directories

### Configuration Security

```json
{
  "security": {
    "mask_api_keys": true,
    "validate_paths": true,
    "sanitize_inputs": true,
    "secure_project_dirs": true
  }
}
```

## Common Security Pitfalls

### ❌ Don't Do This
```bash
# Never commit API keys
git add .env
git commit -m "Added API keys"

# Never expose keys in commands
codeobit --api-key="sk-your-key-here"

# Never use untrusted project files
codeobit load-project /tmp/suspicious-project.json
```

### ✅ Do This Instead
```bash
# Use environment variables
export OPENAI_API_KEY="your-key"

# Use interactive setup
codeobit interactive
> !gpt  # Will prompt for key securely

# Verify project sources
codeobit list-projects
codeobit load-project my-trusted-project
```

## Data Privacy

### Local Data Storage
- All project data stored locally by default
- No telemetry or usage data collected
- User controls all data retention and deletion

### AI Provider Data
- User data sent to AI providers according to their policies
- Review each provider's data handling policies:
  - [OpenAI Privacy Policy](https://openai.com/privacy/)
  - [Google AI Privacy Policy](https://policies.google.com/privacy)
  - [Anthropic Privacy Policy](https://www.anthropic.com/privacy)

### Data Minimization
- Only necessary data sent to AI providers
- Local processing preferred when possible
- User can control what data is shared

## Compliance

### Industry Standards
- Follows OWASP security guidelines
- Implements security by design principles
- Regular security assessments and updates

### Data Protection
- GDPR compliance for EU users
- Right to data portability (export features)
- Right to erasure (delete project features)

## Security Updates

### Automatic Updates
- Security patches released as minor version updates
- Critical vulnerabilities get immediate patch releases
- Users notified of security updates through:
  - GitHub releases
  - CLI update notifications
  - Security mailing list

### Manual Security Checks
```bash
# Check for updates
codeobit --version
codeobit check-updates

# Verify installation integrity
codeobit verify-install
```

## Development Security

### For Contributors

#### Secure Development Practices
- Code reviews required for all changes
- Static analysis security testing (SAST)
- Dependency vulnerability scanning
- No hardcoded secrets in source code

#### Testing Security
```bash
# Run security tests
python -m pytest tests/security/

# Check for vulnerabilities
pip audit
safety check

# Scan dependencies
bandit -r cli/
```

### Dependencies
- Regular dependency updates
- Vulnerability scanning of all dependencies
- Minimal dependency footprint
- Trusted sources only

## Incident Response

### In Case of Security Breach

1. **Immediate Actions**
   - Revoke compromised API keys
   - Update CodeObit CLI to latest version
   - Check project files for unauthorized changes
   - Review recent AI provider usage

2. **Assessment**
   - Determine scope of potential data exposure
   - Check logs for suspicious activity
   - Verify integrity of project data

3. **Recovery**
   - Restore from backups if necessary
   - Generate new API keys
   - Update security configurations

## Contact Information

- **Security Issues**: [security@codeobit.dev]
- **General Support**: [support@codeobit.dev]
- **GitHub Issues**: For non-security bugs only

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Guidelines](https://python.org/dev/security/)
- [AI Security Best Practices](https://ai.gov/ai-security-guidance/)

---

**Last Updated**: January 2025
**Version**: 1.0.0

*This security policy is regularly reviewed and updated. Please check back periodically for the latest security guidelines and best practices.*
