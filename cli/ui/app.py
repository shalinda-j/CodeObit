"""
Flask application for CodeObit web UI
"""

from flask import Flask, render_template, request, jsonify


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Simple in-memory command history
    command_history: list[dict] = []

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/run")
    def api_run():
        payload = request.get_json(silent=True) or {}
        command = payload.get("command")
        args = payload.get("args", [])
        if not command:
            return jsonify({"ok": False, "error": "command is required"}), 400

        # For now, echo back; future: route to CLI command handlers
        record = {"command": command, "args": args}
        command_history.append(record)
        return jsonify({"ok": True, **record})

    @app.get("/api/history")
    def api_history():
        return jsonify({"ok": True, "history": command_history[-50:]})

    return app
