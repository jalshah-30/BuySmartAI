import threading

from flask import Flask, jsonify, render_template, request

from core.rag_pipeline import run_buy_smart, answer_follow_up
from core.vector_store import load_vector_store, delete_vector_store

app = Flask(__name__)

# One research session at a time (the vector store is a single shared store)
state = {"vector_store": None}
lock = threading.Lock()

# run_buy_smart returns these messages (and builds no vector store) when it finds nothing
NO_DATA_PREFIXES = ("No products found", "No usable product data")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/research")
def research():
    query = (request.get_json(silent=True) or {}).get("query", "").strip()
    if not query:
        return jsonify(error="Tell me what you want to buy."), 400

    with lock:
        state["vector_store"] = None
        try:
            answer = run_buy_smart(query)
            if answer.startswith(NO_DATA_PREFIXES):
                return jsonify(answer=answer, followups=False)
            state["vector_store"] = load_vector_store()
        except Exception:
            app.logger.exception("Research failed")
            return jsonify(error="Research failed. Check your API keys and try again."), 500

    return jsonify(answer=answer, followups=True)


@app.post("/api/chat")
def chat():
    message = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not message:
        return jsonify(error="Type a question first."), 400
    if state["vector_store"] is None:
        return jsonify(error="No active research. Start a new search first."), 409

    with lock:
        try:
            return jsonify(answer=answer_follow_up(message, state["vector_store"]))
        except Exception:
            app.logger.exception("Follow-up failed")
            return jsonify(error="Couldn’t answer that. Please try again."), 500


@app.post("/api/end")
def end():
    with lock:
        state["vector_store"] = None
        try:
            delete_vector_store()
        except Exception:
            app.logger.exception("Could not delete vector store")
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)  # reloader off: avoids running init twice