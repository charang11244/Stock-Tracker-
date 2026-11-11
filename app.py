import io
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Stock Tracker | Inventory Intelligence",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#17243a; --muted:#718096; --line:#e8edf4; --teal:#18a999; --blue:#5577ee; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(135deg,#f6f8fc 0%,#eef3fa 100%); color:var(--ink); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#142238 0%,#1d3150 100%); }
[data-testid="stSidebar"] * { color:#eaf1fb !important; }
[data-testid="stSidebar"] .stRadio label { padding:8px 10px; border-radius:10px; }
.block-container { padding-top:1.6rem; padding-bottom:2.5rem; max-width:1500px; }
.hero { background:linear-gradient(115deg,#172b49 0%,#24476c 58%,#167f82 100%); padding:26px 30px; border-radius:22px; color:white; margin-bottom:22px; box-shadow:0 14px 35px rgba(30,58,90,.16); }
.hero h1 { font-family:'Manrope',sans-serif; font-size:30px; font-weight:800; margin:0 0 5px 0; color:white; }
.hero p { color:#d4e4f2; margin:0; font-size:14px; }
.eyebrow { text-transform:uppercase; letter-spacing:2px; font-size:10px; font-weight:700; color:#9ee8df; margin-bottom:8px; }
.metric-card { background:white; border:1px solid #e8edf4; border-radius:17px; padding:17px 18px; box-shadow:0 5px 18px rgba(35,55,80,.045); min-height:118px; }
.metric-label { color:#7b8798; font-size:12px; font-weight:600; margin-bottom:8px; }
.metric-value { color:#17243a; font-family:'Manrope',sans-serif; font-size:27px; font-weight:800; line-height:1.1; }
.metric-note { color:#8995a6; font-size:11px; margin-top:8px; }
.section-title { font-family:'Manrope',sans-serif; color:#1c2c43; font-weight:800; font-size:18px; margin:8px 0 12px 0; }
.panel { background:white; border:1px solid #e8edf4; border-radius:17px; padding:18px 20px; }
.pill { display:inline-block; background:#e9f8f5; color:#128779; padding:5px 10px; border-radius:20px; font-size:11px; font-weight:700; }
div[data-testid="stDataFrame"] { border:1px solid #e8edf4; border-radius:12px; overflow:hidden; }
.stButton>button { border-radius:10px; font-weight:700; }
small, .muted { color:#7d899a; }
hr { border-color:#e8edf4; }
</style>
""", unsafe_allow_html=True)

# ---------- Data helpers ----------
REQUIRED = ["Product_ID", "Product_Name", "Category", "Quantity", "Unit_Price", "Units_Sold"]
ALIASES = {
    "product_id": "Product_ID", "sku": "Product_ID", "id": "Product_ID",
    "product_name": "Product_Name", "product": "Product_Name", "name": "Product_Name",
    "category": "Category", "type": "Category",
    "quantity": "Quantity", "stock": "Quantity", "stock_quantity": "Quantity",
    "unit_price": "Unit_Price", "price": "Unit_Price", "cost": "Unit_Price",
    "units_sold": "Units_Sold", "sales": "Units_Sold", "sold": "Units_Sold",
    "reorder_level": "Reorder_Level", "minimum_stock": "Reorder_Level",
    "supplier": "Supplier", "last_updated": "Last_Updated"
}

def normalize_data(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    rename = {}
    for col in df.columns:
        key = col.lower().replace(" ", "_").replace("-", "_")
        if key in ALIASES:
            rename[col] = ALIASES[key]
    df = df.rename(columns=rename)
    for col in ["Product_ID", "Product_Name", "Category"]:
        if col not in df:
            df[col] = [f"{col[:3].upper()}-{i+1:03d}" for i in range(len(df))] if col == "Product_ID" else "Uncategorized"
    for col in ["Quantity", "Unit_Price", "Units_Sold"]:
        if col not in df:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)
    if "Reorder_Level" not in df:
        df["Reorder_Level"] = 15
    df["Reorder_Level"] = pd.to_numeric(df["Reorder_Level"], errors="coerce").fillna(15).clip(lower=0)
    if "Supplier" not in df: df["Supplier"] = "Not specified"
    if "Last_Updated" not in df: df["Last_Updated"] = date.today().isoformat()
    df["Stock_Value"] = df["Quantity"] * df["Unit_Price"]
    df["Revenue"] = df["Units_Sold"] * df["Unit_Price"]
    df["Stock_Status"] = df.apply(
        lambda r: "Out of stock" if r["Quantity"] <= 0 else ("Low stock" if r["Quantity"] <= r["Reorder_Level"] else "Healthy"),
        axis=1
    )
    return df

@st.cache_data
def load_sample():
    return pd.read_csv("data/sample_inventory.csv")

if "inventory" not in st.session_state:
    st.session_state.inventory = normalize_data(load_sample())

df = st.session_state.inventory.copy()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("<div style='padding:12px 8px 24px 8px'><div style='font-size:30px'>📦</div><div style='font-family:Manrope;font-size:22px;font-weight:800'>STOCK TRACKER</div><div style='font-size:10px;letter-spacing:2px;color:#9fb4cc'>INVENTORY INTELLIGENCE</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("WORKSPACE", ["Overview", "Inventory", "Sales Analytics", "Data Center", "Insights"], label_visibility="visible")
    st.markdown("---")
    st.markdown("**QUICK CSV UPLOAD**")
    sidebar_csv = st.file_uploader("Upload inventory CSV", type=["csv"], key="sidebar_inventory_csv")
    if sidebar_csv is not None:
        if st.button("Load CSV into dashboard", use_container_width=True, type="primary"):
            try:
                uploaded_df = pd.read_csv(sidebar_csv)
                st.session_state.inventory = normalize_data(uploaded_df)
                st.success(f"Loaded {len(uploaded_df):,} records")
                st.rerun()
            except Exception as e:
                st.error(f"CSV upload failed: {e}")
    st.caption("You can also upload and preview files in Data Center.")
    st.markdown("---")
    st.markdown("**DATA STATUS**")
    st.markdown(f"<span class='pill'>● {len(df):,} records loaded</span>", unsafe_allow_html=True)
    st.caption("Big Data Analytics Project")
    st.markdown("---")
    st.caption("Stock Tracker • v1.0")

# ---------- Header ----------
def hero(title, subtitle, eyebrow="INVENTORY ANALYTICS"):
    st.markdown(f"""<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>""", unsafe_allow_html=True)

def metric(label, value, note, icon):
    st.markdown(f"""<div class="metric-card"><div style="display:flex;justify-content:space-between;align-items:center"><div class="metric-label">{label}</div><div style="font-size:20px">{icon}</div></div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>""", unsafe_allow_html=True)

def chart_style(fig, height=330):
    fig.update_layout(
        height=height, margin=dict(l=8,r=8,t=35,b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#65748a", size=11),
        title_font=dict(family="Manrope", size=15, color="#1c2c43"),
        legend_title_text="", hoverlabel=dict(bgcolor="#172b49", font_color="white"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#edf1f6")
    fig.update_yaxes(gridcolor="#edf1f6", zeroline=False)
    return fig

if page == "Overview":
    hero("Inventory overview", "A clear view of stock health, product movement and business performance.", "CONTROL CENTER  /  OVERVIEW")
    total_products = df["Product_ID"].nunique()
    total_units = int(df["Quantity"].sum())
    stock_value = df["Stock_Value"].sum()
    revenue = df["Revenue"].sum()
    low = int((df["Stock_Status"] == "Low stock").sum())
    out = int((df["Stock_Status"] == "Out of stock").sum())
    c = st.columns(4)
    with c[0]: metric("Total products", f"{total_products:,}", "Unique items in catalogue", "🧾")
    with c[1]: metric("Units in stock", f"{total_units:,}", "Across all product categories", "📦")
    with c[2]: metric("Inventory value", f"₹{stock_value:,.0f}", "Current stock × unit price", "💎")
    with c[3]: metric("Sales revenue", f"₹{revenue:,.0f}", "Units sold × unit price", "↗️")
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.45,1])
    with left:
        st.markdown("<div class='section-title'>Sales performance by category</div>", unsafe_allow_html=True)
        cat = df.groupby("Category", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)
        fig = px.bar(cat, x="Category", y="Revenue", color="Revenue", color_continuous_scale=["#b9d9e8","#5577ee","#18a999"], text_auto=".2s")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_style(fig,340), use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Stock health distribution</div>", unsafe_allow_html=True)
        status = df["Stock_Status"].value_counts().rename_axis("Status").reset_index(name="Products")
        fig = px.pie(status, names="Status", values="Products", hole=.68, color="Status",
                     color_discrete_map={"Healthy":"#18a999","Low stock":"#f2b84b","Out of stock":"#ed6a75"})
        fig.update_traces(textposition="outside", textinfo="percent+label", hole=.68)
        st.plotly_chart(chart_style(fig,340), use_container_width=True)
    st.markdown("<div class='section-title'>Needs attention</div>", unsafe_allow_html=True)
    a,b = st.columns(2)
    with a:
        st.markdown(f"<div class='panel'><div style='font-weight:700;color:#b7791f'>⚠️ Low-stock products</div><div style='font-size:30px;font-weight:800;color:#17243a'>{low}</div><div class='muted'>Items at or below their reorder level</div></div>", unsafe_allow_html=True)
    with b:
        st.markdown(f"<div class='panel'><div style='font-weight:700;color:#d35462'>⛔ Out-of-stock products</div><div style='font-size:30px;font-weight:800;color:#17243a'>{out}</div><div class='muted'>Items with zero available quantity</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Recent inventory snapshot</div>", unsafe_allow_html=True)
    st.dataframe(df[["Product_ID","Product_Name","Category","Quantity","Unit_Price","Stock_Status"]].head(8), use_container_width=True, hide_index=True)

elif page == "Inventory":
    hero("Inventory catalogue", "Search, filter and review every product in your inventory.", "WORKSPACE  /  INVENTORY")
    f1,f2,f3 = st.columns([1.4,1,1])
    with f1: search = st.text_input("Search product", placeholder="Search by product name or ID…")
    with f2: categories = st.multiselect("Category", sorted(df["Category"].dropna().unique()), default=[])
    with f3: statuses = st.multiselect("Stock status", ["Healthy","Low stock","Out of stock"], default=[])
    view = df.copy()
    if search:
        view = view[view["Product_Name"].astype(str).str.contains(search, case=False, na=False) | view["Product_ID"].astype(str).str.contains(search, case=False, na=False)]
    if categories: view = view[view["Category"].isin(categories)]
    if statuses: view = view[view["Stock_Status"].isin(statuses)]
    st.markdown(f"<div class='pill'>{len(view):,} matching products</div>", unsafe_allow_html=True)
    st.dataframe(view[["Product_ID","Product_Name","Category","Quantity","Reorder_Level","Unit_Price","Stock_Value","Supplier","Stock_Status"]],
                 use_container_width=True, hide_index=True,
                 column_config={"Unit_Price":st.column_config.NumberColumn(format="₹ %.2f"),"Stock_Value":st.column_config.NumberColumn(format="₹ %.2f")})
    st.markdown("<div class='section-title'>Category stock distribution</div>", unsafe_allow_html=True)
    cat = view.groupby("Category",as_index=False)["Quantity"].sum().sort_values("Quantity",ascending=False)
    fig=px.bar(cat,x="Category",y="Quantity",color="Category",color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(chart_style(fig,300),use_container_width=True)

elif page == "Sales Analytics":
    hero("Sales intelligence", "Explore revenue contribution, product performance and sales patterns.", "ANALYTICS  /  SALES")
    total_rev = df["Revenue"].sum()
    units_sold = int(df["Units_Sold"].sum())
    avg_price = df.loc[df["Units_Sold"]>0,"Unit_Price"].mean() if (df["Units_Sold"]>0).any() else 0
    c=st.columns(3)
    with c[0]: metric("Total revenue",f"₹{total_rev:,.0f}","Calculated from units sold", "💰")
    with c[1]: metric("Units sold",f"{units_sold:,}","Total recorded product movement","🛒")
    with c[2]: metric("Average selling price",f"₹{avg_price:,.0f}","Average unit price of sold items","🏷️")
    left,right=st.columns(2)
    with left:
        st.markdown("<div class='section-title'>Top 10 products by revenue</div>",unsafe_allow_html=True)
        top=df.groupby("Product_Name",as_index=False)["Revenue"].sum().nlargest(10,"Revenue").sort_values("Revenue")
        fig=px.bar(top,x="Revenue",y="Product_Name",orientation="h",color="Revenue",color_continuous_scale=["#b9d9e8","#5577ee"])
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_style(fig,380),use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Category revenue mix</div>",unsafe_allow_html=True)
        cat=df.groupby("Category",as_index=False)["Revenue"].sum()
        fig=px.pie(cat,names="Category",values="Revenue",hole=.55,color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(chart_style(fig,380),use_container_width=True)
    st.markdown("<div class='section-title'>Revenue by product category</div>",unsafe_allow_html=True)
    st.dataframe(df.groupby("Category",as_index=False).agg(Products=("Product_ID","nunique"),Units_Sold=("Units_Sold","sum"),Revenue=("Revenue","sum")).sort_values("Revenue",ascending=False),
                 use_container_width=True,hide_index=True,column_config={"Revenue":st.column_config.NumberColumn(format="₹ %.2f")})

elif page == "Data Center":
    hero("Data center", "Bring your own inventory data, validate records and export clean analytics-ready data.", "DATA OPERATIONS  /  UPLOAD & EXPORT")
    st.markdown("<div class='panel'>",unsafe_allow_html=True)
    st.markdown("**Upload inventory CSV**")
    st.caption("Required columns: Product_ID, Product_Name, Category, Quantity, Unit_Price, Units_Sold. Optional: Reorder_Level, Supplier, Last_Updated. Common alternatives such as Product, Stock, Price and Sales are also recognized.")
    uploaded=st.file_uploader("Choose a CSV file",type=["csv"])
    if uploaded is not None:
        try:
            raw=pd.read_csv(uploaded)
            cleaned=normalize_data(raw)
            st.success(f"Loaded and prepared {len(cleaned):,} records.")
            st.dataframe(cleaned.head(10),use_container_width=True,hide_index=True)
            if st.button("Use this dataset in dashboard",type="primary"):
                st.session_state.inventory=cleaned
                st.rerun()
        except Exception as e:
            st.error(f"Could not read this CSV: {e}")
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Download data</div>",unsafe_allow_html=True)
    csv_bytes=df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download processed inventory CSV",data=csv_bytes,file_name="inventory_analytics_export.csv",mime="text/csv",type="primary")
    st.download_button("⬇️ Download sample CSV template",data=open("data/sample_inventory.csv","rb").read(),file_name="sample_inventory.csv",mime="text/csv")
    st.info("Tip: Keep one row per product or SKU. Use numeric values for quantity, price and units sold.")

elif page == "Insights":
    hero("Business insights", "Actionable observations generated from your current inventory dataset.", "DECISION SUPPORT  /  INSIGHTS")
    low_df=df[df["Stock_Status"]=="Low stock"].sort_values("Quantity")
    out_df=df[df["Stock_Status"]=="Out of stock"]
    top=df.groupby("Product_Name",as_index=False).agg(Units_Sold=("Units_Sold","sum"),Revenue=("Revenue","sum")).sort_values("Units_Sold",ascending=False)
    slow=top[top["Units_Sold"]==top["Units_Sold"].min()]
    most=top.head(5)
    col1,col2=st.columns(2)
    with col1:
        st.markdown("<div class='panel'><div style='font-size:12px;color:#718096;font-weight:700'>REPLENISHMENT PRIORITY</div><div style='font-size:23px;font-weight:800;margin:8px 0'>Stock requiring attention</div>",unsafe_allow_html=True)
        st.write(f"**{len(low_df)}** products are at or below their reorder level, and **{len(out_df)}** products are out of stock.")
        if len(low_df)+len(out_df):
            st.dataframe(pd.concat([out_df,low_df]).head(8)[["Product_Name","Quantity","Reorder_Level","Stock_Status"]],use_container_width=True,hide_index=True)
        else: st.success("All products are above their reorder levels.")
        st.markdown("</div>",unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='panel'><div style='font-size:12px;color:#718096;font-weight:700'>PRODUCT PERFORMANCE</div><div style='font-size:23px;font-weight:800;margin:8px 0'>Top-selling products</div>",unsafe_allow_html=True)
        st.dataframe(most[["Product_Name","Units_Sold","Revenue"]],use_container_width=True,hide_index=True,column_config={"Revenue":st.column_config.NumberColumn(format="₹ %.2f")})
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Automated observations</div>",unsafe_allow_html=True)
    if len(out_df): st.warning(f"{len(out_df)} product records have zero stock. Review replenishment before accepting further orders.")
    if len(low_df): st.warning(f"{len(low_df)} products have reached their reorder threshold.")
    if len(top) and top["Units_Sold"].sum()>0:
        st.success(f"Highest unit movement: **{top.iloc[0]['Product_Name']}** with {int(top.iloc[0]['Units_Sold']):,} units sold.")
    if df["Category"].nunique()>0:
        bestcat=df.groupby("Category")["Revenue"].sum().idxmax()
        st.info(f"Highest revenue category: **{bestcat}**.")
    st.caption("Insights are descriptive and depend on the quality and coverage of the uploaded dataset. Demand forecasting can be added as a separate ML module.")

st.markdown("<div style='text-align:center;color:#9aa6b5;font-size:11px;padding:24px 0 4px'>STOCK TRACKER INVENTORY INTELLIGENCE • BUILT WITH STREAMLIT, PANDAS & PLOTLY</div>",unsafe_allow_html=True)
