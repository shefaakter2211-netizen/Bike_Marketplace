from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Bike, Wishlist, User

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/browse")
def browse():

    brand = request.args.get("brand")
    location = request.args.get("location")
    condition = request.args.get("condition")

    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    year = request.args.get("year")

    min_cc = request.args.get("min_cc")
    max_cc = request.args.get("max_cc")

    sort = request.args.get("sort")

    query = Bike.query.filter_by(is_approved=True)

    if brand:
        query = query.filter_by(brand=brand)

    if location:
        query = query.filter_by(location=location)

    if condition:
        query = query.filter_by(condition_type=condition)

    if min_price:
        query = query.filter(Bike.price >= float(min_price))

    if max_price:
        query = query.filter(Bike.price <= float(max_price))

    if year:
        query = query.filter_by(manufacturing_year=int(year))

    if min_cc:
        query = query.filter(Bike.cc >= int(min_cc))

    if max_cc:
        query = query.filter(Bike.cc <= int(max_cc))

    if sort == "price_low":
        query = query.order_by(Bike.price.asc())

    elif sort == "price_high":
        query = query.order_by(Bike.price.desc())
    
    elif sort == "newest":
        query = query.order_by(Bike.manufacturing_year.desc())
    
    elif sort == "most_viewed":
        query = query.order_by(Bike.view_count.desc())

    bikes = query.all()

    return render_template(
        "browse.html",
        bikes=bikes,
        brand=brand,
        location=location,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        year=year,
        min_cc=min_cc,
        max_cc=max_cc,
        sort=sort
    )


@main_bp.route("/bike/<int:bike_id>")
def bike_details(bike_id):

    bike = Bike.query.get_or_404(bike_id)

    return render_template("bike_details.html", bike=bike)

@main_bp.route("/compare/add/<int:bike_id>")
def add_to_compare(bike_id):

    bike = Bike.query.get_or_404(bike_id)

    compare_list = session.get("compare_list", [])

    if bike_id not in compare_list:

        if len(compare_list) >= 2:
            flash("You can compare only 2 bikes at a time.", "warning")
            return redirect(url_for("main.browse"))

        compare_list.append(bike_id)
        session["compare_list"] = compare_list

        flash("Bike added to comparison.", "success")

    return redirect(url_for("main.browse"))

@main_bp.route("/compare")
def compare_bikes():

    compare_list = session.get("compare_list", [])

    bikes = Bike.query.filter(Bike.id.in_(compare_list)).all()

    if len(bikes) != 2:
        flash("Please select exactly 2 bikes to compare.", "warning")
        return redirect(url_for("main.browse"))

    return render_template("compare.html", bikes=bikes)

@main_bp.route("/compare/clear")
def clear_compare():

    session.pop("compare_list", None)

    flash("Comparison cleared.", "info")

    return redirect(url_for("main.browse"))

@main_bp.route("/wishlist/add/<int:bike_id>")
@login_required
def add_to_wishlist(bike_id):

    bike = Bike.query.get_or_404(bike_id)

    existing_wishlist = Wishlist.query.filter_by(
        buyer_id=current_user.id,
        bike_id=bike.id
    ).first()

    if existing_wishlist:
        flash("Bike is already in your wishlist.", "info")
        return redirect(url_for("main.browse"))

    wishlist = Wishlist(
        buyer_id=current_user.id,
        bike_id=bike.id
    )

    db.session.add(wishlist)
    db.session.commit()

    flash("Bike added to wishlist.", "success")

    return redirect(url_for("main.browse"))

@main_bp.route("/wishlist")
@login_required
def wishlist():

    wishlist_items = Wishlist.query.filter_by(
        buyer_id=current_user.id
    ).all()

    bikes = []

    for item in wishlist_items:
        bike = Bike.query.get(item.bike_id)

        if bike:
            bikes.append(bike)

    return render_template(
        "wishlist.html",
        bikes=bikes
    )

@main_bp.route("/wishlist/remove/<int:bike_id>")
@login_required
def remove_from_wishlist(bike_id):

    wishlist_item = Wishlist.query.filter_by(
        buyer_id=current_user.id,
        bike_id=bike_id
    ).first()

    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()

        flash("Bike removed from wishlist.", "info")

    return redirect(url_for("main.wishlist"))

@main_bp.route("/admin/users")
@login_required
def admin_users():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.dashboard"))

    users = User.query.all()

    return render_template(
        "admin_users.html",
        users=users
    )

@main_bp.route("/admin/users/<int:user_id>/role", methods=["POST"])
@login_required
def change_user_role(user_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.dashboard"))

    user = User.query.get_or_404(user_id)

    new_role = request.form.get("role")

    if new_role not in ["buyer", "seller", "admin"]:
        flash("Invalid role.", "danger")
        return redirect(url_for("main.admin_users"))

    user.role = new_role
    db.session.commit()

    flash("User role updated successfully.", "success")

    return redirect(url_for("main.admin_users"))

@main_bp.route("/admin/listings")
@login_required
def admin_listings():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.dashboard"))

    bikes = Bike.query.all()

    return render_template(
        "admin_listings.html",
        bikes=bikes
    )

@main_bp.route("/admin/listings/<int:bike_id>/approve", methods=["POST"])
@login_required
def approve_listing(bike_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.dashboard"))

    bike = Bike.query.get_or_404(bike_id)

    bike.is_approved = True
    db.session.commit()

    flash("Bike listing approved successfully.", "success")

    return redirect(url_for("main.admin_listings"))


@main_bp.route("/admin/listings/<int:bike_id>/reject", methods=["POST"])
@login_required
def reject_listing(bike_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.dashboard"))

    bike = Bike.query.get_or_404(bike_id)

    bike.is_approved = False
    db.session.commit()

    flash("Bike listing rejected.", "info")

    return redirect(url_for("main.admin_listings"))

@main_bp.route("/admin/moderation")
@login_required
def moderation():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("auth.dashboard"))

    pending_bikes = Bike.query.filter_by(
        is_approved=False
    ).all()

    return render_template(
        "moderation.html",
        bikes=pending_bikes
    )