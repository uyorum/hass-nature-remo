"""Constants for the Nature Remo integration."""

DOMAIN = "nature_remo"

CONF_ACCESS_TOKEN = "access_token"

API_BASE_URL = "https://api.nature.global"
UPDATE_INTERVAL = 60  # Polling interval in seconds (60 seconds to avoid 30 req/5 min limit safely)
