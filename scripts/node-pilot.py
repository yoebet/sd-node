import logging
from os import path

import gradio as gr
from modules import shared, script_callbacks, scripts

from api import register_apis
from runner import NodeRunner, get_node_runner

log = logging.getLogger("sd")

pilot_enabled = False

config_path = shared.cmd_opts.pilot_config_path
if config_path is None:
    config_path = path.join(shared.cmd_opts.data_dir, 'pilot-config.yml')
if path.exists(config_path):
    pilot_enabled = True
    node_runner = get_node_runner()
    node_runner.start(config_path)


class NodePilot(scripts.Script):

    def __init__(self):
        pass

    def title(self):
        return 'Node Pilot'

    def ui(self, is_img2img):
        pass

    def show(self, is_img2img):
        return True

    def run(self, p, *args):
        pass

    def before_process(self, p, *args):
        pass

    def process(self, p, *args):
        pass

    def before_process_batch(self, p, *args, **kwargs):
        pass

    def process_batch(self, p, *args, **kwargs):
        pass

    def postprocess_batch(self, p, *args, **kwargs):
        pass

    def postprocess(self, p, processed, *args):
        pass


def on_app_started(block: gr.Blocks, app):
    register_apis(app)


def on_ui_settings():
    section = ('pilot', "Node Pilot")
    shared.opts.add_option(
        "node_option1",
        shared.OptionInfo(
            False,
            "option1 description",
            gr.Checkbox,
            {"interactive": True},
            section=section)
    )


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            checkbox = gr.Checkbox(
                True,
                label="Show image"
            )
            btn = gr.Button(
                "Refresh"
            ).style(
                full_width=False
            )
            status = gr.Text(shared.opts.data.get('node_option1'))

        btn.click(
            refresh,
            inputs=[checkbox],
            outputs=[status],
        )

        return [(ui_component, "Node Pilot", "node_pilot_tab")]


def refresh(checkbox):
    return []


script_callbacks.on_app_started(on_app_started)
script_callbacks.on_ui_tabs(on_ui_tabs)
script_callbacks.on_ui_settings(on_ui_settings)
