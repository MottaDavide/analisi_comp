
import sys
from pathlib import Path
sys.path.append(str(Path('').absolute().parents[0]))
import pandas as pd
from scripts.A_import import *
from scripts.B_cleaning import *
from scripts.C_shaping import *
import pytest

@pytest.fixture
def get_data():
    return import_one_file()


def test_import(get_data):
    assert isinstance(get_data, pd.DataFrame)
    
def test_type(get_data):
    pass
    