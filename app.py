from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "devsecret")
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "todo.db")

def get_db():
    db_path = app.config["DATABASE"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Task title cannot be empty", "warning")
        return redirect(url_for('index'))
    conn = get_db()
    conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()
    flash("Task added successfully", "success")
    return redirect(url_for('index'))

@app.route("/delete/<int:id>")
def delete_task(id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Task deleted", "info")
    return redirect(url_for('index'))

@app.route("/complete/<int:id>")
def complete_task(id):
    conn = get_db()
    conn.execute("UPDATE tasks SET status='Completed' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Task marked as completed", "success")
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = get_db()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()
    if not task:
        conn.close()
        flash('Task not found', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        status = request.form.get('status', 'Pending')
        if not title:
            flash('Title cannot be empty', 'warning')
            return redirect(url_for('edit_task', id=id))
        conn.execute('UPDATE tasks SET title=?, status=? WHERE id=?', (title, status, id))
        conn.commit()
        conn.close()
        flash('Task updated', 'success')
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', task=task)

@app.route('/admin/reset_sequence', methods=['POST'])
def reset_sequence():
    conn = get_db()
    count = conn.execute('SELECT COUNT(*) as c FROM tasks').fetchone()['c']
    if count != 0:
        conn.close()
        flash('Cannot reset sequence while tasks exist', 'warning')
        return redirect(url_for('index'))
    # Remove sqlite autoincrement sequence entry for tasks
    conn.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    conn.commit()
    conn.close()
    flash('ID sequence reset', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

