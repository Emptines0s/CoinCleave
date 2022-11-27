from app import app
from celery import Celery


def make_celery(app):
    celery = Celery(app.import_name,
                    backend=app.config['RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])

    celery.conf.task_routes = {
        'core.*': {'queue': 'core'},
        'subsc.*': {'queue': 'subsc'},
        'web.*': {'queue': 'web'}
    }
    celery.conf.beat_schedule = {
        'test-celery': {
            'task': 'check_subscription_time',
            'schedule': 60,
            'options': {'queue': 'subsc'}
        },
        'test-loop': {
            'task': 'trade_main_loop',
            'schedule': (60*60*4)+5,
            'options': {'queue': 'core'}
        },
        'test-tickers': {
            'task': 'update_exchange_tickers',
            'schedule': 60*60*12,
            'options': {'queue': 'web'}
        }
    }
    celery.conf.update()

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)
