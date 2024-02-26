import pandas as pd
import numpy as np
from datetime import date, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM


def label_first_order(df: pd.DataFrame, week_inside_first: int = 2) -> pd.DataFrame:
    """
    Labels rows in a DataFrame with a binary indicator ('first_order') for first orders within a specific timeframe
    and categorizes the 'acquisition_mode_group' based on conditions related to first orders and specific groups.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame must include a 'creation_yearweek' column that represents the year and week of an order's
        creation. Additional columns to group by should also be present.
    week_inside_first : int, optional
        The number of weeks from the first order within which subsequent orders are also considered as first orders.
        The default is 2 weeks.

    Returns
    -------
    pd.DataFrame
        Returns a modified copy of the input DataFrame with an additional 'first_order' boolean column indicating
        if the row represents an order within the specified week window from the first order in its group. Also,
        a 'new_acquisition_mode' column is added to categorize the acquisition mode based on specific logic.

    Notes
    -----
    - The 'creation_yearweek' column should be in the 'YYYYWW' format, where 'YYYY' is the 4-digit year and 'WW' is
      the week number.
    - This function operates on a copy of the input DataFrame to avoid modifying the original data.
    - The grouping is based on a predefined list of columns: ['release', 'brand', 'customer', 'dedalo_area',
      'acquisition_mode_group'].
    - It assumes the week starts on Sunday for the purpose of calculations, following the convention in datetime
      conversion (format='%Y%W%w').
    - After labeling and categorization, auxiliary datetime columns used for calculations are dropped before returning
      the DataFrame.
    - The 'new_acquisition_mode' column categorization is based on whether an order is a first order within the
      specified timeframe, and on the original 'acquisition_mode_group' value, with specific rules for 'REP' and
      'RED CARPET' groups.

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'creation_yearweek': ['202101', '202102', '202103', '202104'],
    ...     'release': ['R1', 'R1', 'R2', 'R2'],
    ...     'brand': ['B1', 'B1', 'B2', 'B2'],
    ...     'customer': ['C1', 'C1', 'C2', 'C2'],
    ...     'dedalo_area': ['D1', 'D1', 'D2', 'D2'],
    ...     'acquisition_mode_group': ['REP', 'REP', 'RED CARPET', 'REP']
    ... })
    >>> df = label_first_order(df, week_inside_first=2)
    """
    
    df = df.copy()
    
    df['creation_yearweek_dt'] = pd.to_datetime(df['creation_yearweek'].astype(str) + '0', format='%Y%W%w')

    columns_to_group = [
    'release',
    'brand',
    'customer',
    'dedalo_area',
    #'acquisition_mode_group',
    ]
    column_to_operate = ['creation_yearweek_dt']
    df['first_creation_yearweek_dt'] = df.groupby(columns_to_group)[column_to_operate].transform('min')

    # Calculate the week difference from the first creation_yearweek within each group
    df['week_diff'] = (df['creation_yearweek_dt'] - df['first_creation_yearweek_dt']).dt.days / 7

    # Assign True if the week_diff < week_inside_first, else False
    df['first_order'] = (df['week_diff'] < week_inside_first)

    # Drop the auxiliary datetime columns
    df = df.drop(['creation_yearweek_dt', 'first_creation_yearweek_dt', 'week_diff'], axis=1)
    
    default = 'REPLENISHMENT'
    conditions = [
        (df['first_order'] == True) & (df['acquisition_mode_group'] == 'REP'),
        df['acquisition_mode_group'] == 'RED CARPET',
        (df['first_order'] == False) & (df['acquisition_mode_group'] == 'REP')
        
    ]
    outcomes = [
        'REP FIRST ORDER',
        'EVENT',
        'REP REPLENISHMENT',
    ]

    df['new_acquisition_mode'] = np.select(conditions, outcomes, default=default)
    
    
    return df


def create_common_creation_yearweek(df: pd.DataFrame):
    if not 'common_creation_yearweek' in df.columns:
        df = df.copy()
        df['year_release'] = df['release'].apply(lambda row: row[:4])
        df['max_year'] = max(df['year_release'].unique())
        df['diff'] = df['max_year'].astype(int) - df['year_release'].astype(int)
        df['common_creation_yearweek'] = df['creation_yearweek'] + df['diff']* 100
        df['common_planned_delivery_yearweek'] = df['planned_delivery_yearweek'] + df['diff']* 100  
        df = df.drop(['year_release','max_year','diff'], axis = 1)

    return df

def create_comp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['group_id'] = df['brand'] + '-' + df['customer'] + '-' + df['dedalo_area'] + '-' + df['new_acquisition_mode']

    groups_in_both_releases = df.groupby('group_id')['release'].nunique()
    groups_in_both_releases = groups_in_both_releases[groups_in_both_releases == 2].index

    df['comp'] = df['group_id'].apply(lambda x: 'Y' if x in groups_in_both_releases else 'N')

    df = df.drop('group_id', axis=1)
    
    return df
    
    
def create_till_today(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = create_common_creation_yearweek(df)
    year_week = (date.today() - timedelta(days=7)).strftime('%Y%W')
    
    df['till_today'] = df['common_creation_yearweek'].apply(lambda x: 'Y' if x <= int(year_week) else 'N')
    
    return df

    
def create_comp_today(df: pd.DataFrame, week_inside_first:int = None) -> pd.DataFrame:
    if not 'new_acquisition_mode' in df.columns or week_inside_first!=None:
        df = label_first_order(df, week_inside_first)
    if not 'comp' in df.columns:
        df = create_comp(df)
    if not 'till_today' in df.columns:
        df = create_till_today(df)
        
    df['group_id'] = df['brand'] + '-' + df['customer'] + '-' + df['dedalo_area'] + '-' + df['new_acquisition_mode'] + df['till_today'] + df['comp']

    groups_in_both_releases = df.groupby('group_id')['release'].nunique()
    groups_in_both_releases = groups_in_both_releases[groups_in_both_releases == 2].index

    df['comp_today_pre'] = df['group_id'].apply(lambda x: 'Y' if x in groups_in_both_releases else 'N')
    
    df['comp_today'] = 'N'
    df.loc[(df['till_today'] == 'Y') & (df['comp'] == 'Y') & (df['comp_today_pre'] == 'Y'), 'comp_today'] = 'Y'
    
    df = df.drop(['group_id', 'comp_today_pre'], axis=1)
    
    return df


def detect_outlier(df: pd.DataFrame, method = 'iqr'):
    df = df.copy()

    def detect_outliers_iqr(group: pd.DataFrame):
        # Calculate Q1, Q3 and IQR
        Q1 = group['qty'].quantile(0.25)
        Q3 = group['qty'].quantile(0.75)
        IQR = Q3 - Q1
        # Define outliers as being outside of Q1 - 1.5 * IQR and Q3 + 1.5 * IQR
        lower_bound = max(2,Q1 - 1.5 * IQR)
        upper_bound = Q3 + 1.5 * IQR
        # Mark outliers
        group['outlier'] = ~group['qty'].between(lower_bound, upper_bound)
        return group
    

    def detect_outliers_mad(group, threshold=3.5):
        median = np.median(group['qty'])
        mad = np.median(np.abs(group['qty'] - median))
        modified_z_score = 0.6745 * (group['qty'] - median) / mad
        group['outlier'] = modified_z_score.abs() > threshold
        return group
    
    def detect_outliers_iso(group):
        clf_iso = IsolationForest(random_state=42)
        # Reshape data for a single feature
        X = group['qty'].values.reshape(-1, 1)
        clf_iso.fit(X)
        # Predict and mark outliers
        group['outlier'] = clf_iso.predict(X) == -1
        return group
    
    def detect_outliers_svm(group):
        clf_svm = OneClassSVM(gamma='auto')
        # Reshape data for a single feature
        X = group['qty'].values.reshape(-1, 1)
        clf_svm.fit(X)
        # Predict and mark outliers
        group['outlier'] = clf_svm.predict(X) == -1
        return group
    
    
    
    
    if method == 'iqr':
        df_outliers = df.groupby(['brand', 'dedalo_area', 'new_acquisition_mode'], as_index=False).apply(detect_outliers_iqr)
    elif method == 'mad':
        df_outliers = df.groupby(['brand', 'dedalo_area', 'new_acquisition_mode'], as_index=False).apply(detect_outliers_mad)
    elif method == 'iso':
        df_outliers = df.groupby(['brand', 'dedalo_area', 'new_acquisition_mode'], as_index=False).apply(detect_outliers_iso)
    elif method == 'svm':
        df_outliers = df.groupby(['brand', 'dedalo_area', 'new_acquisition_mode'], as_index=False).apply(detect_outliers_svm)
        
    
    return df_outliers.reset_index(drop=True)


def create_comp_no_outliers(df: pd.DataFrame, method: str = 'iqr'):
    df = df.copy()
    if not 'comp' in df.columns:
        df = create_comp(df)
    if not 'outlier' in df.columns:
        df = detect_outlier(df, method) 
    
    df['comp_no_out'] = 'N'
    df.loc[(df['outlier'] == False) & (df['comp'] == 'Y'), 'comp_no_out'] = 'Y'
    
    return df
    
def create_comp_today_no_outliers(df: pd.DataFrame, method: str = 'iqr'):
    df = df.copy()
    if not 'comp_today' in df.columns:
        df = create_comp_today(df)
    if not 'outlier' in df.columns:
        df = detect_outlier(df, method)
    if not 'comp_no_out' in df.columns:
        df = create_comp_no_outliers(df)
        
        
    df['group_id'] = df['brand'] + '-' + df['customer'] + '-' + df['dedalo_area'] + '-' + df['new_acquisition_mode'] + df['outlier'].astype(str) + df['comp_today']

    groups_in_both_releases = df.groupby('group_id')['release'].nunique()
    groups_in_both_releases = groups_in_both_releases[groups_in_both_releases == 2].index

    df['comp_today_no_out_pre'] = df['group_id'].apply(lambda x: 'Y' if x in groups_in_both_releases else 'N')
    
    df['comp_today_no_out'] = 'N'
    df.loc[(df['outlier'] == False) & (df['comp_today'] == 'Y') & (df['comp_today_no_out_pre'] == 'Y'), 'comp_today_no_out'] = 'Y'
    
    df = df.drop(['group_id', 'comp_today_no_out_pre'], axis=1)
    
    return df
    
    