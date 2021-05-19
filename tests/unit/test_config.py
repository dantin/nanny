# -*- coding: utf-8 -*-

import os

import pytest

from nanny.config import NannyConfig


@pytest.fixture
def cfg_file_path(base_path):
    return os.path.join(base_path, 'sample.cfg')


def test_config(cfg_file_path):
    nanny = NannyConfig(cfg_file_path)

    assert 'gym' in nanny.cfg
    assert 'DEFAULT' in nanny.cfg
