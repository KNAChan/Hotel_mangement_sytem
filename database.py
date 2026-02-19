import sqlite3
from datetime import datetime,timedelta
import random

class Database():
    def __init__(self):
        self.createTable()
        self.createBookingTable()
        #self.inject_test_data()
        #self.delete_allBooking_info()
        #self.delete_Table()

    # Create a new connection for each operation
    def get_conn(self):
        conn = sqlite3.connect("HotelDB.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def createTable(self):
        con = self.get_conn()
        cursor = con.cursor()       
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS Rooms(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_no TEXT UNIQUE,
        room_type TEXT,
        price INTEGER,
        status TEXT,
        photo TEXT,
        services TEXT,
        description TEXT
        )
        """)
        con.commit()
        con.close()

    def add_rooms(self,room_no,room_type,price,photo,services,description):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("INSERT INTO Rooms(room_no,room_type,price,status,photo,services,description) VALUES(?,?,?,?,?,?,?)",
        (room_no,room_type,price,"Available",photo,services,description))
        con.commit()
        con.close()

    def view_rooms_paginated(self,page=1,per_page=5,search_no=None,search_type=None):
        offset = (page - 1)* per_page
        con = self.get_conn()
        cursor = con.cursor()

        query = "SELECT * FROM Rooms WHERE 1=1 "
        count_query = "SELECT COUNT(*) as total FROM Rooms WHERE 1=1 "
        params = []

        if search_no:
            query += "AND room_no LIKE ? " 
            count_query += "AND room_no LIKE ? "
            params.append(f"%{search_no}%")

        if search_type:
            query += "AND room_type LIKE ? "
            count_query += "AND room_type LIKE ?"
            params.append(f"%{search_type}%")
        
        query += "LIMIT ? OFFSET ?"

        cursor.execute(query,params + [per_page,offset])
        rows = cursor.fetchall()
        
        cursor.execute(count_query,params)
        total = cursor.fetchone()["total"]

        con.close()
        return rows,total
    

    def get_room_byid(self,room_id):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Rooms WHERE id = ?",(room_id,))
        row = cursor.fetchone()
        con.close()
        return row

    def get_room_bynumber(self,room_no):
        con = self.get_conn()
        cursor = con.cursor()    
        cursor.execute("SELECT * FROM Rooms WHERE room_no=?",(room_no,))
        row = cursor.fetchone()
        con.close()
        return row

    def update_room(self,room_id,room_no,room_type,price,status,services,photo_name,description):
        con = self.get_conn()
        cursor = con.cursor()       
        cursor.execute("UPDATE Rooms SET room_no=?, room_type=?, price=?, status=?,photo=?,services=?,description=?  WHERE id=?",
        (room_no,room_type,price,status,photo_name,services,description,room_id))
        con.commit()
        con.close() 
    
    def delete_room(self,room_id):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("DELETE FROM Rooms WHERE id = ?",(room_id,))
        con.commit()
        con.close()

    def get_available_rooms(self,current_room=None):
        con = self.get_conn()
        cursor = con.cursor() 
        cursor.execute("SELECT room_no FROM Rooms WHERE status='Available'")
        rows = cursor.fetchall()    
        rooms = [row[0] for row in rows]

        if current_room and current_room not in rooms:
            rooms.append(current_room)
        con.close()
        return rooms

    def total_rooms(self):
        con = self.get_conn()
        cursor = con.cursor() 
        cursor.execute("SELECT COUNT(*) FROM Rooms")
        room = cursor.fetchone()[0] or []
        con.close()
        print(room)
        return room

    def room_type(self):
        con = self.get_conn()
        cursor = con.cursor() 
        cursor.execute("SELECT COUNT(*) FROM Rooms WHERE room_type='Single'")
        single_room = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Rooms WHERE room_type='Double'")
        double_room = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Rooms WHERE room_type='Deluxe'")
        deluxe_room = cursor.fetchone()[0]
        con.close()
        return single_room,double_room,deluxe_room

    def totalCheckin(self):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM Rooms WHERE status =?",("Check in",))
        tot = cursor.fetchone()[0]
        con.close()
        return tot

    def get_booked_room(self):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM Rooms WHERE status = 'Booked'")
        booked_room = cursor.fetchone()[0]
        con.close()
        return booked_room

    def checksameRoomID(self,room_no):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT 1 FROM Rooms WHERE room_no = ?",(room_no,))
        exists = cursor.fetchone() is not None
        return exists

    def changeRoom(self,current_room):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("UPDATE Rooms SET status=? WHERE room_no=?",('Available',current_room))
        con.commit()
        con.close()

#/////////////////////////////////////////////////////////////////

    def createBookingTable(self):
        con = self.get_conn()
        cursor = con.cursor()       
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS Bookings(
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        country TEXT,
        room_no TEXT,
        check_in_date TEXT,
        check_out_date TEXT,
        status TEXT,
        totalprice INTEGER,
        DOB TEXT,
        email TEXT,
        no_of_adults INTEGER,
        no_of_kids INTEGER,
        payment_type TEXt,
        holder_name TEXT,
        card_number INTEGER,
        CVV INTEGER
        )
        """)
        con.commit()
        con.close()

    def add_new_booking(self,firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids,payment_type,holder_name,card_number,CVV):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("INSERT INTO Bookings(first_name,last_name,phone,country,room_no,check_in_date,check_out_date,status,totalprice,DOB,email,no_of_adults,no_of_kids,payment_type,holder_name,card_number,CVV)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids,payment_type,holder_name,card_number,CVV))
        con.commit()
        print("Totalprice = ",totalprice)
        con.close()

    def view_booking_paginated(self,page=1,per_page=5):
        offset = (page - 1)* per_page
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Bookings  ORDER BY check_in_date DESC LIMIT ? OFFSET ?",(per_page,offset))
        rows = cursor.fetchall()
        cursor.execute("SELECT count(*) as total FROM Bookings")
        total = cursor.fetchone()["total"]

        con.close()
        return rows,total

    def get_booking_byid(self,book_id):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Bookings WHERE book_id = ?",(book_id,))
        row = cursor.fetchone()
        con.close()
        return row

    def search_booking_paginated(self,field,keyword,start_date,end_date,page=1,per_page=9):
        offset = (page-1)*per_page
        con = self.get_conn()
        cursor = con.cursor()

        query_parts = ["FROM Bookings WHERE 1=1"]
        params = []

        if keyword:
            query_parts.append(f"AND {field} LIKE ? ")
            params.append(f"%{keyword}%")

        if start_date:
            query_parts.append(f"AND check_in_date >= ? ")
            params.append(start_date)

        if end_date:
            query_parts.append("AND check_in_date <= ? ")
            params.append(end_date)

        where_caluse = " ".join(query_parts)

        query = f"SELECT * {where_caluse} ORDER BY book_id DESC LIMIT ? OFFSET ?"
        try:
            cursor.execute(query,params+[per_page,offset])   
            rows = cursor.fetchall()
        except Exception as e:
            print("Error:",query)

        query = f"SELECT COUNT(*) as total {where_caluse} "
        cursor.execute(query,params)
        total = cursor.fetchone()["total"]
        con.close()
        return total,rows if rows else []

    def update_booking(self,book_id,firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids,payment_type,holder_name,card_number,CVV):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("UPDATE Bookings SET first_name=?,last_name=?, phone=?, country=?, room_no=?, check_in_date=?, check_out_date=?, status=?, totalprice=?, DOB=?, email=?, no_of_adults=?, no_of_kids=?,payment_type=?,holder_name=?,card_number=?,CVV=?  WHERE book_id=?",
        (firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids,payment_type,holder_name,card_number,CVV,book_id))
        con.commit()
        con.close() 

    def delete_booking(self,book_id):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("DELETE FROM Bookings WHERE book_id = ?",(book_id,))
        con.commit()
        con.close()

    def booking_Cancel(self,id):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("UPDATE Bookings SET status = ? WHERE book_id =?",('Cancel',id))
        con.commit()
        con.close()


    def delete_Table(self):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("drop table Rooms")
        con.commit()
        con.close()

    def status_changed(self,room_no,status):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("UPDATE Rooms SET status=? WHERE room_no=?",
        (status,room_no))
        con.commit()
        con.close()

    def price_Cal(self,view):
        con = self.get_conn()
        cursor = con.cursor()

        if view == "monthly":
            query = """ 
            SELECT
                strftime('%Y-%m', check_out_date) AS period,
                SUM(totalprice) AS total_price
            FROM Bookings
            WHERE status = 'Check out'
            AND check_out_date <= date('now')
            GROUP BY period
            ORDER BY period 
            """
        else:
            query = """ 
            SELECT
                strftime('%Y', check_out_date) AS period,
                SUM(totalprice) AS total_price
            FROM Bookings
            WHERE status = 'Check out'
            AND check_out_date <= date('now')
            GROUP BY period
            ORDER BY period
            """

        rows = cursor.execute(query).fetchall()

        labels = [row[0] for row in rows]
        prices = [row[1] for row in rows]

        con.close()
        return {
            "labels" : labels,
            "prices" : prices
        }

    def delete_allBooking_info(self):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("DELETE FROM Bookings")
        con.commit()
        con.close()     


    # inject_test_data() 
    def inject_test_data(self):
        con =  self.get_conn()
        cursor = con.cursor()
    
        # Let's create 1 fake booking for each of the last 6 months
        # for i in range(6):
        #     # Calculate a date in the past
        #     past_date = (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m-%dT%H:%M')
        
        #     cursor.execute("""
        #         INSERT INTO Bookings(first_name, last_name, status, totalprice, check_in_date)
        #         VALUES (?, ?, ?, ?, ?)
        #     """, (f"Guest_{i}", "Test", "Check out", random.randint(200, 800), past_date))
        
        past_indate = datetime(2023,2,3,14,0).strftime('%Y-%m-%dT%H:%M')
        past_outdate = datetime(2023,2,5,14,0).strftime('%Y-%m-%dT%H:%M')

        cursor.execute("INSERT INTO Bookings(first_name,last_name,room_no,check_in_date,check_out_date,status,totalprice,email) VALUES(?,?,?,?,?,?,?,?)",
        ("Test4","4",1,past_indate,past_outdate,"Check out",900,"test4@gmail.com"))

        con.commit()
        con.close()
        print("Success! You now have 6 months of fake data to see your chart.")

    # inject_test_data() # Uncomment to run
