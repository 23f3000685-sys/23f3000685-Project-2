import os, re, json, base64, time, requests
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

app = Flask(__name__)
EXPECTED_SECRET = os.environ.get("QUIZ_SECRET", "s3cr3t-Quiz-2025-XYZ")
MAX_TOTAL_SECONDS = int(os.environ.get("MAX_TOTAL_SECONDS", "170"))

def bad_request(msg): return jsonify({"error": msg}), 400
def forbidden(msg): return jsonify({"error": msg}), 403
def ok(data): return jsonify(data), 200

def extract_base64_from_atob(html):
    m = re.search(r"atob\(\s*`([^`]*)`", html, re.DOTALL)
    if not m:
        m = re.search(r"atob\(['\"]([^'\"]+)['\"]\)", html, re.DOTALL)
    return m.group(1) if m else None

def decode_base64_safe(b64):
    pad = len(b64) % 4
    if pad: b64 += "=" * (4 - pad)
    return base64.b64decode(b64).decode("utf-8", "ignore")

def find_submit_endpoint(html):
    m = re.search(r'"(https?://[^"]*submit[^"]*)"', html, re.I)
    if m: return m.group(1)
    m = re.search(r'<form[^>]+action=["\']([^"\']+)["\']', html, re.I)
    if m: return m.group(1)
    return None

@app.route("/api/quiz-webhook", methods=["POST"])
def quiz():
    start = time.time()
    try:
        payload = request.get_json(force=True)
    except Exception:
        return bad_request("Invalid JSON")
    if not payload or not isinstance(payload, dict):
        return bad_request("JSON must be an object")

    email, secret, url = payload.get("email"), payload.get("secret"), payload.get("url")
    if not (email and secret and url):
        return bad_request("Missing required fields")
    if secret != EXPECTED_SECRET:
        return forbidden("Invalid secret")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            html = page.content()

            b64 = extract_base64_from_atob(html)
            parsed = {}
            if b64:
                decoded = decode_base64_safe(b64)
                m = re.search(r"\{.*\}", decoded, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(0))
                else:
                    parsed["decoded"] = decoded
            else:
                parsed["raw"] = page.inner_text("body")[:2000]

            answer = parsed.get("answer") or 0
            submit_url = parsed.get("submit_url") or find_submit_endpoint(html)
            if not submit_url:
                return ok({"status": "no-submit-url", "parsed": parsed})
            if submit_url.startswith("/"):
                from urllib.parse import urljoin
                submit_url = urljoin(url, submit_url)

            payload_out = {"email": email, "secret": secret, "url": url, "answer": answer}
            r = requests.post(submit_url, json=payload_out, timeout=30)
            try:
                result = r.json()
            except Exception:
                result = {"status": r.status_code, "text": r.text}

            browser.close()
            return ok({
                "status": "processed",
                "elapsed": round(time.time() - start, 2),
                "submit_url": submit_url,
                "submit_result": result,
            })
    except Exception as e:
        return ok({"status": "error", "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
