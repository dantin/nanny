# -*- coding: utf-8 -*-

import os

import pytest


@pytest.fixture
def base_path():
    return os.path.join(os.curdir, 'misc')
