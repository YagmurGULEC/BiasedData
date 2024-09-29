# app.py
from fastapi import FastAPI
import uvicorn
from .dash_app import app as dash_app
from starlette.middleware.wsgi import WSGIMiddleware
from dash import html, dcc

# Initialize FastAPI app
app = FastAPI()

dash_app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

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

# Mount the Dash app using WSGIMiddleware so that it works with FastAPI
app.mount("/dash", WSGIMiddleware(dash_app.server))
dash_app.layout = dash_app.layout
# FastAPI route (optional)
@app.get("/")
async def read_root():
    return {"message": "Hello word"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

