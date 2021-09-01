import praw
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from bokeh.io import show, save
from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Blues8, Reds8, Purples8, Oranges8, Viridis8, Spectral8
from bokeh.transform import linear_cmap

sub_of_interest = 'FemaleDatingStrategy'
hard_limit = 6

# ===== Instantiate Reddit instance =====
reddit = praw.Reddit(
    client_id='FE5apSBviVjlEQ',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    username='mrkillercow',
    password='S4nh4k1mi99e',
    user_agent='1'
)

# === Obtain the most active posters of a subreddit ===


def get_post_activity(subreddit, n_posts):
    """

    Retrieves new submissions made on a specified subreddit to obtain user activity information across subreddits,
    by obtaining which subreddits a user has posted and commented to.

    :param subreddit: specific subreddit to base the search on
    :param n_posts: number of posts to retrieve
    :return: lists of usernames and subreddit names
    """
    users = [s.author for s in reddit.subreddit(subreddit).new(limit=n_posts)]

    for u in users:
        print(u.name)
        print(20 * '=')

    def get_poster_names():
        """
        Retrieves new submissions made by redditors made elsewhere other than the specified subreddit
        :return: List of usernames
        """
        posters = [
            poster.name
            for poster in users
            for p in poster.submissions.new(limit=n_posts)
            # Discount posts in the same subreddit as the posts
            if reddit.submission(id=p.id).subreddit.display_name != sub_of_interest
        ]

        print("Recent posters:", posters)

        return posters

    def get_commentor_names():
        """
        Retrieves new comments made by redditors commented in subs other than specified subreddit
        :return: List of usernames
        """
        commentors = [
            commentor.name
            for commentor in users
            for c in commentor.comments.new(limit=n_posts)
            if c.subreddit != sub_of_interest
        ]

        print("Recent commentors:", commentors)

        return commentors

    def get_post_subs():
        """
        Retrieves new posts made by redditors, and which subreddit it was posted on.
        :return: List of subreddit names
        """
        subreddit_posted = [
            reddit.submission(id=p.id).subreddit.display_name
            for user in users
            for p in user.submissions.new(limit=n_posts)
            if reddit.submission(id=p.id).subreddit.display_name != sub_of_interest
        ]

        print("User posted to:", subreddit_posted)

        return subreddit_posted

    def get_comment_subs():
        """
        Retrieves new comments made by redditors, and which subreddit it was commented on.
        :return: List of subreddit names
        """
        subreddit_commented = [
            c.subreddit.display_name
            for user in users
            for c in user.comments.new(limit=n_posts)
            if c.subreddit != sub_of_interest
        ]

        print("User commented to:", subreddit_commented)

        return subreddit_commented

    return get_poster_names(), get_commentor_names(), get_post_subs(), get_comment_subs()


def get_comment_activity():
    """
    
    """
    


author, commentor, posts, comments = get_post_activity(sub_of_interest, hard_limit)

# === Create dictionaries to create the dataframe with ===
posts_dict = {
    "post_author": author,  # author obtained from subreddit of interest
    "target_post": posts,  # name of subreddit the author posted to (can be NaN)
}

comments_dict = {
    "comment_author": commentor,
    "target_comment": comments
}

# === Create pandas dataframe from the dictionaries ===
df_posts = pd.DataFrame(
    data={k: pd.Series(v) for k, v in posts_dict.items()}
)

df_comments = pd.DataFrame(
    data={k: pd.Series(v) for k, v in comments_dict.items()}
)

print('----- Raw data ----- \n', df_posts, '\n----------\n', df_comments)

# === Define network map variables as dataframe ===
# -- Value counts of posts --
df_counts_p = pd.DataFrame()
# df_counts_p['source'] = [sub_of_interest for i in range(len(df_posts.value_counts()))]
df_counts_p['target'] = df_posts['target_post'].value_counts().index
df_counts_p['weight'] = df_posts['target_post'].value_counts().values

df_counts_p = df_counts_p.astype(
    {
        'target': 'category',
        'weight': 'int64'
    }
)

print("----- Value count (post) data -----\n", df_counts_p, '\n')

# -- Value counts of comments --
df_counts_c = pd.DataFrame()
df_counts_c['target'] = df_comments['target_comment'].value_counts().index
df_counts_c['weight'] = df_comments['target_comment'].value_counts().values

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
    suffixes=['_p', '_c']
).fillna(0)

df_nx['weight_total'] = df_nx['weight_p'] + df_nx['weight_c']
df_nx['source'] = [sub_of_interest for i in range(len(df_nx))]

# -- Drop unnecessary columns --
df_nx.drop(['weight_p', 'weight_c'], axis=1, inplace=True)
df_nx.sort_values(by='weight_total', inplace=True)

# Examine the dataframe
print('----- Map data ----- \n', df_nx, '\n')

# - Send to Excel for quick view -
# df_nx.to_excel('df_nx.xlsx')

# === Instantiate the graph object for network map ===
G = nx.from_pandas_edgelist(
    df_nx,
    'source', 'target', ['weight_total'],
    create_using=nx.MultiDiGraph()
)

# === Define the parameters for graph object ===
# - Choose a title! -
title = '{} subreddit activity map'.format(sub_of_interest)

# - Establish which categories will appear when hovering over each node -
HOVER_TOOLTIPS = [("Subreddit", "@index")]

# Create a plot — set dimensions, toolbar, and title
plot = figure(tooltips=HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
              x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

# Create a network graph object with spring layout
# https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

# Set node size and color
network_graph.node_renderer.glyph = Circle(size=15, fill_color='skyblue')

# Set edge opacity and width
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

# Add network graph to the plot
plot.renderers.append(network_graph)

show(plot)
