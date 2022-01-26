from os.path import dirname, join
from typing import Dict

import pytest


@pytest.fixture(scope="session")
def data() -> Dict[str, str]:
    # This is the standard five-letter dictionary-plus-frequency setup
    datadir = join(dirname(__file__), "static")
    return {
        "5w": join(datadir, "5x1000.txt"),
        "6w": join(datadir, "6x800.txt"),
        "5f": join(datadir, "5x1000.freq"),
        "6f": join(datadir, "6x800.freq"),
    }
