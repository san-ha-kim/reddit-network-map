import praw
from prawcore.exceptions import Forbidden
import numpy as np
import pandas as pd
from pyvis.network import Network
import networkx as nx
import matplotlib.pyplot as plt
from decouple import config

sub_of_interest = "TwoXChromosomes"

username = config('USER')
pw = config()

reddit = praw.Reddit(
    username='mrkillercow',
    password='S4nh4k1mi99e',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    client_id='FE5apSBviVjlEQ',
    user_agent='network_map'
)

print(reddit.user.me())
# === Obtain the most active posters of a subreddit ===


def get_posters(subreddit=sub_of_interest, posts_count=6):
    """
    Retrieves a list of redditors who have recently posted on a subreddit
    :param subreddit: subreddit to crawl
    :param posts_count: number of posts to crawl
    :return: List of usernames who have recently posted
    """

    users = []

    for s in reddit.subreddit(subreddit).new(limit=posts_count):
        print(s.author)
        print(25*"=")
        users.append(s.author)

    return users


def get_commentors(subreddit=sub_of_interest, comments_count=30):
    """
    Retrieves a list of redditors who have recently commented on a subreddit
    :param subreddit: subreddit to crawl
    :param comments_count: number of comments to crawl
    :return: List of usernames who have recently commented
    """

    users = []

    for s in reddit.subreddit(subreddit).comments(limit=comments_count):
        print(s.author)
        print(25*"~")
        users.append(s.author)

    return users


def get_post_activity(subreddit=sub_of_interest, user_lim=6, limit=12):
    """
    Obtain post activity based on where the redditor posted to.
    :param subreddit: Subreddit to crawl over
    :param user_lim: limit on how many users to call
    :param limit: number of posts to crawl
    :return: DataFrame of post destination
    """
    post_users = get_posters(subreddit, user_lim)

    # --- Redditor name who posted to subs that's not sub of interest ---
    posters = [
        poster.name
        for poster in post_users
        for p in poster.submissions.new(limit=limit)
        if reddit.submission(id=p.id).subreddit.display_name != subreddit
    ]

    # --- Names of subreddit to which the redditor posted to
    subreddit_posted = [
        reddit.submission(id=p.id).subreddit.display_name
        for poster in post_users
        for p in poster.submissions.new(limit=limit)
        if reddit.submission(id=p.id).subreddit.display_name != sub_of_interest
    ]

    # --- Generate dataframe of the extracted information
    df = pd.DataFrame(
        data={
            'author': posters,
            'subs_posted': subreddit_posted
        }
    )

    # --- Create another dataframe to define the activity scores --
    df_counts_p = pd.DataFrame()
    df_counts_p['target'] = df['subs_posted'].value_counts().index
    df_counts_p['weight'] = df['subs_posted'].value_counts().values

    df_counts_p = df_counts_p.astype(
        {
            'target': 'category',
            'weight': 'int64'
        }
    )

    return df_counts_p


def get_comm_activity(subreddit=sub_of_interest, user_lim=6, limit=12):
    """
    Obtains where redditors have commented to
    :param subreddit: subreddit to crawl over
    :param user_lim: limit on how many users to call
    :param limit: limit on number of comments
    :return: DataFrame of author and comment destination subreddit.
    """
    comm_users = get_commentors(subreddit, user_lim)

    # === List of commentor usernames ===
    commentors = [
        comm.name
        for comm in comm_users
        for c in comm.comments.new(limit=limit)
        if c.subreddit != sub_of_interest
    ]

    # === List of where the commentors commented to ===
    subreddit_commented = [
        c.subreddit.display_name
        for user in comm_users
        for c in user.comments.new(limit=limit)
        if c.subreddit != sub_of_interest
    ]

    # === Arrange in dictionary ===
    output_dict = {
        "commentor": commentors,
        "subs_commented": subreddit_commented
    }

    # === Make dataframe ===
    df_comments = pd.DataFrame.from_dict(output_dict)

    # -- Value counts of comments --
    df_counts_c = pd.DataFrame()
    df_counts_c['target'] = df_comments['subs_commented'].value_counts().index
    df_counts_c['weight'] = df_comments['subs_commented'].value_counts().values

    df_counts_c = df_counts_c.astype(
        {
            'target': 'category',
            'weight': 'int64'
        }
    )

    return df_counts_c


def main():
    df_counts_p = get_post_activity(sub_of_interest, user_lim=3, limit=hard_limit)
    df_counts_c = get_comm_activity(sub_of_interest, user_lim=3, limit=hard_limit)

    print(df_counts_p)
    print(df_counts_c)
    """
    # --- Merge the count dataframes together to aid in summing the submissions and comments activity, to be used
    # for network mapping ---
    df_nx = df_counts_p.merge(
        df_counts_c,
        how='outer',
        on='target',
        suffixes=('_p', '_c')
    ).fillna(0)

    df_nx['weight_total'] = df_nx['weight_p'] + df_nx['weight_c']
    df_nx['source'] = [sub_of_interest for i in range(len(df_nx))]

    # -- Drop unnecessary columns --
    df_nx.drop(['weight_p', 'weight_c'], axis=1, inplace=True)
    df_nx.sort_values(by='weight_total', inplace=True, ascending=False)

    # Examine the dataframe
    print('----- Map data ----- \n', df_nx, '\n')

    edge_tuples = [(sub_of_interest, sub, w) for w, sub in zip(df_nx['weight_total'], df_nx['target'])]

    node_list = df_nx['target'].tolist()
    node_list = node_list + [sub_of_interest]

    nx = Network()

    nx.add_nodes(node_list, label=node_list)

    nx.add_edges(edge_tuples)

    nx.show("nodes.html")"""


if __name__ == "__main__":
    main()
