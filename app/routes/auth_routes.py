from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("This email is already registered. Please log in.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(name=name, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    role = current_user.role

    if role == "buyer":
        role_color = "primary"
        cards = [
            {"title": "Browse Bikes", "desc": "Search and filter new & secondhand bikes.", "link": "/browse", "action": "Browse Now"},
            {"title": "My Wishlist", "desc": "View bikes you have saved for later.", "link": "/wishlist", "action": "View Wishlist"},
            {"title": "My Inquiries", "desc": "Track messages you have sent to sellers.", "link": "/my-inquiries", "action": "View Inquiries"},
        ]
    elif role == "seller":
        role_color = "success"
        cards = [
            {"title": "My Listings", "desc": "View and manage all your bike listings.", "link": "/my-listings", "action": "View Listings"},
            {"title": "Add New Listing", "desc": "List a new bike, new or secondhand.", "link": "/add-listing", "action": "Add Listing"},
            {"title": "Get Verified", "desc": "Upload NID and papers to become a Trusted Seller.", "link": "/verify-seller", "action": "Apply Now"},
        ]
    else:
        role_color = "dark"
        cards = [
            {"title": "Moderate Listings", "desc": "Approve, edit, or block pending listings.", "link": "/admin/listings", "action": "Review Listings"},
            {"title": "Manage Users", "desc": "Activate or suspend user accounts.", "link": "/admin/users", "action": "Manage Users"},
            {"title": "Analytics", "desc": "View platform-wide stats and trends.", "link": "/admin/analytics", "action": "View Analytics"},
        ]

    return render_template("dashboard.html", role_color=role_color, cards=cards)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
