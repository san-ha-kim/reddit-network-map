
from reddit_network_functions import *
import pandas as pd
from pyvis.network import Network

soi = "MensRights"

def main(sub_of_interest=soi):
    
    # ========================================================
    # <<< 1) Obtain the most active posters of a subreddit >>>
    # ========================================================
    primary_activity = get_redditor_activity(sub_of_interest, post_count=7, comment_count=10, filter_soi=True)
    print(primary_activity[:5])
    print(f"Total length: {len(primary_activity)}")
    
    # ================================================
    # 2) Organize into dataframe and remove self-loops
    # ================================================
    df_primary = pd.DataFrame(
    data=primary_activity
    )    
    
    # ==========================================================================================
    # 3) Iterate over the primary source to see other subreddits where users post and comment to
    # ==========================================================================================
    df_secondary = pd.DataFrame()

    primary_target = list(df_primary.target.unique())

    for subreddit in primary_target:
        secondary_activity = get_redditor_activity(subreddit, post_count=2, comment_count=5, filter_soi=False)

        df_secondary = df_secondary.append(secondary_activity, ignore_index=True)
            
    # ==================================================================
    # 4) Merge primary and secondary dataframes into one large dataframe
    # ==================================================================
    df = pd.concat([df_primary, df_secondary], ignore_index=True)
    
    # === Remove self-loops ===
    df = remove_self_loops(df, 'source', 'target')

    # =====================================
    # 5) Determine the weights of each edge
    # =====================================
    
    # dictionary to determine the aggregation method
    d = {'weight':'sum', 'type': 'first'}
    
    # determine edge weight using .groupby() method and aforementioned dictionary
    df = df.groupby(
        ['source','target'], 
        sort=False, 
        as_index=False
    ).agg(d).reindex(columns=df.columns)
    
    df = df.astype(
        {
            'source':'category',
            'target':'category',
            'type':'category',
            'weight':'int64'
        }
    )
    
    print(df.info())
    
    # save as CSV for later analysis
    
    df.to_csv("reddit_network.csv", mode="a", header=False, index=False)
    
    # =================================================================
    # 6) Specify source and target for network visualization with PyVis
    # =================================================================
    
    # find unique source and target subreddits
    s = df.source.unique().tolist()
    t = df.target.unique().tolist()
    n = list(set(s+t))
    
    # find number of subscribers in the subreddits
    members = [reddit.subreddit(m).subscribers for m in n]
    
    # find if subreddit is NSFW    
    nsfw = [reddit.subreddit(sub).over18 for sub in n]
    nsfw_color = []
    
    for sub in nsfw:
        if sub is True:
            nsfw_color.append("#ff00cc")
        else:
            nsfw_color.append("#d9d9d9")            

    # convert subreddit names into numeric labels
    nodes = {v: k for k, v in enumerate(n)}

    # add new column
    df['source_num'] = df['source'].map(nodes)
    df['target_num'] = df['target'].map(nodes)
    
    # define nodes, labels and edge lists 
    node_list = list(nodes.values())
    node_labels = list(nodes.keys())
    edge_list = [(source, target, weight) for source, target, weight in zip(df.source_num, df.target_num, df.weight)]
    
    nx_pv = Network("1000px", "1000px")

    nx_pv.add_nodes(node_list, label=node_labels, value=members, color=nsfw_color)

    nx_pv.add_edges(edge_list)
    nx_pv.set_options("""
        var options = {
            "physics": {
                "barnesHut": {
                    "gravitationalConstant": -12450,
                    "centralGravity": 1.2,
                    "springLength": 165,
                    "springConstant": 0.025,
                    "damping": 0.33,
                    "avoidOverlap": 0.72
                },
            "minVelocity": 0.75
            }
        }
    """)
    #nx_pv.show_buttons(filter_=['physics'])
    nx_pv.save_graph(f"reddit_map_{sub_of_interest}.html")


if __name__ == "__main__":
    main()
