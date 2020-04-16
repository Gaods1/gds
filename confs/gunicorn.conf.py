import multiprocessing

bind = "localhost:8989"

workers = multiprocessing.cpu_count() * 2 + 1
errorlog = 'gunicorn/gunicorn_error.log'
daemon = True
reload = True
