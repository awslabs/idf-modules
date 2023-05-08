import json
import os

p = os.getenv("SEEDFARMER_PROJECT_NAME")
d = os.getenv("SEEDFARMER_DEPLOYMENT_NAME")
m = os.getenv("SEEDFARMER_MODULE_NAME")

data = {
    "PROJECT_NAME":p,
    "DEPLOYMENT_NAME":d,
    "MODULE_NAME":m
    
}

with open("SEEDFARMER_MODULE_METADATA", "w") as f:
    f.write(json.dumps(data))
