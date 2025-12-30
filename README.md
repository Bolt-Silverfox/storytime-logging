# Server Logs Viewer

A simple web interface for viewing server logs (Nginx, PM2, System, Auth) via a browser.

## Features

- View Nginx access/error logs
- View PM2 application logs
- View system logs (syslog, kernel)
- View auth logs (auth.log, fail2ban)
- Custom log path support
- Filter/search within logs
- Color-coded log entries (errors, warnings, info)

## Files

- `index.html` - Log viewer web interface
- `logs.py` - Python CGI script for reading logs
- `nginx-logs.conf` - Nginx site configuration

## Server Setup

### 1. Install fcgiwrap

```bash
sudo apt install fcgiwrap
sudo systemctl enable fcgiwrap
sudo systemctl start fcgiwrap
```

### 2. Deploy nginx configuration

```bash
sudo cp nginx-logs.conf /etc/nginx/sites-available/logs.storytimeapp.me
sudo ln -s /etc/nginx/sites-available/logs.storytimeapp.me /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 3. Set log read permissions

The web server user needs permission to read log files:

```bash
sudo usermod -aG adm www-data
sudo systemctl restart fcgiwrap
```

### 4. Add SSL (recommended)

```bash
sudo certbot --nginx -d logs.storytimeapp.me
```

### 5. (Optional) Add basic auth

To protect logs from public access:

```bash
sudo apt install apache2-utils
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

Then add to the nginx server block:

```nginx
auth_basic "Log Viewer";
auth_basic_user_file /etc/nginx/.htpasswd;
```

## Adding Custom Log Paths

Edit `logs.py` and add paths to the `CUSTOM_ALLOWED_PATHS` list:

```python
CUSTOM_ALLOWED_PATHS = [
    '/var/log/',
    '/home/shinobi/.pm2/logs/',
    '/path/to/your/app/logs/',
]
```

## Deployment

This repo auto-deploys to the server via GitHub Actions on push to `main`.

### Required GitHub Secrets

- `SSH_PRIVATE_KEY` - SSH private key for server access
- `SSH_HOST` - Server hostname or IP
- `SSH_USER` - SSH username
