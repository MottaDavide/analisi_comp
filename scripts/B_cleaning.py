from config import DICT_CUSTOMER_TYPE
from scripts.A_import import import_area_group
import pandas as pd


def replacing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace values in the 'customer_type' column of a DataFrame based on a predefined dictionary and fill missing values.

    This function replaces the values in the 'customer_type' column of the input DataFrame using a predefined
    dictionary `DICT_CUSTOMER_TYPE` available in the 'config.py' file. It then fills any remaining missing values in the 'customer_type' column with the
    mode of the column (the most frequently occurring value).

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing a 'customer_type' column to be processed.

    Returns
    -------
    pd.DataFrame
        A copy of the input DataFrame with the 'customer_type' column values replaced and missing values filled.

    Notes
    -----
    - The function operates on a copy of the input DataFrame to avoid modifying the original data.
    - It assumes the existence of a global dictionary `DICT_CUSTOMER_TYPE` used for replacing values.
    """
    
    
    df = df.copy()
    df['customer_type'] = df['customer_type'].replace(DICT_CUSTOMER_TYPE)
    df['customer_type'] = df['customer_type'].fillna(df['customer_type'].mode().iloc[0])
    return df


def grouping(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group a DataFrame by multiple columns and sum up a specific column's values.

    The function takes an input DataFrame and groups it by a predefined list of columns. It then sums up the values
    of the 'qty' column for each group.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame to be grouped and summed.

    Returns
    -------
    pd.DataFrame
        A DataFrame with rows grouped by the specified columns and the 'qty' column values summed within each group.

    Notes
    -----
    - The function operates on a copy of the input DataFrame to avoid modifying the original data.
    - The columns used for grouping are predefined within the function.
    """
    
    
    df = df.copy()
    columns_to_group = [
        'release',
        'brand',
        'planned_delivery_yearweek',
        'creation_yearweek',
        'customer',
        'customer_sold_to',
        'division',
        'dedalo_area',
        'acquisition_mode_group',
    ]
    column_to_operate = ['qty']
    df = df.groupby(by=columns_to_group, as_index=False)[column_to_operate].sum()
    return df


def cleaning(df: pd.DataFrame, adding_area = False) -> pd.DataFrame:
    """
    Clean a DataFrame by replacing values and grouping.

    This function applies a two-step cleaning process to the input DataFrame: first, it replaces the values in the
    'customer_type' column and fills missing values as specified in the `replacing_values` function. Second, it groups
    the DataFrame by a predefined set of columns and sums up the 'qty' column for each group, as specified in the
    `grouping` function.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame to be cleaned.

    Returns
    -------
    pd.DataFrame
        The cleaned DataFrame after applying value replacement and grouping operations.

    Notes
    -----
    - The cleaning process involves making copies of the DataFrame at each step to avoid modifying the original data.
    """
    
    df = df.copy()
    df = replacing_values(df)
    df = grouping(df)
    
    if adding_area:
        df_area = import_area_group()
        lenght_df = len(df)
        df = df.merge(df_area, on = ['dedalo_area'])
        assert len(df) == lenght_df, "Number of rows is not correct, check the merge"
        
    
    return df