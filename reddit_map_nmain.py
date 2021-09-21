import praw
import pandas as pd
from timeit import timeit
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go

sub_of_interest = 'FemaleDatingStrategy'
hard_limit = 12

# ===== Instantiate Reddit instance =====
reddit = praw.Reddit(
    client_id='FE5apSBviVjlEQ',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    username='mrkillercow',
    password='S4nh4k1mi99e',
    user_agent='1'
)

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


def get_post_dataframe(subreddit=sub_of_interest, limit=6):

    post_users = get_posters(subreddit, limit)

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

    # === Define network map variables as dataframe ===
    # -- Value counts of posts --
    df_counts_p = pd.DataFrame()
    df_counts_p['target'] = subreddit_posted.count()
    df_counts_p['weight'] = df['subs_posted'].value_counts().values

    df_counts_p = df_counts_p.astype(
        {
            'target': 'category',
            'weight': 'int64'
        }
    )

def get_comm_activity(subreddit=sub_of_interest, limit=6):

    comm_users = get_commentors(subreddit, limit)

    commentors = [
        comm.name
        for comm in comm_users
        for c in comm.comments.new(limit=limit)
        if c.subreddit != sub_of_interest
    ]

    subreddit_commented = [
        c.subreddit.display_name
        for user in comm_users
        for c in user.comments.new(limit=limit)
        if c.subreddit != sub_of_interest
    ]

    output_dict = {
        "commentor": commentors,
        "subs_commented": subreddit_commented
    }

    return output_dict


def main():


    comments_dict = get_comm_activity(sub_of_interest, 6)

    # === Create pandas dataframe from the dictionaries ===
    df_posts = pd.DataFrame.from_dict(posts_dict)
    df_comments = pd.DataFrame.from_dict(comments_dict)

    print('----- Raw data -----')
    print(df_posts, '\n')
    print(df_comments)

    # === Define network map variables as dataframe ===
    # -- Value counts of posts --
    df_counts_p = pd.DataFrame()
    df_counts_p['target'] = df_posts['subs_posted'].value_counts().index
    df_counts_p['weight'] = df_posts['subs_posted'].value_counts().values

    df_counts_p = df_counts_p.astype(
        {
            'target': 'category',
            'weight': 'int64'
        }
    )

    print("----- Value count (post) data -----\n", df_counts_p, '\n')

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

    print("----- Value count (comment) data -----\n", df_counts_c, '\n')

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


if __name__ == "__main__":
    main()
