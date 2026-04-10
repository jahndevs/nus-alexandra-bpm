import os

Import("env")

config = {}
env_path = os.path.join(env.subst("$PROJECT_DIR"), ".env")

with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

env.Append(CPPDEFINES=[
    ("WIFI_SSID", env.StringifyMacro(config.get("WIFI_SSID", ""))),
    ("WIFI_PASSWORD", env.StringifyMacro(config.get("WIFI_PASSWORD", ""))),
    ("BACKEND_IP", env.StringifyMacro(config.get("BACKEND_IP", ""))),
    ("BACKEND_PORT", config.get("BACKEND_PORT", "8000")),
])
