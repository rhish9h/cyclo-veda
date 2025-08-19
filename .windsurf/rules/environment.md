---
trigger: model_decision
description: If the project is written in Python
---

### 🛠️ Coding Environment Rule

- If the project is written in **Python**, always create and activate a virtual environment named `venv` before running **any** server, scripts, or tests.
  - Example:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
- Never run the project against the **global Python environment**.
- Assume the `venv` folder is part of the standard project structure and should be recreated if missing.