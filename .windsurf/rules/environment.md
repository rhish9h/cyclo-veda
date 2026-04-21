---
trigger: model_decision
description: Apply when running local Python scripts or debugging outside Docker. This project runs backend and tests inside Docker — do NOT create a venv for running the server, tests, or migrations.
---

## Runtime Environment

- This project runs **entirely inside Docker**. Do not create or activate a `venv` to run the server, tests, or migrations.
- The correct way to run tests is via Docker Compose (see `docker-compose.test.yml`).
- Only create a `venv` if explicitly running a one-off local Python utility script outside Docker.
- Never run backend code against the global Python environment.