from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from marshmallow import ValidationError

from app.extensions import db, bcrypt, limiter
from .models import User
from .schemas import RegisterSchema, LoginSchema, UserResponseSchema
from app.common.decorators import admin_required

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
user_response_schema = UserResponseSchema()
users_response_schema = UserResponseSchema(many=True)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per hour")
def register():
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422
    
    # BACKEND VALIDATION
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validate username
    if not username or len(username) < 3 or len(username) > 50:
        return jsonify({"error": "Username must be 3-50 characters"}), 400
    
    # Validate email
    if not email or '@' not in email or '.' not in email or len(email) > 100:
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate password
    if not password or len(password) < 6 or len(password) > 128:
        return jsonify({"error": "Password must be 6-128 characters"}), 400
    
    # Update data with cleaned values
    data['username'] = username
    data['email'] = email.lower()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409

    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        email=data["email"],
        username=data["username"],
        password_hash=password_hash,
        role="user",
    )
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "message": "User registered successfully",
        "access_token": access_token,
        "user": user_response_schema.dump(user),
    }), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("50 per minute")
def login():
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user_response_schema.dump(user),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify({"user": user_response_schema.dump(user)}), 200


@auth_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    users = User.query.all()
    return jsonify({"users": users_response_schema.dump(users)}), 200


@auth_bp.route("/users/<int:user_id>/deactivate", methods=["PATCH"])
@admin_required
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    return jsonify({"message": f"User {user.username} deactivated"}), 200


@auth_bp.route("/users/<int:user_id>/promote", methods=["PATCH"])
@admin_required
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    user.role = "admin"
    db.session.commit()
    return jsonify({"message": f"User {user.username} promoted to admin"}), 200
