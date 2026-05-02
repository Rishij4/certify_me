from flask import Blueprint, request, jsonify
from models import db, Admin, Opportunity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

routes = Blueprint("routes", __name__)

# ================= AUTH =================

@routes.route("/api/signup", methods=["POST"])
def signup():
    data = request.json

    if Admin.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email exists"}), 400

    user = Admin(
        full_name=data["full_name"],
        email=data["email"],
        password_hash=generate_password_hash(data["password"])
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Signup success"})


@routes.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = Admin.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user, remember=True)
    return jsonify({"message": "Login success"})


@routes.route("/api/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})


@routes.route("/api/forgot-password", methods=["POST"])
def forgot():
    data = request.json
    email = data["email"]

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    user = Admin.query.filter_by(email=email).first()

    if user:
        token = serializer.dumps(email, salt="reset")
        print("Reset link:", f"http://localhost:5000/reset/{token}")

    return jsonify({"message": "If email exists, reset link sent"})


# ================= OPPORTUNITIES =================

@routes.route("/api/opportunities", methods=["GET"])
@login_required
def get_ops():
    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()

    return jsonify([
        {
            "id": op.id,
            "name": op.name,
            "duration": op.duration,
            "start_date": op.start_date,
            "description": op.description,
            "skills": op.skills.split(","),
            "category": op.category,
            "future_opportunities": op.future_opportunities,
            "max_applicants": op.max_applicants
        }
        for op in ops
    ])


@routes.route("/api/opportunities", methods=["POST"])
@login_required
def add_op():
    data = request.json

    op = Opportunity(
        name=data["name"],
        duration=data["duration"],
        start_date=data["start_date"],
        description=data["description"],
        skills=",".join(data["skills"]),
        category=data["category"],
        future_opportunities=data["future_opportunities"],
        max_applicants=data.get("max_applicants"),
        admin_id=current_user.id
    )

    db.session.add(op)
    db.session.commit()

    return jsonify({"message": "Created"})


@routes.route("/api/opportunities/<int:id>", methods=["PUT"])
@login_required
def edit_op(id):
    op = Opportunity.query.get_or_404(id)

    if op.admin_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json

    op.name = data["name"]
    op.duration = data["duration"]
    op.start_date = data["start_date"]
    op.description = data["description"]
    op.skills = ",".join(data["skills"])
    op.category = data["category"]
    op.future_opportunities = data["future_opportunities"]
    op.max_applicants = data.get("max_applicants")

    db.session.commit()

    return jsonify({"message": "Updated"})


@routes.route("/api/opportunities/<int:id>", methods=["DELETE"])
@login_required
def delete_op(id):
    op = Opportunity.query.get_or_404(id)

    if op.admin_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(op)
    db.session.commit()

    return jsonify({"message": "Deleted"})