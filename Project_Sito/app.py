import os
import json
from urllib import error, request as url_request

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DEFAULT_OPENAI_MODEL = "gpt-5-mini"
DEFAULT_CV_CONTEXT_PATH = os.path.join("private", "francesco_cv.txt")
MAX_CV_CONTEXT_CHARS = 18000


def load_local_env():
    env_path = os.path.join(app.root_path, ".env")

    if not os.path.exists(env_path):
        return

    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key and key not in os.environ:
                os.environ[key] = value


load_local_env()


def load_private_cv_context():
    cv_path = os.environ.get("CV_CONTEXT_PATH", DEFAULT_CV_CONTEXT_PATH).strip()

    if not os.path.isabs(cv_path):
        cv_path = os.path.join(app.root_path, cv_path)

    if not os.path.exists(cv_path):
        return "No private CV context file has been added yet."

    with open(cv_path, encoding="utf-8") as cv_file:
        cv_text = cv_file.read().strip()

    if not cv_text:
        return "The private CV context file exists, but it is empty."

    cv_text = cv_text.replace("Paste Francesco's CV text here.", "", 1).strip()

    if not cv_text:
        return "The private CV context file has not been filled in yet."

    if len(cv_text) > MAX_CV_CONTEXT_CHARS:
        cv_text = cv_text[:MAX_CV_CONTEXT_CHARS]

    return cv_text


FRANCESCO_CONTEXT = """
Francesco Lami is a Mechanical Engineer based in Modena, Italy.
He works at the intersection of industrial automation, robotics, power transmission,
industrial machinery, international business development, and AI-assisted engineering work.

Professional background and market experience:
- Mechanical engineering with technical-commercial experience.
- Automation, robotics, gearboxes, gearmotors, power transmission and industrial machinery.
- International sales strategy, technical consulting, key account management and business development.
- Experience developing relationships across China, India, Southeast Asia, Latin America and Europe.
- Professional history connected with companies and sectors including Dinamic Oil, General Electric Oil & Gas,
  Montanari Engineering Construction, NORD DRIVESYSTEMS, Rossi, SAI Hydraulic Motors and Vivendi.

Current themes Francesco explores:
- AI in industrial automation.
- Human trust in AI-assisted systems.
- Laundry automation and robotics.
- Mechanical systems and process reliability.
- Industrial strategy and solution selling.
- The future role of engineering work.

Contact information visible on the website:
- Email: francesco.lami@gmail.com
- LinkedIn: https://www.linkedin.com/in/francesco-lami-803234b/
- Location: Modena, Italy
- Languages: Italian and English

Private CV context:
{private_cv_context}
"""

PRIVATE_CV_CONTEXT = load_private_cv_context()

CHAT_INSTRUCTIONS = f"""
You are Francesco AI, an assistant on Francesco Lami's personal website.
Answer as if you are helping a visitor understand Francesco's professional profile, work, interests and contact options.

Voice and behavior:
- Use the same language as the visitor when possible.
- You may speak in first person when it is natural, but do not pretend to be the human Francesco in private or real-time situations.
- Keep answers concise, warm, professional and technically credible.
- Prefer 3 to 6 short sentences unless the visitor explicitly asks for detail.
- Sound like a mechanical engineer with international technical-commercial experience, not like a generic marketing bot.
- Be grounded only in the website context below.
- Do not invent jobs, certifications, private details, project results, prices, availability, legal claims or confidential information.
- If the visitor asks something outside the available context, say that you do not have that information and suggest contacting Francesco directly.
- For hiring, collaboration or business inquiries, gently point to the email or LinkedIn contact.

Website context:
{FRANCESCO_CONTEXT.format(private_cv_context=PRIVATE_CV_CONTEXT)}
"""


def build_chat_response(user_message):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if not api_key or api_key == "replace-with-your-openai-api-key":
        return (
            "The AI chat is configured, but the server still needs a real OpenAI API key. "
            "Please update Project_Sito/.env and restart Flask."
        ), 503

    payload = {
        "model": os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        "instructions": CHAT_INSTRUCTIONS,
        "input": user_message,
        "max_output_tokens": 700,
    }
    api_request = url_request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with url_request.urlopen(api_request, timeout=30) as api_response:
            data = json.loads(api_response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            details = json.loads(exc.read().decode("utf-8"))
            message = details.get("error", {}).get("message", "OpenAI API request failed.")
        except Exception:
            message = "OpenAI API request failed."

        return friendly_api_error(exc.code, message), exc.code
    except error.URLError as exc:
        return (
            "I could not reach the OpenAI API from this server. "
            f"Network detail: {exc.reason}"
        ), 503

    answer = extract_response_text(data)
    return answer or "I could not generate an answer right now. Please try again later.", 200


def friendly_api_error(status_code, message):
    lower_message = message.lower()

    if status_code == 401:
        return "The AI chat could not authenticate with OpenAI. Please check the server API key."

    if status_code == 429:
        return "The AI chat is temporarily unavailable because the OpenAI account reached a rate or quota limit."

    if "model" in lower_message:
        return "The AI chat model is not available for this API key. Please check OPENAI_MODEL in Project_Sito/.env."

    return "The AI chat is temporarily unavailable. Please try again later."


def extract_response_text(data):
    if isinstance(data.get("output_text"), str):
        return data["output_text"]

    parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if content.get("type") == "output_text" and text:
                parts.append(text)

    return "\n".join(parts).strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please write a question first."}), 400

    if len(message) > 1200:
        return jsonify({"error": "Please keep the question shorter than 1200 characters."}), 400

    try:
        answer, status_code = build_chat_response(message)
    except Exception:
        app.logger.exception("AI chat request failed")
        return jsonify({
            "error": "I could not generate an answer right now. Please try again later."
        }), 500

    if status_code != 200:
        return jsonify({"error": answer}), status_code

    return jsonify({"answer": answer})


@app.route("/blog/automation-ai-mechanical-engineering")
def automation_ai_article():
    return render_template("automation-ai-mechanical-engineering.html")


@app.route("/blog/building-technical-trust-across-markets")
def technical_trust_article():
    return render_template("building-technical-trust-across-markets.html")


@app.route("/blog/from-components-to-solutions")
def components_to_solutions_article():
    return render_template("from-components-to-solutions.html")


if __name__ == "__main__":
    app.run(debug=True)
