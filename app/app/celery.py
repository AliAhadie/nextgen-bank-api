from celery import Celery
from kombu import Queue, Exchange
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(['authentication.tasks'])

app.conf.task_queues = [
    Queue(
        "q.email.tasks",
        Exchange("ex.email.tasks", type="direct"),
        routing_key="task",
        queue_arguments={
            'x-message-ttl':60000,
        }
    )
]

app.conf.task_routes = {
    "authentication.tasks.*": {"queue": "q.email.tasks", "routing_key": "task"},
}