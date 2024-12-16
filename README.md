# E-Commerce Dashboard 🛍️

## 💡 Introduction
This is an interactive **E-Commerce Dashboard** built using **Streamlit**. The dashboard provides comprehensive insights into e-commerce performance. The dataset contains informations about customers, order items, products, prices, reviews, geolocation, and more. The goal of this dashboard is to assist in data-driven decision making by providing visualizations and key metrics based on e-commerce data.

## 🔧 Getting Started
### Requirements
**Step 1.** Set Up a Virtual Environment
```
conda create --name main-ds python=3.9
conda activate main-ds
```

**Step 2.** Install Dependencies
```
pip install -r requirements.txt
```

## 🚀 Run the Streamlit Dashboard
After installation, you can launch the dashboard by running the following command in your terminal:
```
streamlit run dashboard.py
```
This command will open the dashboard in your default web browser, allowing you to interact with the data and visualizations.

Alternatively, access the deployed e-commerce dashboard directly via the link:  
[e-commerce Streamlit Dashboard](https://e-commerce-gy6mqjhtp3ts42noagnktq.streamlit.app)

### Dashboard Features
1️⃣ **Data Range Filter:** Filter data by specific date range to view relevant metrics for that period.

2️⃣ **Total Orders and Total Revenue Metrics:** A metric displaying the total number of orders and total revenue for the selected date range.

3️⃣ **Daily Orders Line Plot:** A time series plot showing the number of orders per day.

4️⃣ **Order Distribution Pie Chart:** A pie chart that visualizes the distribution of total orders across different review scores.

5️⃣ **Delivery Time Metrics:** Metrics showing the average delivery time for each review score, providing insights into how delivery times correlate with customer satisfaction.

6️⃣ **Best Product Performance Bar Chart:** Highlights best-selling products based on customer reviews and the number of orders.

7️⃣ **RFM (Recency, Frequency, and Monetary) Metrics and Bar Charts:** Display customer segmentation based on their purchasing behaviour.

8️⃣ **Geospatial Map:** An interactive map that visualizes sales and revenue distribution accross various locations.

9️⃣ **About and Creator Sidebar:** Provides information about the dashboard and the creator.
