# Global Vibe Coding Rules

## 1. Development Principles

- **DRY & KISS:** Don't repeat yourself, keep it simple.
- **File Limit:** Max 500 lines per file. Split into modules if exceeded.
- **Refactoring:** Always look for opportunities to simplify logic before adding new features.

## 2. Language Specifics

### [Go]

- Framework: Standard Library or Gin Gonic (if specified).
- Error Handling: Errors must be wrapped with context: `fmt.Errorf("context: %w", err)`.
- Concurrency: Use channels and waitgroups safely. No naked returns.
- Coding follow document https://go.dev/doc/effective_go

### [Python]

- Style: Follow PEP 8.
- Validation: Use Pydantic models for all API requests/responses.
- Docs: Use Google-style docstrings.

## 3. Security (OWASP Top 10 focus)

- **Injection:** Use ORM or parameterized queries only.
- **Broken Access Control:** Check user ownership before any DB update/delete.
- **Sensitive Data:** Never log passwords or PII (Personally Identifiable Information).

## 4. Workflow

- Before writing code, explain the plan in 3 bullet points.
- After writing code, provide a 'Vibe Check' list for me to verify.
