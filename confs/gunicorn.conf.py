import multiprocessing

bind = "127.0.0.1:8787"
workers = multiprocessing.cpu_count() * 2 + 1
errorlog = 'gunicorn/gunicorn_error.log'
daemon = True
reload = True