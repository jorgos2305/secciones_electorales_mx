import requests
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output

from config import APP_HOST

app = Dash(__name__)

app.layout = html.Div([
    html.H4('Mexican Elections'),
    html.P("Select a state"),
    dcc.Dropdown(id="state_selector", options=[n for n in range(1,33)]),
    dcc.Graph(id="graph")
])


@app.callback(
    Output("graph", "figure"),
    Input("state_selector", "value")
    )
def display_choropleth(value):
    
    if value is not None:
        response = requests.get(f"http://{APP_HOST}:8000/states/{value}/geom")
        feature = response.json()
        gdf = gpd.GeoDataFrame.from_features([feature])

        fig = px.choropleth_map(
            gdf,
            geojson=gdf.__geo_interface__,
            locations="state_id",
            featureidkey="properties.state_id",
            hover_data={
                "state_id" : True,
                "name"     : True,
                "capital"  : True
            },
            center={"lat":23.634501, "lon":-102.552784},
            zoom=3,
            map_style="open-street-map",
            width=600,
            height=600
        )
        fig.update_traces(
        marker_line_width=1,
        marker_line_color="black",
        marker_opacity=0.4
        )
    else:
        fig = px.choropleth_map(
            center={"lat":23.634501, "lon":-102.552784},
            zoom=3,
            map_style="open-street-map",
            width=600,
            height=600
        )

    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")