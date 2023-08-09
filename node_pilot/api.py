import logging
from gradio.routes import App

from .runner import NodeRunner, NodeStatus

log = logging.getLogger(__name__)


def register_apis(app: App, runner: NodeRunner):
    @app.get("/pilot")
    def index():
        return runner.state

    @app.get("/pilot/node_status")
    def node_status() -> NodeStatus:
        return runner.node_status

    @app.get("/pilot/node_config")
    def node_config():
        return runner.get_config_yaml()

    @app.post("/pilot/reload-config")
    def reload_config():
        runner.reload_config()
        return {}
