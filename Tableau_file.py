#!/user/bin/env
import Gephi_to_dataframe as gd
import pandas as pd
import os

def stack_user_edges(user_edges, src, tgt):
    """
    """
    user_edges["key"] = [x+1 for x in range(user_edges.shape[0])] # add key for building network in Tableau
    user_edges_cp = user_edges.copy()
    user_edges_cp[[src, tgt]] = user_edges[[tgt, src]]
    appended_df = user_edges.append(user_edges_cp)
    return appended_df

def merge_nodes_edges(gephi_df, appended_df, gephi_df_key, appended_df_key):
    return gephi_df.merge(appended_df, left_on = gephi_df_key, right_on = appended_df_key, how = "inner")


if __name__ == "__main__":
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    edge_path = os.path.join(__location__, "dataset/user_edges.csv")
    # read user_edges file
    user_edges = pd.read_csv(edge_path)
    gephi_path = os.path.join(__location__, "dataset/network_gephi.gexf")
    # read the processed gexf file into dataframe
    coord_df = gd.gexf_to_dataframe(gephi_path, label_name_dtype = "numeric")

    # process to data to make it Tableau ready
    append_df = stack_user_edges(user_edges, "_id", "followers")
    df_tableau_ready = merge_nodes_edges(coord_df, append_df, "node_id", "_id")

    # save df_tableau_ready for opening it in Tableau
    # df_tableau_ready.to_csv("df_tableau_ready.csv", index = False)

    # read the df_tableau_ready.csv into Tableau, and plot network based on the steps in readme.md