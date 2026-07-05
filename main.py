from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, yaml
from dotenv import load_dotenv

app = FastAPI()

# 1. Defaults
config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000"
}

# 2. YAML layer
if os.path.exists("config.development.yaml"):
    with open("config.development.yaml", "r") as f:
        yaml_config = yaml.safe_load(f)
        config.update(yaml_config)

# 3. .env layer
load_dotenv()
if os.getenv("APP_PORT"):
    config["port"] = int(os.getenv("APP_PORT"))
if os.getenv("NUM_WORKERS"):
    config["workers"] = int(os.getenv("NUM_WORKERS"))
if os.getenv("APP_API_KEY"):
    config["api_key"] = os.getenv("APP_API_KEY")

# 4. OS env vars (APP_* prefix)
if os.getenv("APP_WORKERS"):
    config["workers"] = int(os.getenv("APP_WORKERS"))

@app.get("/effective-config")
async def effective_config(request: Request):
    # 5. CLI overrides (?set=key=value)
    overrides = request.query_params.getlist("set")
    for item in overrides:
        if "=" in item:
            key, value = item.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Type coercion
            if key in ["port", "workers"]:
                config[key] = int(value)
            elif key == "debug":
                config[key] = value.lower() in ["true", "1", "yes", "on"]
            else:
                config[key] = value

    # Mask api_key
    masked = config.copy()
    masked["api_key"] = "****"

    return JSONResponse(masked)
