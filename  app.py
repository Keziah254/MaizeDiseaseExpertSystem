from flask import Flask, render_template, request, redirect, session
from database import get_db, create_table
from inference import diagnose

app = Flask(__name__)
app.secret_key = "secret123"

create_table()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']

        conn = get_db()
        conn.execute("INSERT INTO users (name, password, role) VALUES (?, ?, ?)",
                     (name, password, role))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE name=? AND password=?",
                            (name, password)).fetchone()
        conn.close()

        if user:
            session['user'] = user['name']
            session['role'] = user['role']
            return redirect('/dashboard')
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    return render_template('dashboard.html', role=session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/diagnose', methods=['POST'])
def diagnose_route():
    if 'user' not in session:
        return redirect('/login')

    symptoms = request.form.getlist('symptoms')

    print("Symptoms received:", symptoms)

    if not symptoms:
        return "Please select at least one symptom"

    result = diagnose(symptoms)

    print("Diagnosis result:", result)

    return render_template('result.html', result=result)
@app.route('/delete_rule/<int:id>')
def delete_rule(id):
    if session.get('role') != 'admin':
        return "Access denied"

    conn = get_db()
    conn.execute("DELETE FROM rules WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')
@app.route('/add_rule', methods=['POST'])
def add_rule():
    if session.get('role') != 'admin':
        return "Access denied"

    conditions = request.form['conditions']
    disease = request.form['disease']
    treatment = request.form['treatment']
    cf = float(request.form['cf'])

    conn = get_db()
    conn.execute(
        "INSERT INTO rules (conditions, disease, treatment, cf) VALUES (?, ?, ?, ?)",
        (conditions, disease, treatment, cf)
    )
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/admin')
def admin_panel():
    if 'role' not in session or session['role'] != 'admin':
        return "Access denied"

    conn = get_db()
    rules = conn.execute("SELECT * FROM rules").fetchall()
    conn.close()

    return render_template('admin.html', rules=rules)

if __name__ == '__main__':
    app.run(debug=True)