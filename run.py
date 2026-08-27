#!/usr/bin/env python3
"""
CoreClicks — Local Development Runner
"""
import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"🚀 CoreClicks is running at http://127.0.0.1:{port}")
    print(f"🔑 Demo Admin: admin@coreclicks.dev / Admin@12345")
    print(f"👤 Demo User:  user@coreclicks.dev  / User@12345")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
