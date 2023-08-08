import logging
from typing import Optional, Dict
from gradio.routes import App

log = logging.getLogger(__name__)


def register_apis(app: App):
    @app.get("/pilot/node_status")
    def node_status():
        return {'status': 'ok'}

    @app.post("/pilot/reload-config")
    def reload_config():
        return {}
