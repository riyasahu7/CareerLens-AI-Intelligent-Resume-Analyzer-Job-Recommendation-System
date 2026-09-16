# Contributing to CareerLens AI

Thank you for your interest in contributing!

## Getting Started

1. Fork the repo and clone it locally
2. Follow the [Quick Start](README.md#-quick-start) to get it running
3. Create a branch: `git checkout -b feature/your-feature`

## Guidelines

- Keep PRs focused — one feature or fix per PR
- Add tests for new backend services
- Follow existing code style (no new linting tools needed)
- Never commit `.env` files or API keys
- Update README if you add a new feature or endpoint

## Reporting Issues

Open a GitHub Issue with:
- What you expected vs what happened
- Steps to reproduce
- Python/Node version and OS

## Pull Request Checklist

- [ ] Tests pass: `pytest tests/ -v`
- [ ] Frontend builds: `npm run build`
- [ ] `.env` not committed
- [ ] Description explains what and why
