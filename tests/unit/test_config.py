# -*- coding: utf-8 -*-

import os

from robot.config import load_config_from_file


def test_load_config_from_file(base_path):
    cfg_file = os.path.join(base_path, 'sample', 'sample.yml')
    cfg = load_config_from_file(cfg_file)

    assert 'gym' in cfg
