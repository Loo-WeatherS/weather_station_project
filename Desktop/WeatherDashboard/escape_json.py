import json

# Replace this with your actual JSON filename
with open("weather-station-25716-firebase-adminsdk-fbsvc-9a69b630a9.json") as f:
    raw = f.read()

# Escape for TOML (Streamlit Secrets)
escaped = raw.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")

# Print the result (to paste into Streamlit secrets)
print(f'FIREBASE_CREDENTIAL_JSON = """{escaped}"""')