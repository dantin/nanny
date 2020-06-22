# -*- coding: utf-8 -*-

import hashlib


_MD5_CODEC = hashlib.md5()


def md5_hexdigest(data):
    _MD5_CODEC.update(data.encode(encoding='utf-8'))
    return _MD5_CODEC.hexdigest()
