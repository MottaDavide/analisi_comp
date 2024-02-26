from pathlib import Path
import sys


from config import ROAD
import pandas as pd
import numpy as np

def import_one_file(path_to_file: Path = ROAD.input / "Comp_Analysis_FIL.xlsx"):
    """
    Imports a file into a pandas DataFrame based on the file extension.
    
    This function supports importing files with extensions: .xlsx, .csv, and .parquet.
    It reads the file into a pandas DataFrame with specific data types assigned to certain columns.
    The 'Short Trip - Datest Code' column is read as string, and 'No Return Frame - TOTAL Order Qty'
    is read as an integer (32-bit). If the file is a .xlsx or .csv, it also parses dates automatically.
    
    Parameters:
    - path_to_file (Path): The file path of the file to be imported. The path must include the file extension.
    
    Returns:
    - pd.DataFrame: A pandas DataFrame containing the imported data. If the file extension is not supported,
    the function may return an uninitialized variable or error, depending on its usage context.

    Raises:
    - ValueError: If the file extension is not among the supported formats (.xlsx, .csv, .parquet),
    a ValueError is raised indicating the unsupported file format.
    
    Example:
    ```
    df = import_one_file('path/to/file.csv')
    ```
    
    Note: This function assumes the pandas library is imported with the alias 'pd' and numpy with 'np'.
    Ensure these libraries are installed and imported in your script before using this function.
    """
    
    new_col_name = {
        'SAP - Order Type': 'order_type',
        'NPI_Release': 'release', 
        'Brand - code': 'brand',
        'Calendar - Planned Delivery Date - Date': 'planned_delivery_date',
        'Planned Delivery Date: Month': 'planned_delivery_month', 
        'Calendar - Order Date - Year Week': 'creation_yearweek',
        'Calendar - Planned Delivery Date - Year Week': 'planned_delivery_yearweek',
        'Customer Sold To Description act': 'customer_sold_to',
        'Customer: Code': 'customer',
        'SAP Optical/Sun/Clip On Desc': 'division',
        'Orders - KeyAccountCode': 'key_account_code', 
        'Subsidiary Name': 'datest_name',
        'Short Trip - Datest Code': 'datest', 
        'Short Trip - DEDALO Area': 'dedalo_area',
        'Acquisition Mode Desc': 'acquisition_mode_desc', 
        'Acquisition Mode Group': 'acquisition_mode_group',
        'Orders - Specification': 'order_specification', 
        'Customer Sales: GTM Rating': 'customer_type',
        'No Return Frame - TOTAL Order Qty': 'qty'
    }
    valid_extensions = (".xlsx", ".csv", ".parquet")
    if path_to_file.suffix in valid_extensions:
        if path_to_file.suffix == ".xlsx":
            df = pd.read_excel(path_to_file, 
                            dtype={'Short Trip - Datest Code': str, "No Return Frame - TOTAL Order Qty": np.int32,'Customer: Code': str},
                            parse_dates=True)
    
        elif path_to_file.suffix == ".csv":
            df = pd.read_csv(path_to_file, 
                            dtype={'Short Trip - Datest Code': str, "No Return Frame - TOTAL Order Qty": np.int32,'Customer: Code': str},
                            parse_dates=True)
    
        else:
            df = pd.read_parquet(path_to_file, 
                            dtype={'Short Trip - Datest Code': str, "No Return Frame - TOTAL Order Qty": np.int32,'Customer: Code': str},
                            engine='pyarrow')

        df = df.rename(columns=new_col_name)
        try:
            sorted(df.columns.to_list()) == sorted(list(new_col_name.values()))
        except:
            raise ValueError('Columns do not match. Please check the function "import_one_file" in the script "A_import.py". Chance the "new_col_name" dictionary')
        return df
    else:
        raise ValueError("Extension different from .xlsx, .csv, .parquet")
    


def import_all(path_to_folder: Path, word_to_check: str = "Comp_Analysis", aggregate: bool = True):
    """
    Imports all files starting with `word_to_check` from a folder and optionally aggregates them.

    Args:
        path_to_folder: Path to the folder containing the files.
        word_to_check: String to check if the filename starts with.
        aggregate: Boolean flag to indicate whether to aggregate the imported dataframes.

    Returns:
        A pandas DataFrame containing the aggregated data (if aggregate is True) or a list of DataFrames.
    """

    if not path_to_folder.exists():
        raise ValueError(f"Folder not found: {path_to_folder}")

    valid_extensions = (".xlsx", ".csv", ".parquet")
    dataframes = []

    for file in path_to_folder.glob("*"):
        if file.suffix in valid_extensions and file.name.startswith(word_to_check):
            print(f"Importing {file.name}")
            df = import_one_file(file)
            dataframes.append(df)

    if aggregate and len(dataframes) > 1:
        print('Aggregating')
        return pd.concat(dataframes)
    else:
        return dataframes
    

def import_area_group():
    """
    Imports an Excel file "FILIALI AREE DEDALO" stored in 02_NPI/USEFUL containing area group data into a pandas DataFrame.

    This function specifically targets an Excel file named "FILIALI_AREE DEDALO.xlsx" located in a directory
    specified by the `ROAD.external_area =  02_NPI/USEFUL` path. It imports the 'AREA_EXPORT_DEDALO' sheet using the 'openpyxl'
    engine. All columns are imported as strings to ensure consistency and to avoid any unintended type inference
    that pandas might perform.

    Returns:
    - pd.DataFrame: A DataFrame containing the data from the 'AREA_EXPORT_DEDALO' sheet of the specified Excel file.
    
    Note:
    - This function assumes that the 'pd' alias for pandas is already imported and that a 'ROAD' object with an
    'external_area' attribute (representing the path to the directory containing the Excel file) is defined
    and accessible within the scope where this function is called.
    
    - It is also assumed that the 'openpyxl' library is installed and available for use as the engine for reading
    Excel files. This is particularly useful for handling .xlsx files.

    Example Usage:
    ```
    df_areas = import_area_group()
    ```
    
    Ensure that any required libraries (pandas and openpyxl) are installed and imported, and that the 'ROAD'
    object is correctly configured before calling this function.
    """
    df = pd.read_excel(ROAD.external_data / "Aree.xlsx", 
                        sheet_name='AREA_EXPORT_DEDALO',
                        engine='openpyxl',
                        dtype=str,
                        usecols='B:C',
                        names=['dedalo_area','launch_type'])
    return df