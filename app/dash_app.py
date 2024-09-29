import dash
import dash_bootstrap_components as dbc
# Create the Dash application, make sure to adjust requests_pathname_prefx
app = dash.Dash(__name__, requests_pathname_prefix='/dash/',external_stylesheets=[dbc.themes.BOOTSTRAP])
