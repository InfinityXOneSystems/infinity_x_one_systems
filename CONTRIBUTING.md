# Contributing to Infinity X One Systems

Thank you for your interest in contributing to Infinity X One Systems! This document provides guidelines and instructions for contributing to our corporate repository.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Documentation Standards](#documentation-standards)
- [Commit Message Guidelines](#commit-message-guidelines)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Search existing issues before creating a new one
- Provide clear, detailed descriptions with examples
- Include relevant labels and assign to appropriate team members

### Suggesting Enhancements

- Open an issue with the "enhancement" label
- Describe the proposed change and its benefits
- Discuss with the team before implementing major changes

### Contributing Code or Documentation

1. **Fork and Clone**: Fork the repository and clone it locally
2. **Create a Branch**: Create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**: Implement your changes following our standards
4. **Test**: Ensure all changes are tested and validated
5. **Commit**: Write clear commit messages following our guidelines
6. **Push**: Push your changes to your fork
7. **Pull Request**: Open a PR against the `main` branch

## Pull Request Process

1. **Description**: Provide a clear description of changes
2. **Link Issues**: Reference related issues using `#issue-number`
3. **Documentation**: Update relevant documentation
4. **Review**: Request review from appropriate team members
5. **CI/CD**: Ensure all automated checks pass
6. **Approval**: Obtain required approvals before merging
7. **Merge**: Squash and merge when approved

### PR Title Format

```
<type>: <short description>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat: add new project template for microservices`
- `docs: update contributing guidelines`
- `fix: correct broken link in README`

## Coding Standards

### General Principles

- **Clarity**: Write clear, readable code
- **Consistency**: Follow existing patterns and conventions
- **Simplicity**: Keep solutions simple and maintainable
- **Documentation**: Document complex logic and decisions

### File Organization

- Keep files focused and single-purpose
- Use descriptive file and folder names
- Maintain consistent directory structure
- Group related files together

### Naming Conventions

- Use clear, descriptive names
- Follow language-specific conventions
- Avoid abbreviations unless widely understood
- Use consistent casing (camelCase, PascalCase, snake_case as appropriate)

## Documentation Standards

### Markdown Files

- Use proper heading hierarchy (# for title, ## for sections)
- Include a table of contents for long documents
- Use code blocks with language specifications
- Keep lines under 100 characters when possible
- Include examples and use cases

### Code Comments

- Explain **why**, not **what**
- Keep comments up-to-date with code changes
- Use consistent comment style
- Document public APIs and interfaces

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Subject

- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize first letter
- No period at the end
- Limit to 50 characters

### Body (optional)

- Provide context and motivation
- Explain what and why, not how
- Wrap at 72 characters

### Footer (optional)

- Reference issues: `Closes #123`
- Note breaking changes: `BREAKING CHANGE: description`

### Examples

```
feat(templates): add Python project template

Add a comprehensive Python project template with best practices
including testing, linting, and CI/CD configuration.

Closes #45
```

```
docs: update contribution guidelines

Clarify the pull request process and add examples for commit
messages to help new contributors.
```

## Review Process

### For Contributors

- Respond to feedback promptly
- Be open to suggestions and improvements
- Keep discussions professional and constructive
- Update your PR based on review comments

### For Reviewers

- Review PRs in a timely manner
- Provide constructive, specific feedback
- Approve when standards are met
- Request changes when necessary

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Reach out to the platform team
- Review existing documentation

Thank you for contributing to Infinity X One Systems!
