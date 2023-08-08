import threading
import logging
import time
from os import path
from omegaconf import OmegaConf
from modules import shared, script_callbacks, scripts

log = logging.getLogger(__name__)


class NodeRunner:
    instance = None

    def __init__(self, **kwargs):
        self.thread = threading.Thread(target=self.run)
        if NodeRunner.instance is not None:
            raise Exception("NodeRunner instance already exists")
        NodeRunner.instance = self
        self.config_path = None
        self.status = 'not-start'
        self.conf = None

    def start(self, config_path=None):
        if self.status == 'running':
            log.info('already running')
            return
        if config_path is not None:
            self.config_path = config_path
            self.conf = OmegaConf.load(self.config_path)
        self.thread.start()

    def run(self):
        self.status = 'running'
        cmd_opts = shared.cmd_opts
        print('subpath', cmd_opts.subpath)
        print('nowebui', cmd_opts.nowebui)
        print('api_auth', cmd_opts.api_auth)
        print('webui_auth', cmd_opts.gradio_auth)
        while True:
            print(OmegaConf.to_yaml(self.conf))
            print(time.time())
            time.sleep(5)


def get_node_runner(**kwargs):
    if NodeRunner.instance is None:
        NodeRunner(**kwargs)
    return NodeRunner.instance
