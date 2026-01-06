# To-Do List Application (Flask + SQLite)

This project is a simple To-Do List web application built with Flask (Python) and SQLite. It demonstrates the SDLC phases: Requirements, Design, Implementation, Testing, and Deployment.

## Features
- Add tasks
- View tasks
- Edit tasks (title and status)
- Mark tasks as Completed
- Delete tasks

## SDLC Summary
- Requirements: Provide CRUD for tasks, persistent storage with SQLite, simple UI.
- Design: Flask backend, SQLite database, Bootstrap frontend templates.
- Implementation: `app.py` contains routes and DB logic. Templates are under `templates/`.
- Testing: Automated tests using `pytest` are under `tests/`.
- Deployment: Run locally with Flask; for production, use a WSGI server.

## Setup (Windows)
1. Create a virtual environment:
   python -m venv venv
2. Activate it:
   .\venv\Scripts\Activate
3. Install requirements:
   pip install -r requirements.txt
4. Run the app:
   python app.py
5. Run tests:
   pytest -q

## Files
- `app.py` - Flask application and DB initialization
- `templates/` - HTML templates (`index.html`, `edit.html`)
- `tests/` - pytest test suite

---

Happy coding!