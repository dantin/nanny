# -*- coding: utf-8 -*-

import os

import pytest

from robot.config import load_config_from_file


@pytest.fixture
def cfg_file_path(base_path):
    return os.path.join(base_path, 'sample', 'sample.yml')


def test_load_config_from_file(cfg_file_path):
    cfg = load_config_from_file(cfg_file_path)

    assert 'gym' in cfg


def test_gym_config(cfg_file_path):
    cfg = load_config_from_file(cfg_file_path)

    assert 'gym' in cfg

    gym_cfg = cfg['gym']

    assert 'base_url' in gym_cfg
    assert 'sso' in gym_cfg
    assert 'phone' in gym_cfg
    assert 'name' in gym_cfg
    assert 'rule' in gym_cfg
