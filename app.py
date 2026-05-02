from flask import Flask, render_template
from config import Config
from models import db, Admin
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_DOMAIN"] = None

# Initialize DB
db.init_app(app)

# Enable CORS
CORS(app, supports_credentials=True)


# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None
@login_manager.unauthorized_handler
def unauthorized():
    return {"error": "Unauthorized"}, 401

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# ✅ IMPORT BLUEPRINT
from routes import routes
app.register_blueprint(routes)


# ✅ FRONTEND ROUTE
@app.route("/")
def index():
    return render_template("admin.html")


# RUN APP
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
