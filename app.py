from flask import Flask, render_template, request, redirect
import os
import psycopg2

app = Flask(__name__)

# 🔐 Admin Password
ADMIN_PASSWORD = "Sindhu@Memories2026💜"

# 🌐 Database URL (from Render Environment)
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)


# 🧱 Create table
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            person TEXT,
            sender TEXT,
            message TEXT
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()


# ✅ RUN DB INIT (Flask 3 fix)
init_db()


# 🏠 Home Page
@app.route('/')
def home():
    friends = [
        "Kanugula Sindhu",
        "Anugu Thanishika",
        "Pittu Vaishnavi",
        "Pasham Tejaswani"
    ]
    return render_template('index.html', friends=friends)


# 💌 Message Page
@app.route('/message/<path:name>', methods=['GET', 'POST'])
def message(name):

    if request.method == 'POST':
        sender = request.form.get('sender')
        msg = request.form.get('message')

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO messages (person, sender, message) VALUES (%s, %s, %s)",
            (name, sender, msg)
        )

        conn.commit()
        cur.close()
        conn.close()

        return redirect('/?success=1')

    return render_template('message.html', name=name)


# 🔐 Admin Page
@app.route('/sindhu-private-access', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        password = request.form.get('password')

        if password == ADMIN_PASSWORD:

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT person, sender, message FROM messages")
            data = cur.fetchall()

            cur.close()
            conn.close()

            # 🔄 Group messages by person
            messages = {}
            for person, sender, msg in data:
                if person not in messages:
                    messages[person] = []
                messages[person].append((sender, msg))

            return render_template('admin.html', messages=messages)

        else:
            return "<h3 style='color:red;'>❌ Wrong Password</h3>"

    return render_template('login.html')


# ▶ Run locally
if __name__ == '__main__':
    app.run(debug=True)
