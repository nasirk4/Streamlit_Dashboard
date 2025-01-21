import streamlit as st
import pandas as pd
import os
import warnings
import plotly.express as px
import plotly.figure_factory as ff

warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(page_title="PRR Program", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Pakistan Raises Revenue Program")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# File uploader
fl = st.sidebar.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xls", "xlsx"])

if fl is not None:
    filename = fl.name
    st.write(filename)
    try:
        if filename.endswith('.csv') or filename.endswith('.txt'):
            df = pd.read_csv(fl, encoding="ISO-8859-1")
        elif filename.endswith('.xls') or filename.endswith('.xlsx'):
            df = pd.read_excel(fl, encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    #os.chdir(r"D:/Personal/Python Projects/dashboard")
    try:
        df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Error loading default dataset: {e}")

# Start the Date Picker
col1, col2 = st.columns((2))

df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d/%m/%Y", dayfirst=True)

# Getting Min and Max Dates or range of dates
startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

# Setting date variables
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Filtering data with respect to dates picked
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Setting up sidebar and sidebar filters
st.sidebar.header("Choose Your Filter:")
region = st.sidebar.multiselect("Pick Region", df["Region"].unique())
state = st.sidebar.multiselect("Province", df["State"].unique())
city = st.sidebar.multiselect("Location", df["City"].unique())

# Filtering the data based on selected filters
filtered_df = df.copy()
if region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]
if state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]
if city:
    filtered_df = filtered_df[filtered_df["City"].isin(city)]

# Creating charts
col1, col2 = st.columns((2))

# Category-wise Sales Bar Chart
category_df = filtered_df.groupby("Category")["Sales"].sum().reset_index()
with col1:
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Region-wise Sales Pie Chart
with col2:
    st.subheader("Region Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# Filtered Data Downloaders
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv")

with cl2:
    with st.expander("Region_ViewData"):
        region_df = filtered_df.groupby("Region")["Sales"].sum().reset_index()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

# Visualization of Data based on time periods
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

# Line Chart
linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%b"))["Sales"].sum().reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

# Time Series Data Downloader
with st.expander("View Data of Line Chart:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download LineChart Data', data=csv, file_name="LineChartData.csv", mime='text/csv')

# Treemap
st.subheader("Hierarchical View of Sales Using Treemap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales",
                  hover_data=["Sales"], color="Sub-Category")
fig3.update_layout(width=800, height=600)
st.plotly_chart(fig3, use_container_width=True)

# Pie Charts for Segments and Category
Chart1, Chart2 = st.columns((2))
with Chart1:
    st.subheader("Segment Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with Chart2:
    st.subheader("Category Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="plotly_dark")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Showing data in tables with formatting
st.subheader(":point_right: Month Wise Sub-Category Wise Sample Table")
with st.expander("Sub_Category_Table"):
    df_sample = df[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]].head(5)
    fig = ff.create_table(df_sample, colorscale="cividis")
    st.plotly_chart(fig, use_container_width=True)

    # Month Wise Sub-Category Table
    st.markdown("Month Wise Sub-Category Table")
    filtered_df["Month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="Month")
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))

# Create a Scatter Plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1['layout'].update(title="Relationship Between Sales and Profits",
                       titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=19)),
                       yaxis=dict(title="Profit", titlefont=dict(size=19)))
st.plotly_chart(data1, use_container_width=True)

# Displaying top 500 rows of data in a table
with st.expander("Data Snapshot"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download Original Dataset
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download Original Data", data=csv, file_name="Original_Dataset.csv", mime="text/csv")
