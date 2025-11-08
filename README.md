# LLM Quiz Solver API

This Flask API accepts quiz tasks, renders JavaScript pages via Playwright, extracts instructions, and submits answers.

## 🚀 How to run locally

```bash
pip install -r requirements.txt
playwright install chromium
export QUIZ_SECRET="s3cr3t-Quiz-2025-XYZ"
python server.py
