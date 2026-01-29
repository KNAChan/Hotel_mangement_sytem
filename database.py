import sqlite3

class Database():
    def __init__(self):
        self.createTable()
        self.createBookingTable()
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
        photo TEXT
        )
        """)
        con.commit()
        con.close()

    def add_rooms(self,room_no,room_type,price,photo):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("INSERT INTO Rooms(room_no,room_type,price,status,photo) VALUES(?,?,?,?,?)",
        (room_no,room_type,price,"Available",photo))
        con.commit()
        con.close()

    def view_rooms_paginated(self,page=1,per_page=5):
        offset = (page - 1)* per_page
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Rooms LIMIT ? OFFSET ?",(per_page,offset))
        rows = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM Rooms")
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

    def update_room(self,room_id,room_no,room_type,price,status):
        con = self.get_conn()
        cursor = con.cursor()       
        cursor.execute("UPDATE Rooms SET room_no=?, room_type=?, price=?, status=? WHERE id=?",
        (room_no,room_type,price,status,room_id))
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
        no_of_kids INTEGER
        )
        """)
        con.commit()
        con.close()

    def add_new_booking(self,firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("INSERT INTO Bookings(first_name,last_name,phone,country,room_no,check_in_date,check_out_date,status,totalprice,DOB,email,no_of_adults,no_of_kids)VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids))
        con.commit()
        con.close()

    def view_booking_paginated(self,page=1,per_page=5):
        offset = (page - 1)* per_page
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Bookings LIMIT ? OFFSET ?",(per_page,offset))
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

    def search_booking_paginated(self,field,keyword,page=1,per_page=5):
        offset = (page-1)*per_page
        con = self.get_conn()
        cursor = con.cursor()
        query = f"SELECT * FROM Bookings WHERE {field} LIKE ? ORDER BY Check_in_date DESC LIMIT ? OFFSET ?"
        cursor.execute(query,(f"%{keyword}%",per_page,offset))      
        rows = cursor.fetchall()
        query = f"SELECT COUNT(*) as total FROM Bookings WHERE {field} LIKE ?"
        cursor.execute(query,(f"%{keyword}%",))
        total = cursor.fetchone()["total"]
        con.close()
        return total,rows if rows else []

    def update_booking(self,book_id,firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("UPDATE Bookings SET first_name=?,last_name=?, phone=?, country=?, room_no=?, check_in_date=?, check_out_date=?, status=?, totalprice=?, DOB=?, email=?, no_of_adults=?, no_of_kids=? WHERE book_id=?",
        (firstname,lastname,phone,country,room_no,check_in_date,check_out_date,status,totalprice,dob,email,Noadults,Nokids,book_id))
        con.commit()
        con.close() 

    def delete_booking(self,book_id):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("DELETE FROM Bookings WHERE book_id = ?",(book_id,))
        con.commit()
        con.close()


    def delete_Table(self):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("drop table Bookings")
        con.commit()
        con.close()

    def status_changed(self,room_no,status):
        con = self.get_conn()
        cursor = con.cursor()
        cursor.execute("UPDATE Rooms SET status=? WHERE room_no=?",
        (status,room_no))
        con.commit()
        con.close()
