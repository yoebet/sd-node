import os
from modules import paths


def preload(parser):
    parser.add_argument("--pilot-config-path",
                        type=str,
                        help="config centric redis to register self",
                        default=os.path.join(paths.data_path, 'pilot-config.yml'))
