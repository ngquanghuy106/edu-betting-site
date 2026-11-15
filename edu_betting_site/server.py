from flask import Flask, render_template, request, redirect, session
from pathlib import Path
import os
from dotenv import load_dotenv

from data import Data, UserData


BASE_DIR = Path(__file__).parent / "frontend"


load_dotenv(Path(__file__).parent / ".env")


class Server:
    def __init__(self):
        self.app = Flask(
            __name__,
            template_folder=BASE_DIR / "templates",
			static_folder=BASE_DIR / "static"
        )

        self.app.secret_key = os.getenv("FLASK_SECRET_KEY")

        if not self.app.secret_key:
            raise RuntimeError("FLASK_SECRET_KEY is missing")

        self.data = Data()

        self.web()

    def web(self):
        @self.app.route("/")
        def index():
            if "user_id" in session:
                return render_template(
                    "index.html",
                    username=session["username"],
                    logged_in=True
                )

            return render_template(
                "index.html",
                logged_in=False
            )
        @self.app.route("/register")
        def register_page():
            return render_template("register.html")

        @self.app.route("/api/register", methods=["POST"])
        def register_user():
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")

            def render_register(error):
                return render_template(
                    "register.html",
                    error=error,
                    username=username
                ), 400

            if password != confirm_password:
                return render_register("Passwords do not match")

            success, result = self.data.register(username, password)

            if not success:
                return render_register(result)

            return redirect("/login")


        @self.app.route("/login")
        def login_page():
            return render_template("login.html")

        @self.app.route("/api/login", methods=["POST"])
        def login_user():
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            success, result = self.data.login(username, password)

            if not success:
                return render_template(
                    "login.html",
                    error=result,
                    username=username
                ), 401

            if not isinstance(result, dict):
                return "Unexpected login result", 500

            user: UserData = result

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/")

        @self.app.route("/logout", methods=["POST"])
        def logout():
            session.clear()
            return redirect("/")

    def run(self):
        self.app.run(
            host="0.0.0.0",
            port=5000,
            debug=True
        )


if __name__ == "__main__":
    server = Server()
    server.run()
