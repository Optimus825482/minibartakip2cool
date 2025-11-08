release: python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database tables created')"
web: gunicorn app:app
