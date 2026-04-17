from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# 🔐 Admin password
ADMIN_PASSWORD = "Sindhu@Memories2026💜"


# 🗄️ Create database
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person TEXT,
            sender TEXT,
            message TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()


# 🏠 HOME PAGE
@app.route('/')
def home():
    friends = [
        "Kanugula Sindhu",
        "Anugu Thanishika",
        "Pittu Vaishnavi",
        "Pasham Tejaswani"
    ]
    return render_template('index.html', friends=friends)


# 💌 MESSAGE PAGE
@app.route('/message/<path:name>', methods=['GET', 'POST'])
def message(name):

    if request.method == 'POST':
        sender = request.form.get('sender')
        msg = request.form.get('message')

        conn = sqlite3.connect('messages.db')
        c = conn.cursor()

        c.execute(
            "INSERT INTO messages (person, sender, message) VALUES (?, ?, ?)",
            (name, sender, msg)
        )

        conn.commit()
        conn.close()

        # ✅ redirect with success popup
        return redirect('/?success=1')

    return render_template('message.html', name=name)


# 🔐 HIDDEN ADMIN (GROUPED MESSAGES)
@app.route('/sindhu-private-access', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        password = request.form.get('password')

        if password == ADMIN_PASSWORD:
            conn = sqlite3.connect('messages.db')
            c = conn.cursor()
            c.execute("SELECT person, sender, message FROM messages")
            data = c.fetchall()
            conn.close()

            # ✅ GROUP BY PERSON
            messages = {}
            for person, sender, msg in data:
                if person not in messages:
                    messages[person] = []
                messages[person].append((sender, msg))

            return render_template('admin.html', messages=messages)

        else:
            return "<h3 style='color:red;'>❌ Wrong Password</h3>"

    return render_template('login.html')


# ▶️ RUN APP
if __name__ == '__main__':
    app.run(debug=True)