# Cyclo Veda Documentation

Welcome to the Cyclo Veda documentation! This directory contains all the documentation for the Cyclo Veda project, including architecture decisions, changelog, and detailed guides.

## Directory Structure

```
documentation/
├── adr/                  # Architecture Decision Records
│   └── 2025-08-18-jwt-authentication.md
├── changelog/            # Project changelog
│   └── CHANGELOG.md
└── docs/                 # Detailed documentation
    ├── api-reference.md  # API endpoint documentation
    ├── architecture.md   # System architecture overview
    ├── authentication.md # Authentication system details
    └── development.md    # Development setup and guidelines
```

## Documentation Guide

### Architecture Decision Records (ADRs)
- Location: `adr/`
- Purpose: Document important architectural decisions and their context
- Naming: `YYYY-MM-DD-short-description.md`

### Changelog
- Location: `changelog/CHANGELOG.md`
- Follows [Keep a Changelog](https://keepachangelog.com/) format
- Updated with each release

### API Documentation
- Location: `docs/api-reference.md`
- Includes all available endpoints
- Request/response examples
- Error codes and formats

### Development Guide
- Location: `docs/development.md`
- Setup instructions
- Testing guidelines
- Code style and standards
- Git workflow

### Authentication System
- Location: `docs/authentication.md`
- Authentication flow
- Security considerations
- Token management

### System Architecture
- Location: `docs/architecture.md`
- High-level system design
- Component interactions
- Data flow
- Security considerations

## Contributing to Documentation

1. Keep documentation up-to-date with code changes
2. Follow the established format and style
3. Use clear, concise language
4. Include examples where helpful
5. Update the changelog for significant changes

## Documentation Standards

- Use Markdown for all documentation
- Include code examples where applicable
- Keep lines under 100 characters
- Use descriptive headers
- Include tables of contents for long documents

## Generating Documentation

### API Documentation
API documentation is automatically generated from code using FastAPI's built-in OpenAPI support.

View the interactive API docs at:
- Development: http://localhost:8000/docs
- Production: https://api.cycloveda.com/docs

### Static Documentation
For generating static documentation from Markdown files, you can use:

```bash
# Using markdown-pdf
markdown-pdf README.md -o documentation.pdf

# Or using pandoc
pandoc README.md -o documentation.pdf
```

## License

All documentation is available under the same license as the project. See the main `LICENSE` file for details.
