import os
from functools import wraps
from flask import request, jsonify, g

API_KEY_REQUIRED = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
VALID_API_KEYS = set(filter(None, os.getenv("API_KEYS", "").split(",")))

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not API_KEY_REQUIRED:
            return f(*args, **kwargs)

        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in VALID_API_KEYS:
            return jsonify({
                "error": "Invalid or missing API key",
                "request_id": getattr(g, "request_id", None)
            }), 401
        return f(*args, **kwargs)
    return wrapper
