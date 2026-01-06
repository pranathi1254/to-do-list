import os
import sqlite3
import tempfile
import pytest
from app import app, init_db

@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test_todo.db"
    app.config['DATABASE'] = str(db_file)
    init_db()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def db_all_tasks(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute('SELECT * FROM tasks')
    rows = cur.fetchall()
    conn.close()
    return rows


def test_index_empty(client, tmp_path):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'To-Do List Application' in rv.data


def test_add_and_list_task(client, tmp_path):
    db_path = app.config['DATABASE']
    resp = client.post('/add', data={'title': 'Test Task'}, follow_redirects=True)
    assert resp.status_code == 200
    rows = db_all_tasks(db_path)
    assert len(rows) == 1
    assert rows[0]['title'] == 'Test Task'


def test_edit_task(client):
    db_path = app.config['DATABASE']
    client.post('/add', data={'title': 'Old Title'}, follow_redirects=True)
    rows = db_all_tasks(db_path)
    tid = rows[0]['id']
    resp = client.post(f'/edit/{tid}', data={'title': 'New Title', 'status': 'Pending'}, follow_redirects=True)
    assert resp.status_code == 200
    rows = db_all_tasks(db_path)
    assert rows[0]['title'] == 'New Title'


def test_complete_and_delete(client):
    db_path = app.config['DATABASE']
    client.post('/add', data={'title': 'Do this'}, follow_redirects=True)
    rows = db_all_tasks(db_path)
    tid = rows[0]['id']
    client.get(f'/complete/{tid}', follow_redirects=True)
    rows = db_all_tasks(db_path)
    assert rows[0]['status'] == 'Completed'
    client.get(f'/delete/{tid}', follow_redirects=True)
    rows = db_all_tasks(db_path)
    assert len(rows) == 0


def test_reset_sequence(client):
    db_path = app.config['DATABASE']
    # create two tasks to advance the autoincrement counter
    client.post('/add', data={'title': 'A'}, follow_redirects=True)
    client.post('/add', data={'title': 'B'}, follow_redirects=True)
    rows = db_all_tasks(db_path)
    assert len(rows) == 2
    # delete all tasks
    for r in rows:
        client.get(f"/delete/{r['id']}", follow_redirects=True)
    rows = db_all_tasks(db_path)
    assert len(rows) == 0
    # reset sequence (allowed only when table empty)
    resp = client.post('/admin/reset_sequence', follow_redirects=True)
    assert resp.status_code == 200
    assert b'ID sequence reset' in resp.data
    # add a new task, its id should be 1
    client.post('/add', data={'title': 'New after reset'}, follow_redirects=True)
    rows = db_all_tasks(db_path)
    assert len(rows) == 1
    assert rows[0]['id'] == 1
