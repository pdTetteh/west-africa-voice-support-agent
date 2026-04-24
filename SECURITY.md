# Security Policy

## Project status

West Africa Voice Support Agent is an open-source prototype and research/product demo. It is not yet a hardened production support platform.

## Sensitive data warning

Do not commit or upload:

- API keys
- `.env` files
- real customer data
- real customer audio
- private business documents
- private support conversations
- production databases
- personally identifiable information
- secrets or credentials
- model cache files
- virtual environments

## Local development files

The following should remain local and ignored by Git:

```text
.env
app.db
.venv/
.venv311/
.cache/
*.egg-info/