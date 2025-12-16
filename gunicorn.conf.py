"""
Gunicorn configuration file for field_management project
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "field_management"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Application
raw_env = [
    f"DJANGO_SETTINGS_MODULE=field_management.settings",
]

# SSL (optional, uncomment if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
# ca_certs = "/path/to/ca_certs"

# Server hooks
def post_fork(server, worker):
    """Called after a worker has been spawned."""
    pass

def post_worker_int(worker):
    """Called when a worker receives a SIGTERM."""
    pass

def pre_exec(server):
    """Called before exec of new process."""
    pass
