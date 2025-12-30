#!/usr/bin/env python3
"""
CGI script for reading server logs.
Place this in your cgi-bin directory and configure nginx to execute it.
"""

import cgi
import os
import subprocess
import sys
from pathlib import Path

# PM2 logs location - update this to your actual user
PM2_LOG_DIR = '/home/ubuntu/.pm2/logs'

# Define allowed log paths for security
ALLOWED_LOGS = {
    'nginx': {
        'access': '/var/log/nginx/access.log',
        'error': '/var/log/nginx/error.log',
    },
    'pm2': {
        'out': PM2_LOG_DIR,
        'error': PM2_LOG_DIR,
    },
    'system': {
        'syslog': '/var/log/syslog',
        'kern': '/var/log/kern.log',
    },
    'auth': {
        'auth': '/var/log/auth.log',
        'fail2ban': '/var/log/fail2ban.log',
    },
}

# Additional custom paths you want to allow (add your app logs here)
CUSTOM_ALLOWED_PATHS = [
    '/var/log/',
    PM2_LOG_DIR,
    # Add more allowed directories here
]


def is_path_allowed(path):
    """Check if the requested path is in allowed directories."""
    resolved = os.path.realpath(path)
    for allowed in CUSTOM_ALLOWED_PATHS:
        if resolved.startswith(os.path.realpath(allowed)):
            return True
    return False


def read_log(filepath, lines=100):
    """Read last N lines from a log file using tail."""
    try:
        if not os.path.exists(filepath):
            return f"Log file not found: {filepath}"

        result = subprocess.run(
            ['tail', '-n', str(lines), filepath],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return f"Error reading log: {result.stderr}"

        return result.stdout or "(empty log file)"

    except subprocess.TimeoutExpired:
        return "Error: Timeout reading log file"
    except PermissionError:
        return f"Permission denied: {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"


def list_pm2_logs(log_type):
    """List and read PM2 logs."""
    pm2_log_dir = Path(PM2_LOG_DIR)

    if not pm2_log_dir.exists():
        return "PM2 logs directory not found. Is PM2 installed?"

    # Find relevant log files
    if log_type == 'out':
        pattern = '*-out.log'
    else:
        pattern = '*-error.log'

    logs = list(pm2_log_dir.glob(pattern))

    if not logs:
        return f"No {log_type} logs found in {pm2_log_dir}"

    # Read from the most recently modified log
    latest_log = max(logs, key=lambda p: p.stat().st_mtime)
    return f"=== {latest_log.name} ===\n\n" + read_log(str(latest_log), 100)


def main():
    # Output headers
    print("Content-Type: text/plain; charset=utf-8")
    print("Access-Control-Allow-Origin: *")
    print()

    # Parse query parameters
    form = cgi.FieldStorage()

    category = form.getvalue('category', '')
    log_type = form.getvalue('type', '')
    lines = min(int(form.getvalue('lines', 100)), 1000)  # Cap at 1000 lines
    custom_path = form.getvalue('path', '')

    # Handle custom path
    if custom_path:
        if is_path_allowed(custom_path):
            print(read_log(custom_path, lines))
        else:
            print(f"Access denied: {custom_path} is not in allowed paths")
        return

    # Handle predefined logs
    if category == 'pm2':
        print(list_pm2_logs(log_type))
        return

    if category in ALLOWED_LOGS and log_type in ALLOWED_LOGS[category]:
        filepath = ALLOWED_LOGS[category][log_type]
        print(read_log(filepath, lines))
    else:
        print(f"Unknown log: {category}/{log_type}")
        print("\nAvailable logs:")
        for cat, types in ALLOWED_LOGS.items():
            for t in types:
                print(f"  - {cat}/{t}")


if __name__ == '__main__':
    main()
