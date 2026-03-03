# Notification Configuration Template
# Copy this file to notification_config.py and fill in your credentials

# Email Notifications (SMTP)
EMAIL_ENABLED = False
EMAIL_SMTP_SERVER = "smtp.gmail.com"
EMAIL_SMTP_PORT = 587
EMAIL_FROM = "your-email@example.com"
EMAIL_TO = "admin@example.com"
EMAIL_PASSWORD = "your-app-password"  # Use app-specific password for Gmail
EMAIL_SUBJECT_PREFIX = "[Bus Schedules]"

# Webhook Notifications (Slack, Discord, etc.)
WEBHOOK_ENABLED = False
WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
WEBHOOK_TYPE = "slack"  # Options: slack, discord, generic

# Pushover Notifications
PUSHOVER_ENABLED = False
PUSHOVER_USER_KEY = "your-user-key"
PUSHOVER_API_TOKEN = "your-api-token"

# Telegram Notifications
TELEGRAM_ENABLED = False
TELEGRAM_BOT_TOKEN = "your-bot-token"
TELEGRAM_CHAT_ID = "your-chat-id"

# Notification Settings
NOTIFY_ON_SUCCESS = False  # Send notification on successful downloads
NOTIFY_ON_ERROR = True     # Send notification on errors
NOTIFY_ON_CHANGE = True    # Send notification when PDFs change
NOTIFY_ON_NO_CHANGE = False  # Send notification when PDFs haven't changed

# Example Usage:
# 1. Copy this file: cp notification_config.example.py notification_config.py
# 2. Edit notification_config.py with your credentials
# 3. Enable desired notification methods
# 4. The script will automatically use these settings
