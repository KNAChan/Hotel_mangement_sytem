from flask import Flask,render_template,redirect,request,url_for,session,flash
from AdminClass import Admin
from database import Database
import os
from functools import wraps
from datetime import datetime,date

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key-for-admin-John"
admin = Admin()
DB = Database()

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def index():
    return redirect(url_for("login"))

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        name = request.form["username"]
        password = request.form["password"]

        if admin.login(name,password) :
            session["username"] = name
            return redirect(url_for("dashboard",name=name))
        else:
            return render_template("login.html",error = "Invalid user name or password")

    return render_template("login.html")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash("You must log in first!", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)  # remove username from session
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    name = session.get("username")
    total_checkin = DB.totalCheckin()
    total_room = len(DB.total_rooms())
    available_room = len(DB.get_available_rooms())
    booked_room = DB.get_booked_room()
    single_room,double_room,deluxe_room = DB.room_type()

    if total_room > 0:
        checkin_rate = (total_checkin / total_room) * 100 
        available_rate = (available_room/total_room) * 100 
        booked_rate = (booked_room/total_room) * 100
    else:
        checkin_rate = available_rate = booked_rate = 0

    return render_template(
        "dashboard.html",
        name = name,
        total_checkin = total_checkin,
        total_room = total_room,
        available_room = available_room,
        booked_room = booked_room,
        single_room = single_room,
        double_room = double_room,
        deluxe_room = deluxe_room,
        checkin_rate = checkin_rate,
        available_rate = available_rate,
        booked_rate = booked_rate,
        today_date = datetime.now().strftime("%B %d, %Y")
        )

@app.route('/manage_rooms',methods=['GET','POST'])
@login_required
def manage_rooms():
    if request.method == 'POST':
        room_no = request.form["room_no"]
        room_type = request.form["room_type"]
        price = request.form["price"]
        photo = request.files["photo"]

        photo_name = photo.filename
        photo.save(os.path.join(app.config["UPLOAD_FOLDER"], photo_name))

        DB.add_rooms(room_no, room_type, price, photo_name)
        return redirect(url_for("manage_rooms"))

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    rooms, total = DB.view_rooms_paginated(page, per_page)
    total_pages = (total + per_page - 1) // per_page  # ceiling division

    return render_template('manage_rooms.html',rooms=rooms,page=page,total_pages=total_pages)

@app.route('/edit_room/<int:id>',methods=['GET','POST'])
@login_required
def edit_room(id):
    room = DB.get_room_byid(id)

    if request.method == 'POST':
        DB.update_room(
            id,
            request.form["room_no"],
            request.form["room_type"],
            request.form["price"],
            request.form["status"]
        )
        return redirect(url_for('manage_rooms'))

    return render_template('/edit_rooms.html',room=room)

@app.route('/delete_room_route/<int:id>')
@login_required
def delete_room_route(id):
    DB.delete_room(id)
    return redirect(url_for('manage_rooms'))


@app.route('/manage_booking',methods=['GET','POST'])
@login_required
def manage_booking():
    query = request.args.get("q","").strip()
    field = request.args.get("field","first_name")

    # whitelist fields (VERY IMPORTANT)-> to prevent SQL injection
    allowed_fields = ("first_name","last_name", "phone", "room_no")
    if field not in allowed_fields:
        field = "first_name"

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5

    if query:
        total,rows = DB.search_booking_paginated(field,query,page,per_page)
    else:
        rows,total = DB.view_booking_paginated(page,per_page)

    total_pages = (total + per_page - 1) // per_page  # ceiling division

    if request.method == 'POST':
        mode = request.form.get("mode")
        return redirect(url_for('booking_operations',mode=mode))
    
    return render_template('manage_booking.html',bookingdata=rows,query=query,field=field,page=page,total_pages=total_pages)

def Cal_totalprice(booking):
    today = date.today()
    in_datetime = booking["check_in_date"]
    in_date = datetime.strptime(in_datetime, "%Y-%m-%dT%H:%M").date()
    out_datetime = booking["check_out_date"]
    out_date = datetime.strptime(out_datetime, "%Y-%m-%dT%H:%M").date()
    stays = (out_date - in_date).days
    room = DB.get_room_bynumber(booking["room_no"])
    price_per_room = room["price"] if room else 0 

    return stays,price_per_room

@app.route('/booking_operations/<mode>',methods=['GET','POST'])
@app.route('/booking_operations/<mode>/<int:id>',methods=['GET','POST'])
@login_required
def booking_operations(mode,id=None):
    booking = None
    stays = 0
    price_per_room = 0

    if id:
        booking = DB.get_booking_byid(id)
        current_room = booking["room_no"] if booking else None
        if booking:
            stays, price_per_room = Cal_totalprice(booking)
    else:
        current_room = None

    available_rooms = DB.get_available_rooms(current_room=current_room) #to fill room_no combo box

    if request.method == 'POST':
        #delete mode
        if mode == 'delete' and id:
            # Delete mode: skip validations
            booking = DB.get_booking_byid(id)
            if booking:
                DB.delete_booking(id)
                # Mark the room as available
                DB.status_changed(booking["room_no"], status="Available")
            return redirect(url_for('manage_booking'))

        firstname = request.form.get("firstname","").strip()
        lastname = request.form.get("lastname","").strip()
        phone = request.form.get("phoneNumber","").strip()
        country = request.form.get("country","").strip()
        room_no = request.form.get("room_no")
        check_in_date = request.form.get("check_in_date","").strip()
        check_out_date = request.form.get("Check-Out-Date","").strip()
        status = request.form.get("status","").strip()
        dob = request.form.get("dob","").strip()
        email = request.form.get("email","").strip()
        Noadults = request.form.get("Noadults","").strip()
        Nokids = request.form.get("Nokids","").strip()
        payment_type = request.form.get("payment_type","").strip()
        holder_name = request.form.get("holder_name","").strip()
        card_number = request.form.get("card_number","").strip()
        CVV = request.form.get("CVV","").strip()
        totalprice_input = request.form.get("price","").strip()
        
        errorList = {}

        if not firstname:
            errorList["firstname"] = "First Name can't be space or blank" 
        if not lastname:
            errorList["lastname"] = "Last Name can't be space or blank"   
        if not phone or not phone.startswith("09") or not phone.isdigit() or len(phone)!=11:
            errorList["phone"] = "phone must start with 09 and must include 11digits"   
        if not country:
            errorList["country"] = "country required"
        if not room_no:
            errorList["room_no"] = "choose room number"

        if not dob:
            errorList["dob"] = "Date of birth required"
        else:
            d_date = datetime.strptime(dob,"%Y-%m-%d").date()
            today = date.today()
            age = today.year - d_date.year - ((today.month, today.day) < (d_date.month, d_date.day))

            if d_date > today:
                errorList["dob"] = "Date of birth can't be earlier than today"
            elif age < 18:
                errorList["dob"] = "You must be at least 18 years old"
        if not email:
            errorList["email"] = "email required"
        else:
            if "@gmail.com" not in email:
                errorList["email"] = "invalid email"
        if not Noadults:
            errorList["Noadults"] = "Choose Number of adults"
        if not Nokids:
            errorList["Nokids"] = "Choose Number of kids"
        if not payment_type:
            errorList["payment_type"] = "Choose payment type"
        if not holder_name:
            errorList["holder_name"] = "Enter holder name"
        if not card_number or not card_number.isdigit() or len(card_number) != 16:
            errorList["card_number"] = "Enter card number"      
        if not CVV or not CVV.isdigit() or len(CVV) != 3:
            errorList["CVV"] = "Enter CVV number" 

        validate_check_in = False
        validate_check_out = False

        if mode == "insert":
            validate_check_in = True
            validate_check_out = True
        elif mode == "update":
            if status == "booked":
                validate_check_in = True
                validate_check_out = True
            elif status == "check-in":
                validate_check_in = False
                validate_check_out = True
            elif status == "check-out":
                validate_check_in = False
                validate_check_out = False
        elif mode == "delete":
            validate_check_in = False
            validate_check_out = False  

         # --- Check-in date validation ---
        if validate_check_in:
            if not check_in_date:
                errorList["check_in_date"] = "Check-in date required"
            else:
                check_date = datetime.strptime(check_in_date, "%Y-%m-%dT%H:%M").date()
                today = date.today()
                if check_date < today:
                    errorList["check_in_date"] = "Check-in date cannot be earlier than today"

        # --- Check-out date validation ---
        if validate_check_out:
            if not check_out_date:
                errorList["check_out_date"] = "Check-out date required"
            else:
                checkout_date = datetime.strptime(check_out_date, "%Y-%m-%dT%H:%M").date()
                if validate_check_in and checkout_date <= check_date:
                    errorList["check_out_date"] = "Check-out date must be after check-in date"

        if errorList:
            return render_template(
                "booking_operations.html",
                available_rooms=available_rooms,
                mode=mode,
                booking=booking,
                stays = stays,
                price_per_room = price_per_room,
                errorList=errorList,
                inputData=request.form
                )

        if mode == 'insert':
            DB.add_new_booking(firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice_input,dob,email,Noadults,Nokids,payment_type,holder_name,card_number,CVV)
            DB.status_changed(room_no,status)
        elif mode == 'update' and id:
            stays,price_per_room = Cal_totalprice(booking)
            totalprice = price_per_room * stays
            DB.update_booking(id,firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids,payment_type,holder_name,card_number,CVV)
            if status == 'Check out':
                DB.status_changed(room_no,"Available")
            else:
                DB.status_changed(room_no,status)

        return redirect(url_for('manage_booking'))
    return render_template(
        'booking_operations.html',
        available_rooms=available_rooms,
        mode=mode,
        booking=booking,
        stays = stays,
        price_per_room = price_per_room,
        errorList={},
        inputData={}
        )
    

#get room price dynamically
@app.route('/get_room_price')
@login_required
def get_room_price():
    room_no = request.args.get("room_no")
    if not room_no:
        return {"price": 0}

    room = DB.get_room_bynumber(room_no) 
    if room:
        return {"price": int(room["price"])}
    return {"price": 0}


@app.route('/price-analysis')
@login_required
def price_analysis():
    view = request.args.get("view", "monthly")
    labels, prices = DB.price_Cal(view)

    return {
        "labels": labels,
        "prices": prices
    }



if __name__ == "__main__":
    app.run(debug=True)