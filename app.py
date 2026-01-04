import pandas as pd
from dash import Dash, html, dcc
from plotly.express import line

# the path to the formatted data file
DATA_PATH = "./formatted_data.csv"

# load in data
data = pd.read_csv(DATA_PATH)

# ensure correct types
data["date"] = pd.to_datetime(data["date"], errors="coerce")
data["sales"] = pd.to_numeric(data["sales"], errors="coerce")

# drop bad rows and sort by date
data = data.dropna(subset=["date", "sales"]).sort_values(by="date")

# initialize dash
dash_app = Dash(__name__)

# create the visualization (with axis labels)
line_chart = line(
    data,
    x="date",
    y="sales",
    title="Pink Morsel Sales (Sorted by Date)",
    labels={"date": "Date", "sales": "Sales ($)"}
)

visualization = dcc.Graph(
    id="visualization",
    figure=line_chart
)

# create the header
header = html.H1(
    "Pink Morsel Visualiser",
    id="header"
)


# define the app layout
dash_app.layout = html.Div(
    style={"maxWidth": "1100px", "margin": "0 auto", "padding": "24px"},
    children=[
        header,
        visualization,
    ]
)

# this is only true if the module is executed as the program entrypoint
if __name__ == "__main__":
    dash_app.run(debug=True)
