from flask import Flask, jsonify
import pymysql

app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="myuser",
        password="Aakash@5454",
        database="college_db"
    )

@app.route("/students")
def students():
    db = get_db_connection()
    cur = db.cursor()

    cur.execute("SELECT * FROM college_table")
    data = cur.fetchall()

    db.close()

    return jsonify(data)



@app.route("/")
def home():
    return "Flask is running!"


if __name__ == "__main__":
    app.run(debug=True)