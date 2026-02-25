# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email **info@ideamax.eu** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. You will receive a response within 48 hours
4. A fix will be released as a patch version

## Scope

This library processes images and generates visual output. Security concerns include:

- Path traversal in file export functions
- Denial of service via extremely large images or frame counts
- Dependency vulnerabilities in Pillow, numpy, imageio

## Best Practices for Users

- Validate file paths before passing to `export()` functions
- Set reasonable limits on image dimensions and frame counts
- Keep dependencies updated
