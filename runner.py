import json
import threading
import logging
import time
from os import path
import json
from omegaconf import OmegaConf
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Any, Callable, Union, Optional, List, Dict, Tuple
import redis

from modules import shared, script_callbacks, scripts
from modules.sd_models import checkpoints_list, unload_model_weights, reload_model_weights, checkpoint_aliases
from modules.sd_vae import vae_dict
from modules.sd_models_config import find_checkpoint_config_near_filename

log = logging.getLogger("sd")

REDIS_KEYS = {
    'all_nodes': 'sd_n_nodes',
    'node_prefix': 'sd_n_status',
}


class NodeStatus(BaseModel):
    available: bool = True
    public_base_url: str
    web_ui: bool = True
    api_auth: Optional[str] = None  # user:pass
    status_interval: int = 5  # update interval seconds
    capacity: float = 1.0
    sd_models: List[Any] = []
    sd_vaes: List[Any] = []
    last_update: Optional[str] = None
    up_time: Optional[str] = None
    down_time: Optional[str] = None
    load: Optional[float] = 0


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
        self.nodeStatus = NodeStatus(public_base_url='')
        self.redis_clis: List[redis.Redis] = []
        self.basic_status_changed = True
        self.models_changed = True
        self.first_delay = 5

    def start(self, config_path=None):
        print('node pilot config:', config_path)
        if config_path is not None:
            self.config_path = config_path
        self.thread.start()

    def set_models(self):
        sd_mdoels = [{"title": x.title, "model_name": x.model_name, "sha256": x.sha256} for x in
                     checkpoints_list.values()]
        sd_vaes = [{"model_name": x} for x in vae_dict.keys()]
        status = self.nodeStatus
        status.sd_models = sd_mdoels
        status.sd_vaes = sd_vaes

    def load_config(self):
        self.conf = OmegaConf.load(self.config_path)
        node_info = self.conf.sd_node
        public_access = node_info.public_access
        public_https = public_access.get('public_https', False)
        public_host = public_access.host
        public_port = public_access.port
        if public_https:
            public_base_url = f'https://{public_host}'
            if public_port != 443:
                public_base_url = f'{public_base_url}:{public_port}'
        else:
            public_base_url = f'http://{public_host}'
            if public_port != 80:
                public_base_url = f'{public_base_url}:{public_port}'

        cmd_opts = shared.cmd_opts
        if cmd_opts.subpath:
            public_base_url = f'{public_base_url}/{cmd_opts.subpath}'

        print('public_base_url', public_base_url)

        redis_configs = self.conf.centric_redis
        self.redis_clis: List[redis.Redis] = []
        for rc in redis_configs:
            try:
                cli = redis.Redis(host=rc.host, port=rc.port, db=rc.db,
                                  username=rc.get('username', None),
                                  password=rc.get('password', None))
                # cli.set('cc-' + rc.label, rc.label)
                self.redis_clis.append(cli)
            except Exception as e:
                log.error(e)

        status = self.nodeStatus
        status.public_base_url = public_base_url
        status.capacity = node_info.capacity
        status.status_interval = node_info.status_interval
        status.web_ui = not cmd_opts.nowebui
        status.api_auth = cmd_opts.api_auth
        status.available = True
        # milliseconds
        status.up_time = datetime.utcnow().isoformat(timespec='seconds') + 'Z'

        self.set_models()

    def run(self):
        if self.status == 'not-start':
            time.sleep(self.first_delay)
            self.load_config()
        self.status = 'running'
        while True:
            try:
                self.update()
            except Exception as e:
                log.error(e)
            status = self.nodeStatus
            time.sleep(status.status_interval)

    def update(self):
        status = self.nodeStatus
        status.last_update = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
        # print(status)

        if len(self.redis_clis) == 0:
            log.warning('no redis cli')
            return

        mapping = {
            'last_update': status.last_update,
            'load': status.load,
        }
        if self.basic_status_changed:
            mapping.update({
                'available': str(status.available),
                'up_time': status.up_time,
                'down_time': status.down_time if status.down_time else '',
                'api_auth': status.api_auth if status.api_auth else '',
                'web_ui': str(status.web_ui),
                'status_interval': status.status_interval,
                'capacity': status.capacity,
            })

        if self.models_changed:
            # self.set_models()
            sd_models_json = json.dumps(status.sd_models)
            sd_vaes_json = json.dumps(status.sd_vaes)
            mapping.update({
                'sd_models': sd_models_json,
                'sd_vaes': sd_vaes_json,
            })
        # print(mapping)

        redis_status_key = f'{REDIS_KEYS["node_prefix"]}:{status.public_base_url}'
        for cli in self.redis_clis:
            if status.available:
                cli.hset(REDIS_KEYS['all_nodes'], status.public_base_url, status.last_update)
            else:
                cli.hdel(REDIS_KEYS['all_nodes'], status.public_base_url)
            cli.hset(redis_status_key, mapping=mapping)

        self.basic_status_changed = False
        self.models_changed = False


def get_node_runner(**kwargs):
    if NodeRunner.instance is None:
        NodeRunner(**kwargs)
    return NodeRunner.instance
