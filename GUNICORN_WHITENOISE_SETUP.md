# Gunicorn & WhiteNoise Configuration Guide

## What's Been Configured

### 1. **WhiteNoise**
- Added `whitenoise==6.7.0` to requirements.txt
- Added WhiteNoise middleware to MIDDLEWARE in settings.py
- Configured `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- Updated WSGI app to use WhiteNoise wrapper
- Created directories: `static/`, `staticfiles/`, and `media/`

### 2. **Gunicorn**
- Already in requirements.txt (gunicorn==23.0.0)
- Created `gunicorn.conf.py` with production-ready configuration
- Configured for multi-worker deployment with optimal settings

## Running the Application

### Development Mode
```bash
python manage.py runserver
```

### Production Mode with Gunicorn

1. **Collect Static Files** (in Docker or production):
```bash
python manage.py collectstatic --noinput
```

2. **Run Gunicorn**:
```bash
gunicorn -c gunicorn.conf.py field_management.wsgi:application
```

Or with custom parameters:
```bash
gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    field_management.wsgi:application
```

3. **Using Gunicorn Config File**:
```bash
gunicorn --config gunicorn.conf.py field_management.wsgi:application
```

## Static Files Configuration

| Setting | Value |
|---------|-------|
| STATIC_URL | `/static/` |
| STATIC_ROOT | `{BASE_DIR}/staticfiles` |
| STATICFILES_DIRS | `{BASE_DIR}/static` |
| STATICFILES_STORAGE | CompressedManifestStaticFilesStorage |
| MEDIA_URL | `/media/` |
| MEDIA_ROOT | `{BASE_DIR}/media` |

## Gunicorn Configuration Details

The `gunicorn.conf.py` includes:
- **Workers**: Auto-calculated as `(CPU_count * 2) + 1`
- **Bind Address**: `0.0.0.0:8000`
- **Timeout**: 30 seconds
- **Worker Class**: sync (suitable for Django)
- **Logging**: Stdout/stderr for Docker
- **Access Log Format**: Detailed with request duration

## Docker Integration

Add this to your Dockerfile:
```dockerfile
# Collect static files
RUN python manage.py collectstatic --noinput

# Run with Gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "field_management.wsgi:application"]
```

Or in your docker-compose.yml:
```yaml
command: gunicorn --bind 0.0.0.0:8000 --workers 4 field_management.wsgi:application
```

## Nginx Reverse Proxy (Optional)

Add to your nginx.conf for reverse proxying:
```nginx
upstream django {
    server gunicorn:8000;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

## Environment Variables

For production, ensure these are set:
- `DJANGO_SETTINGS_MODULE=field_management.settings`
- `ALLOWED_HOSTS` (update in settings.py for your domain)
- Database credentials (PostgreSQL)

## Troubleshooting

### Static Files Not Loading
1. Run `python manage.py collectstatic --noinput`
2. Check STATIC_ROOT and STATIC_URL are correct
3. Ensure staticfiles directory is writable

### Connection Issues
- Check Gunicorn is bound to correct address: `--bind 0.0.0.0:8000`
- Verify firewall allows port 8000

### Worker Issues
- Reduce workers if memory constrained: `--workers 2`
- Increase timeout if requests are slow: `--timeout 60`

## Performance Tips

1. Use `--workers = (2 * CPU_cores) + 1` for production
2. Use `--worker-class gthread` for I/O bound operations
3. Monitor with: `gunicorn --statsd-host localhost:8125`
4. Use nginx caching for static files
5. Enable WhiteNoise compression for faster delivery

## Verification

Check everything is working:
```bash
# Test Gunicorn starts without errors
gunicorn --check-config gunicorn.conf.py

# Test static files collection
python manage.py collectstatic --dry-run

# Check static files are being served
curl http://localhost:8000/static/
```
