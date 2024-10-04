import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc,html
from dash import html, dcc
from dash.dependencies import Input, Output,State

# Create the Dash application, make sure to adjust requests_pathname_prefx
app = dash.Dash(__name__, requests_pathname_prefix='/dash/',external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    html.Div(id='output-data-upload',children=[]),
    html.Button('Start Download', id='download-button', n_clicks=0),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5],
                    'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

@app.callback(
    Output('output-data-upload', 'children'),
    Input('download-button', 'n_clicks'),
    State
)
def download_data(n_clicks):
    if n_clicks > 0:
        return html.A('Click here to download data', href='/dash/download')
    return html.Div()
