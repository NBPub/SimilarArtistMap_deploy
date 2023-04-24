import networkx as nx
import numpy as np
import plotly.graph_objects as go


"""Function to create Network"""
# specify artist, whether or not to add neighbors

def network(artist, add_neighbors, similar_artists, artists_alias):

    # Establish Network
    G = nx.MultiGraph()
    
    for val in similar_artists[artist]:
        weight = np.power(val['score'], 0.85) # scale match score
        # add edge from artist to each similar artist
        G.add_edge(artist,val['name'], weight=weight)
        
        if val['library']:
            # adjust name if needed, alias names saved in dict
            if val['name'] in similar_artists.keys():
                addname = val['name']
            elif val['name'] in artists_alias.keys():
                addname = artists_alias[val['name']]
            else:
            # skip if name not found
                continue
            
            # add_neighbors: include all connections from similar artists in library
            if add_neighbors:
                G.add_edges_from([(val['name'], 
                                   val2['name'], 
                                   np.power(val2['score'], 0.85)) \
                              for val2 in similar_artists[addname]])
            # no neighbors: only add intra-connections of similar artists
            else:
                for val2 in similar_artists[addname]:
                    if val2['name'] in list(G.nodes):
                        G.add_edge(val['name'], 
                                   val2['name'], 
                                   np.power(val2['score'], 0.85))
    return G, add_neighbors


"""Function to create Plotly Figure from Network Data"""

def net_figure(G, pos, artist, similar_artists, add_neighbors, layout, artists_alias):
    
    # disjointed lines for each edge
    edge_x = []
    edge_y = []
    
    # label edges at midpoints
    etext_x = []
    etext_y = []
    edge_text = []
    etext_colors = []
    inds = {val['name']:i for i,val in enumerate(similar_artists[artist])}
    
    for edge in G.edges():
        # line segment
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
        
        # edge label
        etext_x.append((x0+x1)/2)
        etext_y.append((y0+y1)/2)    
        
        if edge[0] == artist:
            etext_colors.append('palegreen')
            edge_text.append(\
    f'{edge[0]} ⟷ {edge[1]}: <b>{round(similar_artists[artist][inds[edge[1]]]["score"]/1e5,1)}</b>')
            
        else: # logic can be improved with better schema for similar_artists
            
            etext_colors.append('lemonchiffon') 
            if edge[0] in similar_artists.keys() and edge[1] in similar_artists.keys():
                if edge[1] in [val['name'] for val in similar_artists[edge[0]]]:
                    key = 0
                else:
                    key = 1
            elif edge[0] in similar_artists.keys():
                key = 0
            else:
                key = 1
            other = 1 if key == 0 else 0

            inds2 = {val['name']:i for i,val in enumerate(similar_artists[edge[key]])}
            edge_text.append(\
    f'{edge[0]} ⟷ {edge[1]}: <b>{round(similar_artists[edge[key]][inds2[edge[other]]]["score"]/1e5,1)}</b>')
    
    # edge lines
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='slategrey'),
        mode='lines')
    # edge labels
    eweights_trace = go.Scatter(x=etext_x,y= etext_y, text=edge_text, 
                                mode='markers', hoverinfo='text',
                                marker=dict(size=5,color=etext_colors))
    
    # Nodes
    colors = []
    for val in list(G.nodes):
        if val == artist:
            colors.append('limegreen')
        else:
            colors.append('lightseagreen' if val in \
                          similar_artists.keys() else 'deeppink')
        
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y, text = [f'<b>{val}</b>' for val in list(G.nodes)],
        mode='markers+text',
        textfont = dict(size=16, color=colors),
        hoverinfo='text', # textposition='middle left',
        marker=dict(
            color=colors,
            symbol='line-ew', 
            line_width=0))
    
    # list main match scores on bottom of graph, title contains other info
    figtext = ' | '.join([f"<a href='{val['link']}'>{val['name']}</a>: <b>{round(val['score']/1e5,1)}</b>"\
                          for val in similar_artists[artist]])
    
    fig = go.Figure(data=[edge_trace, node_trace, eweights_trace],
             layout=go.Layout(
                title=f'<b>{artist.title()} [{len(G.nodes)}]</b> | {layout.lower()} network graph {"with neighbors" if add_neighbors else "without neighbors"}',
                titlefont_size=16,
                titlefont_color='moccasin',
                paper_bgcolor = 'slategrey',
                plot_bgcolor = 'black',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=5,l=5,r=5,t=35),
                annotations=[ dict(
                    text=figtext,
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=0.005 )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            )
                    )
    
    return fig