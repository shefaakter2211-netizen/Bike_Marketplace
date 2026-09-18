from flask import Blueprint, render_template, request
from app.models import Bike

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