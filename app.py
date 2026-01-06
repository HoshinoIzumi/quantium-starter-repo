import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# =====================
# Config
# =====================
DATA_PATH = "./formatted_data.csv"

# colors according to Soul Origin official website
COLORS = {
    "bg": "#F7F5F0",
    "card": "#FFFFFF",
    "accent": "#FDB813",
    "accent_soft": "#D9DEC8",
    "text": "#1E1E1E",
    "muted": "#4F4F4F",
}

# =====================
# Load & prepare data
# =====================
df = pd.read_csv(DATA_PATH)

df.columns = [c.strip().lower() for c in df.columns]

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
df["region"] = df["region"].astype(str).str.strip().str.lower()
df.columns = [c.strip().lower() for c in df.columns]

df = df.dropna(subset=["date", "sales", "region"])

# =====================
# App
# =====================
app = Dash(__name__)
app.title = "Pink Morsel Sales Dashboard"

# =====================
# Layout components
# =====================
header = html.Div(
    [
        html.H1("Pink Morsel Sales Dashboard"),
        html.P(
            "Were sales higher before or after the price increase on 15 January 2021? Please check on the chart.",
            className="subtitle",
        ),
    ],
    className="header",
)

region_filter = html.Div(
    [
        html.Span("Region:", className="filter-label"),
        dcc.RadioItems(
            id="region-filter",
            options=[
                {"label": "All", "value": "all"},
                {"label": "North", "value": "north"},
                {"label": "East", "value": "east"},
                {"label": "South", "value": "south"},
                {"label": "West", "value": "west"},
            ],
            value="all",
            inline=True,
            className="region-radio",
        ),
    ],
    className="filter-card",
)

chart = html.Div(
    dcc.Graph(id="sales-chart"),
    className="chart-card",
)

app.layout = html.Div(
    [
        header,
        region_filter,
        chart,
    ],
    className="page",
)

# =====================
# Callback
# =====================
@app.callback(
    Output("sales-chart", "figure"),
    Input("region-filter", "value"),
)
def update_chart(region):
    if region == "all":
        filtered = df
    else:
        filtered = df[df["region"] == region]

    daily = (
        filtered.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
    )

    fig = px.line(
        daily,
        x="date",
        y="sales",
        labels={"date": "Date", "sales": "Sales ($)"},
    )

    fig.update_layout(
        plot_bgcolor=COLORS["card"],
        paper_bgcolor=COLORS["card"],
        font_color=COLORS["text"],
        margin=dict(l=40, r=20, t=20, b=40),
        hovermode="x unified",
    )

    fig.update_traces(line_color=COLORS["accent"], line_width=3)

    # price increase marker
    inc_date = pd.to_datetime("2021-01-15")

    # vertical line
    fig.add_shape(
        type="line",
        x0=inc_date,
        x1=inc_date,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",  # 0~1 means full chart height
        line=dict(color=COLORS["muted"], width=2, dash="dash"),
    )

    # label for the line
    fig.add_annotation(
        x=inc_date,
        y=1,
        xref="x",
        yref="paper",
        text="Price increase",
        showarrow=False,
        yanchor="bottom",
        xanchor="left",
        font=dict(color=COLORS["muted"]),
    )

    return fig


# =====================
# Run
# =====================
if __name__ == "__main__":
    app.run(debug=True)
