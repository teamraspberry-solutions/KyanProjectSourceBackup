# config.py

# ----------------------------------------------
# API Keys and Credentials
# ----------------------------------------------
# Azure OpenAI API
AZURE_OPENAI_API_KEY = "Cg10kdlEepiZPkzbDNhY6qQm4W7gulx0Ylol5ofhKbcNYTEQSFj6JQQJ99AKAC77bzfXJ3w3AAABACOGsGeY"
AZURE_OPENAI_REGION = "southindia"  # E.g., "eastus"
AZURE_OPENAI_ENDPOINT = "https://kyanopenaimodel.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview"
OPENAI_MODEL = "gpt-4"

# Azure Speech API
AZURE_SPEECH_API_KEY = "BucQLE9Q8sG1HNvjEkKsGLtGXlATXqWBS4RpTv8BoVKpiAv76gC8JQQJ99AKACqBBLyXJ3w3AAAYACOGWjnb"
AZURE_SPEECH_REGION = "southeastasia"  # E.g., "eastus"
AZURE_SPEECH_ENDPOINT = "https://your-speech-cognitive-service-url"

# Azure Sentiment Analysis API
AZURE_SENTIMENT_API_KEY = "8svMt89ekLhLNXt7zOSMz9YrQ6Iic7n7Gtp383tYyStqFQg0K6u5JQQJ99AKACqBBLyXJ3w3AAAaACOGREMD"
AZURE_SENTIMENT_REGION = "your_sentiment_region_here"  # E.g., "eastus"
AZURE_SENTIMENT_ENDPOINT = "https://kyansentimentanalysismodel.cognitiveservices.azure.com/"

# ----------------------------------------------
# Database Settings (Local and Cloud)
# ----------------------------------------------
# Local SQLite Database File Path
LOCAL_DB_PATH = "./kyan_local.db"  # Path to the local SQLite database

# Cloud Database Connection (example for PostgreSQL)
CLOUD_DB_HOST = "aws-0-ap-southeast-1.pooler.supabase.com"
CLOUD_DB_PORT = 5432  # Default port for PostgreSQL
CLOUD_DB_NAME = "postgres"
CLOUD_DB_USER = "postgres.khkcwmeyehvbjnvedlfe"
CLOUD_DB_PASSWORD = "projectraspberrykyan"

# ----------------------------------------------
# Sync Settings for Local to Cloud
# ----------------------------------------------
# Periodic sync interval (in seconds)
SYNC_INTERVAL = 1800  # 2 hours (adjust as needed)

# Cloud sync configuration
SYNC_TABLES = ["focus_tracker", "session", "sentiment"]  # Tables to sync to the cloud

# ----------------------------------------------
# Standby and Timeout Settings
# ----------------------------------------------
# Time before bot enters standby mode (in seconds)
STANDBY_TIMEOUT = 15  # 15 seconds of inactivity before standby

# ----------------------------------------------
# Study Session Settings
# ----------------------------------------------
# Focus tracking interval (in seconds)
FOCUS_TRACKING_INTERVAL = 30  # Track focus every 30 seconds during study sessions

# ----------------------------------------------
# Logging and Error Handling
# ----------------------------------------------
LOG_FILE_PATH = "./backup/kyan_bot.log"  # Path to log file
ERROR_LOGGING_ENABLED = True  # Toggle error logging

# ----------------------------------------------
# General Configurable Parameters
# ----------------------------------------------
# Set bot characteristics mode (1 = Friendly, 2 = Study Pal)
DEFAULT_CHARACTERISTIC_MODE = 1

# Speech Settings
SPEECH_RATE = 150  # Rate at which the bot speaks (words per minute)
SPEECH_VOLUME = 1  # Volume level (0 to 1)

# ----------------------------------------------
# Additional Settings (if necessary)
# ----------------------------------------------
# You can add more settings here as needed
