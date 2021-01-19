import os
import yaml

import trafaret as t
from typing import AnyStr, Dict

CONFIG_TRAFARET = t.Dict(
    {
        'mongo_uri': t.String(),
        'db_name': t.String(),
    }
)


def load_config(fname: AnyStr) -> Dict:
    if not os.path.isfile(fname):
        raise RuntimeError("Config file doesn't exist")

    with open(fname, 'rt') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    return CONFIG_TRAFARET.check(data)
