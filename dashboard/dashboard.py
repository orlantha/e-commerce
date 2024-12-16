import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import folium
from streamlit_folium import st_folium
sns.set(style='dark')


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_purchase_timestamp":"order_date",
        "order_id":"order_count",
        "price":"revenue"
    }, inplace=True)
    
    return daily_orders_df


def create_delivery_analysis_df(df):
    delivery_analysis_df = df.groupby(by="review_score").agg({
        "order_id":"nunique",
        "order_delivery_time":["max","mean", "median", "std"]
    })
    delivery_analysis_df.columns = ["order_count", "max_time", "mean_time", "median_time", "std_time"]

    return delivery_analysis_df


def create_top10_product(df):
    top_10_product = df[df['review_score'] == 5].groupby('product_category_name')['order_id'].nunique().nlargest(10)
    return top_10_product


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp":"max",   # mengambil tanggal order terakhir
        "order_id":"count",                 # menghitung jumlah pesanan (order)
        "price":"sum"                       # menghitung jumlah pendapatan (revenue) yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # Menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df


def create_orders_location(df):
    orders_location = df.groupby(by=["geolocation_state","geolocation_city","geolocation_lat","geolocation_lng"]).agg({
    "order_id":"nunique",
    "price":"sum"
    }).reset_index()
    orders_location.columns = ["state","city","latitude","longitude","order_count","revenue"]

    return orders_location


all_df = pd.read_csv("https://raw.githubusercontent.com/orlantha/e-commerce/refs/heads/main/dashboard/all_data.csv")


datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


# Membuat komponen filter
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:    
    # Mengambil start_date & end_date dari date_input
    st.sidebar.title('Filter')
    start_date, end_date = st.date_input(
        label='Select Date Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]


daily_orders_df = create_daily_orders_df(main_df)
delivery_analysis_df = create_delivery_analysis_df(main_df)
top_10_product = create_top10_product(main_df)
rfm_df = create_rfm_df(main_df)
orders_location = create_orders_location(main_df)


# ----------------------------------------------------------------
# Sidebar - About Dashboard and Creator
st.sidebar.title("About")
st.sidebar.info(
    """
    This dashboard provides comprehensive insights into e-commerce performance.
    \n- Use the sidebar filter to select a date range and view various metrics.
    \n- Explore daily orders and total revenue trends over time.
    \n- Analyze order distribution and average delivery time by customer review score.
    \n- View top-performing products based on highest review scores and the most orders.
    \n- Get insights into customer behavior using RFM metrics.
    \n- Discover geospatial insights related to sales and revenue across cities and states.
    """
)

st.sidebar.markdown(
    """
    **Created by:**<br>
    Orlantha Kendenan<br>
    orlantha.kdn@gmail.com
    """, unsafe_allow_html=True
)

st.sidebar.caption("(c) 2024")



# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header("E-Commerce Dashboard :sparkles:")
# ----------------------------------------------------------------
st.subheader("Daily Orders :shopping_bags:")
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_date"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="royalblue"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.divider()
# ----------------------------------------------------------------
st.subheader("Order Distribution and Average Delivery Time by Customer Review Score :star::truck:")


col1, col2 = st.columns([2, 1])

with col1:
    # Pie chart
    fig, ax = plt.subplots(figsize=(16, 6))
    explode = [0.1 if count == delivery_analysis_df['order_count'].max() else 0 for count in delivery_analysis_df['order_count']]
    
    delivery_analysis_df['order_count'].plot.pie(
        labels=delivery_analysis_df.index,
        autopct='%1.1f%%',
        colors=sns.color_palette("PuBu", len(delivery_analysis_df)),
        startangle=90,
        explode=explode,
        legend=False,
        textprops={'fontsize': 10}
    )
    ax.set_title("Distribution of Total Orders per Review Score", fontsize=20)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    st.pyplot(fig)

with col2:
    for score in sorted(delivery_analysis_df.index, reverse=True):
        avg_time = delivery_analysis_df.loc[score, "mean_time"]
        st.metric(f"Average Delivery Time (Score {score})", f"{avg_time:.0f} days")

st.divider()
# ----------------------------------------------------------------
st.subheader("Best Product Performance based on Highest Review Scores and The Most Orders :trophy:")

fig, ax = plt.subplots(figsize=(16, 8))
colors_product = ['royalblue' if value == top_10_product.max() else 'lightgrey' for value in top_10_product.values]

sns.barplot(
    x=top_10_product.values, 
    y=top_10_product.index, 
    palette=colors_product
)
ax.set_ylabel(None)
ax.set_xlabel("Number of Orders", fontsize=20)
ax.set_title(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.divider()
# ----------------------------------------------------------------
st.subheader("Best Customer Based on RFM Parameters :medal:")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (Days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR') 
    st.metric("Average Monetary", value=avg_monetary)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors_rfm = ["royalblue"] * 5

# Plot untuk recency 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors_rfm, ax=ax[0])
ax[0].set_ylim(0, None)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (Days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis ='x', labelsize=35, rotation=90)

# Plot untuk frequency
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors_rfm, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35, rotation=90)

# Plot untuk monetary
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors_rfm, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35, rotation=90)
 
st.pyplot(fig)

st.divider()
# ----------------------------------------------------------------
st.subheader("Geospatial Sales Insights :earth_americas:")

# Kota atau negara bagian dengan penjualan dan pendapatan tertinggi
highest_orders_city = orders_location.loc[orders_location["order_count"].idxmax()]
highest_revenue_city = orders_location.loc[orders_location["revenue"].idxmax()]

m = folium.Map(location=[-14.2350, -51.9253], tiles="OpenStreetMap", zoom_start=4)  # pusat Brazil

# Menambahkan titik untuk setiap kota
for _, row in orders_location.iterrows():
    folium.CircleMarker(
        location=(row["latitude"], row["longitude"]),
        radius=row['order_count'] ** 0.5,  # ukuran berdasarkan jumlah penjualan
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=(
            f"<b>{row['city']}</b><br>"
            f"State: {row['state']}<br>"
            f"Total Sales: {row['order_count']}<br>"
            f"Total Revenue: {row['revenue']:.2f}"
        )
    ).add_to(m)

# Menandai kota dengan penjualan dan pendapatan tertinggi
folium.Marker(
    location=(highest_orders_city["latitude"], highest_orders_city["longitude"]),
    popup=(
        f"<b>Highest Sales</b><br>"
        f"City: {highest_orders_city['city']}<br>"
        f"State: {highest_orders_city['state']}<br>"
        f"Total Sales: {highest_orders_city['order_count']}<br>"
        f"Total Revenue: {highest_orders_city['revenue']:.2f}"
    ),
    icon=folium.Icon(color='green')
).add_to(m)

map_html_path = "geospatial_sales_map.html"
m.save(map_html_path)

st_folium(m, width=700, height=500)

with open(map_html_path, "rb") as f:
    st.download_button(
        label="Download Map as HTML",
        data=f,
        file_name="geospatial_sales_map.html",
        mime="text/html"
    )
