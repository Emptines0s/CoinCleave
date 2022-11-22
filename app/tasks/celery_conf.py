from app import app, make_celery

celery = make_celery(app)
