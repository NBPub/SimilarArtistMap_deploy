import json
from pathlib import Path
from dash import Dash, html, dcc, callback, Output, Input
import dash_daq as daq
import dash_bootstrap_components as dbc # https://dash-bootstrap-components.opensource.faculty.ai/docs/


import networkx as nx
from random import sample

from network_graph import network, net_figure
import plotly.graph_objects as go

# network(artist, add_neighbors, similar_artists)
    # returns G, add_neighbors
# net_figure(G, pos, artist, similar_artists, add_neighbors)
    # returns figure


"""Load Similar Artist Data"""

folder = Path(Path.cwd(), 'artist_data')
with open(Path(folder,'similar_artists.json'), 'r', encoding = 'utf-8') as file:
    similar_artists = json.loads(file.read())
with open(Path(folder,'artists_alias.json'), 'r', encoding = 'utf-8') as file:
    artists_alias = json.loads(file.read())

# drop-down needs explicit list
art_list = list(similar_artists.keys()) 

   
"""Dash Application""" 

app = Dash(__name__,  title="Sim Art Map",
           external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div([ 
    html.Div(dcc.Link('Network Layout Reference',
             href = "https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout"),
             className='mx-5 text-end'),
    
    html.H1(children='Similar Artists Map', className='mb-3'),
    
    html.Div([
        dcc.Dropdown(art_list, sample(art_list,1)[0], id='artist', clearable=False,),
        
        dcc.RadioItems(options=['Spring', 'Spiral', 'Shell','Kamada Kawai', 
                                'Planar', 'Random'],
                       value='Spring', id='network-layout', className='form-check'),
        
        daq.BooleanSwitch(id='add_neighbors', on=False, color="deeppink",
                          label="add neighbors", labelPosition='bottom', className='form-check'),
            ], className='input-group'),
    
    dcc.Graph(figure={},id='graph-content', className='mt-3'),
    
    dcc.Link('similarity scores provided by last.fm',
             href="https://www.last.fm/api/show/artist.getSimilar", 
             className='fst-italic mx-5'),
    
    html.Footer(dcc.Link('Source Code - GPLv3', href='https://github.com/NBPub/SimilarArtistMap'))   
], className='mt-2 mx-5')
    

@callback(
    Output('graph-content', 'figure'), # artist map
    Input('artist', 'value'), # artist selection
    Input('network-layout', 'value'), # network type
    Input('add_neighbors', 'on'), # neighbors
)


def update_graph(artist, layout, add_neighbors):
    if not artist:
        return {}
    G, _ = network(artist, add_neighbors, similar_artists, artists_alias)
    
    # match case for network layout
    match layout:
        case 'Spring':
            pos = nx.spring_layout(G, k=25 if add_neighbors else 1.5)
        case 'Spiral':
            pos = nx.spiral_layout(G, resolution=len(G.nodes)/25 if add_neighbors else 0.35) 
        case 'Shell':
            pos = nx.shell_layout(G) 
        case 'Random':
            pos = nx.random_layout(G)
        case 'Kamada Kawai': # can give warning if nodes > 45ish
            if add_neighbors:
                pos = nx.kamada_kawai_layout(G, pos=nx.kamada_kawai_layout(G))              
            else:
                pos = nx.kamada_kawai_layout(G)
        case 'Planar':
            try:
                pos = nx.planar_layout(G)
            except:
                return go.Figure(data=[],layout=go.Layout(title='Resulting network is not planar'))
        case _:
            return {} 
    
    fig = net_figure(G, pos, artist, similar_artists, add_neighbors, layout, artists_alias)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)