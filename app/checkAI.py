import os
import subprocess
import re

def check_AI_exist() -> list:
    return __get_providers()

def use_AI(providers: str):
    if providers == "ollama":
        local_models = __get_local_model()
    pass

def __get_local_model():
    result = subprocess.run(["ollama", "ls"], check=True, text=True, capture_output=True)
    local_models = re.findall(r"\n([^ ]+)", result.stdout.strip())

    return local_models

def __get_providers():
    keywords = ["ollama", "antropic", "openai", "gemini"]
    providers = []

    for key, val in os.environ.items():
        for kw in keywords:
            if kw in key.lower() or kw in val.lower():
                providers.append(kw)

    return providers

def __call_ollama():
    import requests

    url = "http://localhost:11434/api/chat"

