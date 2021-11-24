# -*- coding: utf-8 -*-

import pytest
from aws_text_insight.lbd import hdl_hello_world


def test_handler():
    response = hdl_hello_world.handler(None, None)
    assert "Hello World" in response["message"]


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
