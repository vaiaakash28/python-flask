from flask import Flask, jsonify, redirect, render_template, request, session
import pymysql
from werkzeug.security import check_password_hash, generate_password_hash
import os


#-------------------app initialization------------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)
# app.secret_key = "mysecretkey1234"

#-------------------database connection------------------------------------
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="myuser",
        password="mypassword",
        database="student_db",
        cursorclass=pymysql.cursors.DictCursor
    )

#-------------------login------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db_connection()
        cur = db.cursor()

        cur.execute("SELECT * FROM student_table WHERE username=%s", (username,))
        student_table = cur.fetchone()

        db.close()

        if student_table and check_password_hash(student_table["password"], password):
            session["student_table"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

#-------------------add_student------------------------------------
@app.route("/add_student", methods=["POST"])
def add_student():

    if "student_table" not in session:
        return redirect("/login")

    name = request.form["name"]
    month = request.form["month"]
    status = request.form["status"]

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS results_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            month VARCHAR(50),
            status VARCHAR(20)
        )
    """)

    cur.execute(
        "INSERT INTO results_table (name, month, status) VALUES (%s, %s, %s)",
        (name, month, status)
    )

    db.commit()
    db.close()

    return redirect("/dashboard")

#-------------------logout------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

#-------------------dashboard------------------------------------
@app.route("/dashboard")
def dashboard():

    if "student_table" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

#-------------------register------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        name = request.form["name"]
        branch = request.form["branch"]
        semester = request.form["semester"]
        month = request.form["month"]
        fees = request.form["fees"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match"

        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        cur = db.cursor()

        # insert student
        student_query = """
        INSERT INTO student_table
        (username, name, branch, semester, password)
        VALUES (%s, %s, %s, %s, %s)
        """

        student_values = (
            username,
            name,
            branch,
            semester,
            hashed_password
        )

        cur.execute(student_query, student_values)

        # get auto-generated id
        student_id = cur.lastrowid

        # insert fees
        fees_query = """
        INSERT INTO fees_table(student_id, month, fees)
        VALUES (%s, %s, %s)
        """

        fees_values = (
            student_id,
            month,
            fees
        )

        cur.execute(fees_query, fees_values)

        db.commit()
        db.close()

        return redirect("/students")

    return render_template("register.html")

#--------------------signup------------------------------------
@app.route("/signup")
def signup():
    return render_template("signup.html")

#--------------------students------------------------------------
@app.route("/students")
def students():

    db = get_db_connection()
    cur = db.cursor()

    search_id = request.args.get("id")

    if search_id:
        query = "SELECT * FROM student_table WHERE id=%s"
        cur.execute(query, (search_id,))
        student = cur.fetchone()

        db.close()

        # convert single result into list so template works the same way
        return render_template(
            "show.html",
            students=[student] if student else [],
            student=student
        )

    else:
        cur.execute("SELECT * FROM student_table")
        data = cur.fetchall()

        db.close()

        return render_template(
            "show.html",
            students=data
        )
    
#--------------------student_list------------------------------------
@app.route("/student_list")
def student_list():

    if "student_table" not in session:
        return redirect("/login")

    db = get_db_connection()
    cur = db.cursor()

    query = """
    SELECT * FROM student_table
    """

    cur.execute(query)

    students = cur.fetchall()

    db.close()

    return render_template(
        "student_list_all.html",
        students=students
    )

#--------------------student_search------------------------------------
@app.route("/student_search")
def student_search():

    if "student_table" not in session:
        return redirect("/login")

    keyword = request.args.get("keyword")

    db = get_db_connection()
    cur = db.cursor()

    query = """
    SELECT * FROM student_table
    WHERE id LIKE %s
    OR name LIKE %s
    """

    value = (
        f"%{keyword}%",
        f"%{keyword}%"
    )

    cur.execute(query, value)

    students = cur.fetchall()

    db.close()

    return render_template(
        "student_list_all.html",
        students=students
    )

#--------------------addstudent------------------------------------
@app.route("/addStudent")
def addstudent():

    if "student_table" not in session:
        return redirect("/login")

    return render_template("addStudent.html")

#--------------------addmonth------------------------------------
@app.route("/addmonth")
def addmonth():

    if "student_table" not in session:
        return redirect("/login")

    return render_template("addMonth.html")

#--------------------add_month------------------------------------
@app.route("/add_month", methods=["POST"])
def add_month():

    if "student_table" not in session:
        return redirect("/login")

    student_id = request.form["student_id"]
    month = request.form["month"]
    fees = request.form["fees"]

    db = get_db_connection()
    cur = db.cursor()

    query = """
    INSERT INTO fees_table(student_id, month, fees)
    VALUES (%s, %s, %s)
    """

    values = (
        student_id,
        month,
        fees
    )

    cur.execute(query, values)

    db.commit()
    db.close()

    return redirect("/dashboard")

#--------------------pass_students------------------------------------
@app.route("/pass_students")
def pass_students():

    if "student_table" not in session:
        return redirect("/login")

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT * FROM results_table WHERE status='Pass'")

    students = cur.fetchall()

    db.close()

    return render_template(
        "student_list.html",
        students=students,
        title="Pass Students"
    )
#--------------------fail_students------------------------------------
@app.route("/fail_students")
def fail_students():

    if "student_table" not in session:
        return redirect("/login")

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT * FROM results_table WHERE status='Fail'")

    students = cur.fetchall()

    db.close()

    return render_template(
        "student_list.html",
        students=students,
        title="Fail Students"
    )

#--------------------colleges (JSON)------------------------------------
@app.route("/colleges")
def colleges():

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT * FROM college_table")

    data = cur.fetchall()

    db.close()

    return jsonify(data)

#--------------------colleges_list (HTML)------------------------------------
@app.route("/colleges_list")
def colleges_list():

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT * FROM college_table")

    colleges = cur.fetchall()

    db.close()

    return render_template(
        "college_list.html",
        colleges=colleges
    )

#--------------------home------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

#--------------------delete_student------------------------------------
@app.route("/delete_student/<int:id>")
def delete_student(id):

    if "student_table" not in session:
        return redirect("/login")

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("DELETE FROM student_table WHERE id=%s", (id,))

    db.commit()
    db.close()

    return redirect("/student_list")

#--------------------edit_student------------------------------------
@app.route("/edit_student/<int:id>")
def edit_student(id):

    if "student_table" not in session:
        return redirect("/login")

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT * FROM student_table WHERE id=%s", (id,))
    student = cur.fetchone()

    db.close()

    return render_template("edit_student.html", student=student)

#--------------------update_student------------------------------------
@app.route("/update_student/<int:id>", methods=["POST"])
def update_student(id):

    if "student_table" not in session:
        return redirect("/login")

    name = request.form["name"]
    branch = request.form["branch"]
    semester = request.form["semester"]

    db = get_db_connection()
    cur = db.cursor()

    cur.execute("""
        UPDATE student_table
        SET name=%s, branch=%s, semester=%s
        WHERE id=%s
    """, (name, branch, semester, id))

    db.commit()
    db.close()

    return redirect("/student_list")

if __name__ == "__main__":
    app.run(debug=True)