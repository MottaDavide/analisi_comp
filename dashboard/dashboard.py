import streamlit as st
import sys
from pathlib import Path
import plotly.express as px

sys.path.append(str(Path('').absolute().parents[0]))

import pandas as pd

st.set_page_config(page_title="Sales Dashboard",
                page_icon=":smile:",
                layout="wide")

@st.cache_data
def get_data():
    df = pd.read_excel(Path('').absolute() / 'data' /'output'/ 'df_comp_cleaned.xlsx', dtype={'common_creation_yearweek': str, 'common_planned_delivery_yearweek': str}, nrows=5000)
    
    return df

df = get_data()




# ------ SIDEBAR ---------
st.sidebar.header("Please Filter Here: ")
brand = st.sidebar.selectbox(
    "Select the Brand:",
    options=df.brand.unique()
)


release = st.sidebar.multiselect(
    "Select the Release:",
    options=df.release.unique(),
    default=df.release.unique()
)

df_selection = df.query(
    'brand == @brand & release == @release'
)

st.dataframe(df_selection)

# ----- MINIPAGE ---------
st.title(":smile: Sales Dashboard")
st.markdown("##")

# KPI
total_sales = int(df_selection.qty.sum())
number_of_distinct_customer = len(df_selection.customer.unique())
average_sales = round(df_selection.qty.mean(),1)

left_col, middle_col, right_col = st.columns(3)
with left_col:
    st.subheader("Total Sales:")
    st.subheader(f"{total_sales}")
    
with middle_col:
    st.subheader("Average Sales:")
    st.subheader(f"{average_sales}")
    
with right_col:
    st.subheader("# Customer:")
    st.subheader(f"{number_of_distinct_customer}")
    
st.markdown("---")



# BAR CHART


sales_by_creation = (
    df_selection[df_selection.common_creation_yearweek > '202400'].groupby(by = ['common_creation_yearweek', 'release'], as_index=False)['qty'].sum().sort_values('release')
)
fig_sales_by_creation = px.bar(
    sales_by_creation,
    x = 'common_creation_yearweek',
    y = 'qty',
    color='release',
    orientation='v',
    title="<b>Sales by Creation Date</b>",
    template='plotly_white',
    labels={'common_creation_yearweek': 'Creation Date (W)', 'qty': 'Qty'},
    barmode='group'
)


sales_by_delivery = (
    df_selection[df_selection.common_creation_yearweek > '202400'].groupby(by = ['common_planned_delivery_yearweek', 'release'], as_index=False)['qty'].sum().sort_values('release')
)
fig_sales_by_delivery = px.bar(
    sales_by_delivery,
    x = 'common_planned_delivery_yearweek',
    y = 'qty',
    color='release',
    orientation='v',
    title="<b>Sales by Delivery Date</b>",
    template='plotly_white',
    labels={'common_planned_delivery_yearweek': 'Delivery Date (W)', 'qty': 'Qty'},
    barmode='group'
)

left_col, right_col = st.columns(2)
left_col.plotly_chart(fig_sales_by_creation)
right_col.plotly_chart(fig_sales_by_delivery)

st.markdown("---")
