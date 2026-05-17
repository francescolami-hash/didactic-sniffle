from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

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
