from platform import system
from typing import Final
from pathlib import Path

# root directory of the project
ROOT_DIR: Final = Path(__file__).parent.absolute()

# system: Windows, Darwin (Mac)
SYSTEM: Final = system()

DICT_ACQUISITION_MODE = {
    'EDI': 'REPLENISH'
}

DICT_CUSTOMER_TYPE = {
    'BPF': 'BP',
    'PF': 'P'
}

# various folders and files
class Road:
    """
    Class meant to store all the needed paths used in this project
    """
    def __init__(self):
        self.input = ROOT_DIR / Path(r"data/input")
        self.output = ROOT_DIR / Path(r"data/output")
        self.data = ROOT_DIR / Path(r"data")
        self.root_dir = ROOT_DIR
        if SYSTEM == 'Darwin':
            self.external_data = Path(r"/Volumes/share/Gruppo_Demand_Planning/02_NPI/02_Data")
            #self.external_area = Path(Path(r"/Volumes/share/Gruppo_Demand_Planning/02_NPI/USEFUL"))
        elif SYSTEM == 'Windows':
            self.external_data = Path(r"//luxapplp04/share/Gruppo_Demand_Planning/02_NPI/02_Data")
            #self.external_area = Path(Path(r"//luxapplp04/share/Gruppo_Demand_Planning/02_NPI/USEFUL"))
        else:
            raise SystemError('This project is available only in Windows or MacOS systems')
ROAD = Road()




