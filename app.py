import requests
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

from config import APP_HOST

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Political candidate voting pool analysis'),
    html.P("Select a level:"),
    dcc.RadioItems(
        id='maplevel',
        options=["Country", "State", "Municipality"],
        value="State",
        inline=True
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"),
    Input("maplevel", "value"))
def display_choropleth(maplevel):
    
    response = requests.get(f"http://{APP_HOST}:8000/states/1/geom")
    feature = response.json()   
    fig = go.Figure()

    fig.add_trace(
        go.Choropleth(
            geojson=feature,
            locations=[15],
            z=[1],
            featureidkey="properties.state_id"
        )
    )

    fig.update_geos(fitbounds="locations", visible=False)
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")