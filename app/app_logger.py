import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = './logs'
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(request_id)s] %(name)s: %(message)s'
    )

    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            record.request_id = getattr(record, 'request_id', '-')
            return True

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.addFilter(RequestIdFilter())

    file = RotatingFileHandler(
        f'{log_dir}/app.log',
        maxBytes=10_000_000,
        backupCount=5
    )
    file.setFormatter(formatter)
    file.addFilter(RequestIdFilter())

    root.addHandler(console)
    root.addHandler(file)
