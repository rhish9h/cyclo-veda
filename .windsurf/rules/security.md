---
trigger: always_on
---

Security Guidelines (DO NOT LEAK SECRETS)

Never hard-code usernames, passwords, API keys, tokens, or secrets in source code, Dockerfiles, docker-compose.yml, shell commands, or config files.

Always read secrets from .env files and only commit the corresponding .env.example with placeholder values.
Backend: use backend/.env + backend/.env.example
Frontend: use frontend/.env + frontend/.env.example
Root services (used by docker-compose.yml): use ./.env + ./.env.example

When showing examples, use placeholder names (e.g. YOUR_DB_PASSWORD, STRAVA_CLIENT_SECRET) and never real values.

Do not modify .gitignore to include .env or other secret files in git; assume all secret files must stay untracked.

Do not print or log secrets (even in debug logs or examples). Log only non-sensitive identifiers.

If a task seems to require a real credential, stop and ask for an env var name or placeholder, not the actual secret.