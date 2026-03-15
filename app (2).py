from flask import Flask, render_template, request
import sqlite3, uuid, os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    return sqlite3.connect("database.db")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    report_id = str(uuid.uuid4())[:8]
    category = request.form['category']
    description = request.form['description']

    file = request.files['evidence']
    filename = None

    if file and file.filename != "":
        filename = report_id + "_" + file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO reports (report_id, category, description, file_name, status)
        VALUES (?, ?, ?, ?, ?)
    """, (report_id, category, description, filename, "Submitted"))
    db.commit()
    db.close()

    return f"""
    <h3>Report Submitted Successfully</h3>
    <p>Your Tracking ID: <b>{report_id}</b></p>
    <a href='/'>Go Back</a>
    """

@app.route('/track', methods=['GET', 'POST'])
def track():
    status = None
    if request.method == 'POST':
        rid = request.form['report_id']
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT status FROM reports WHERE report_id=?", (rid,))
        row = cur.fetchone()
        status = row[0] if row else "Invalid Tracking ID"
        db.close()
    return render_template("track.html", status=status)

@app.route('/admin')
def admin():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM reports")
    reports = cur.fetchall()
    db.close()
    return render_template("admin.html", reports=reports)

if __name__ == "__main__":
    app.run(debug=True)
