from pathlib import Path
from config import ROAD
import pandas as pd
import pyarrow


def save(df: pd.DataFrame, path_output: Path = ROAD.output, name = 'df_comp.xlsx'):
    format = name.split(".")[-1]
    if format == 'xlsx':
        df.to_excel(path_output / name, index=False)
    
    elif format == 'parquet':
        df.to_parquet(path_output / name, index=False)
        
    elif format == 'csv':
        df.to_csv(path_output / name, index=False)