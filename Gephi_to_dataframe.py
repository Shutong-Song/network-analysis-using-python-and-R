#! /usr/bin/env
import pandas as pd # version 1.2.1
import os
import numpy as np # version 1.19.4
import networkx as nx #version 2.5
import matplotlib.pyplot as plt #version 3.3.3

# manipulate large network in Gephi:
    #1. read source data .csv file into a dataframe (for example, name it as user_edges_df)
    #2. save it as a xxx.gexf file using dataframe_to_gexf() function
    #3. manipulate network in Gephi application with the layout you desired, and save that to a xxx1.gexf file
    #4. convert the xxx1.gexf file to a dataframe with all coordinates (X, Y) of nodes extracted
    #5. plot the network using networkx with the coordinates using network_plot() function

def dataframe_to_gexf(user_edges_df, src, tgt):
    """
    convert dataframe to Gephi file
    input: an edges dataframe with columns: src(the source node), tgt(the target node)
    output: a "network.gexf" will be save into your current working directory
    """
    G = nx.convert_matrix.from_pandas_edgelist(user_edges_df, source = src, target = tgt)
    nx.write_gexf(G, "network.gexf")

def gexf_to_dataframe(gephi_path, label_name_dtype = "str"):
    """
    extract label, value, x-axis position, y-axis position from a xxx.gexf file
    input: the Gephi file path from dataframe_to_gexf() function
    output: a dataframe extracted from xxx.gexf file with four columns: node_id (label), node_degree (value), X, Y
    """
    g = pd.read_csv(gephi_path)

    # start to extract columns from xxx.gexf file
    # depends on the columns you have when read into Gephi, you can add more columns here to extract similar way
    #label_name = g[g.columns.values[0]].str.extract(r'label="(.+?)"')
    #node_degree = g[g.columns.values[0]].str.extract(r'value="(.+?)"')
    #X = g[g.columns.values[0]].str.extract(r'x="(.+?)"')
    #Y = g[g.columns.values[0]].str.extract(r'y="(.+?)"')


    ## process the extracted columns
    #node_degree = node_degree[1:].append([np.nan],ignore_index=True)
    #X = X[2:].append([np.nan, np.nan], ignore_index=True)
    #Y = Y[2:].append([np.nan, np.nan], ignore_index=True)

    ## concatenates all extracted columns into dataframe
    #df = pd.concat([label_name, node_degree, X, Y], axis=1)
    #df.dropna(axis=0, how="any", inplace=True)
    #df.columns = ["node_id", "node_degree", "X", "Y"]
    #df.drop_duplicates(inplace=True)

    ## start to extract columns from xxx.gexf file
    ## depends on the columns you have when read into Gephi, you can add more columns here to extract similar way
    label_name = g[g.columns.values[0]].str.extract(r'label="(.+?)"')
    node_degree = g[g.columns.values[0]].str.extract(r'value="(.+?)"')
    X = g[g.columns.values[0]].str.extract(r'x="(.+?)"')
    Y = g[g.columns.values[0]].str.extract(r'y="(.+?)"')

    ## process the extracted columns
    node_degree = node_degree[1:].append([np.nan],ignore_index=True)
    X = X[2:].append([np.nan, np.nan], ignore_index=True)
    Y = Y[2:].append([np.nan, np.nan], ignore_index=True)

    ## concatenates all extracted columns into dataframe
    df = pd.concat([label_name, node_degree, X, Y], axis=1)
    df.dropna(axis=0, how="any", inplace=True)
    df.columns = ["node_id", "node_degree", "X", "Y"]
    df.drop_duplicates(inplace=True)

    ## convert columns data types to numeric because they are string when extracted using regular expression
    cvt_dtype_cols = ["node_degree", "X", "Y"]
    cvt_dtype_types = [np.float64, np.float64, np.float64]
    df = df.astype(dict(zip(cvt_dtype_cols, cvt_dtype_types)))
    if label_name_dtype == "numeric": #if label is numeric, it convert is to numeric, otherwise stay in string type
        df.loc[:, "node_id"] = df.loc[:,"node_id"].astype(np.float64)
    return df


def network_plot(user_edges_df, src, tgt, gephi_df):
    """
    plot the network based on their coordinates
    input: the dataframe user_edges_df with at least two columns: src, tgt, a nodes dataframe with coordinates (gephi_df)
    output: a network graph
    """
    G = nx.convert_matrix.from_pandas_edgelist(user_edges_df, source = src, target = tgt)

    # prepare nodes attributes to G from coords_df
    # 1. set "pos" as nodes coordinates attributes
    node_attrs = {ids:{"pos":(x, y)} for ids, (x, y) in zip(gephi_df.node_id.values.astype(np.int32).tolist(),
                                           zip(gephi_df.X.values.astype(np.float64).tolist(), gephi_df.Y.values.astype(np.float64).tolist()))}
    # 2. if you have degree set from Gephi application, you can set degree attribute
    for ids, node_degree in zip(gephi_df.node_id.values.astype(np.int32).tolist(),
                                 gephi_df.node_degree.values.astype(np.float64).tolist()):
        node_attrs[ids]["degree"] = node_degree
    
    # set node attributes to graph G
    nx.set_node_attributes(G, node_attrs)

    # plot network
    # 1. set nodes color based on nodes degree, depends on your minimum and maximum node degree,
    #    you can set the range based on your needs here: 15, 25 is just a test number, 
    #    you can even set more ranges than 3, and change the color set based on matplotlib color sets
    color_map = []
    for node in list(G.degree):
        if node[1] < 15:
            color_map.append("cornflowerblue")
        elif node[1] >= 15 and node[1] < 25:
            color_map.append("cyan")
        else:
            color_map.append("orange")
    
    # 2. get coordinates
    coords = {user_id:(x, y) for user_id, (x, y) in nx.get_node_attributes(G, "pos").items()}
    fig, ax = plt.subplots(figsize = (20, 20))

    # 3. get degree
    dg = dict(G.degree)

    # 4. plot
    nx.draw(G, coords, with_labels = False, node_size = [v*20 for v in dg.values()], node_color = color_map)
    plt.show()

if __name__ == "__main__":
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    edge_path = os.path.join(__location__, "dataset/user_edges.csv")
    user_edges_df = pd.read_csv(edge_path)
    dataframe_to_gexf(user_edges_df, "_id", "followers")
    gephi_path = os.path.join(__location__, "dataset/network_gephi.gexf")
    coord_df = gexf_to_dataframe(gephi_path)
    network_plot(user_edges_df, "_id", "followers", coord_df)
    

