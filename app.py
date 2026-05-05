from flask import Flask, render_template, request, redirect, send_file
import os
import psycopg2

app = Flask(__name__)

# 🔐 Admin Password
ADMIN_PASSWORD = "Sindhu@Memories2026💜"

# 🌐 Database URL
DATABASE_URL = os.environ.get("DATABASE_URL")


# ✅ DB Connection
def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


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


# ✅ Run DB init safely
try:
    init_db()
except Exception as e:
    print("DB ERROR:", e)


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

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO messages (person, sender, message) VALUES (%s, %s, %s)",
                (name, sender, msg)
            )

            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            print("INSERT ERROR:", e)

        return redirect('/?success=1')

    return render_template('message.html', name=name)


# 🔐 Admin Page
@app.route('/sindhu-private-access', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        password = request.form.get('password')

        if password == ADMIN_PASSWORD:

            try:
                conn = get_connection()
                cur = conn.cursor()

                cur.execute("SELECT person, sender, message FROM messages")
                data = cur.fetchall()

                cur.close()
                conn.close()

            except Exception as e:
                return f"<h3>DB ERROR: {e}</h3>"

            # 🔄 Group messages
            messages = {}
            for person, sender, msg in data:
                if person not in messages:
                    messages[person] = []
                messages[person].append((sender, msg))

            return render_template('admin.html', messages=messages)

        else:
            return "<h3 style='color:red;'>❌ Wrong Password</h3>"

    return render_template('login.html')


# 📄 DOWNLOAD PDF (PER PERSON)
@app.route('/download-pdf/<name>')
def download_pdf_person(name):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT sender, message FROM messages WHERE person = %s",
        (name,)
    )

    data = cur.fetchall()

    cur.close()
    conn.close()

    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    y = 750

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, f"Messages for {name}")
    y -= 30

    pdf.setFont("Helvetica", 10)

    for sender, msg in data:
        text = f"{sender}: {msg}"

        pdf.drawString(50, y, text)
        y -= 20

        if y < 50:
            pdf.showPage()
            y = 750

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{name}.pdf",
        mimetype='application/pdf'
    )


# ▶ Run locally
if __name__ == '__main__':
    app.run(debug=True) 
