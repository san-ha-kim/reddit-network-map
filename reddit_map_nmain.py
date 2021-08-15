import praw
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

sub_of_interest = 'FemaleDatingStrategy'
num = 6

# ===== Instantiate Reddit instance =====
reddit = praw.Reddit(
    client_id='FE5apSBviVjlEQ',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    username='mrkillercow',
    password='S4nh4k1mi99e',
    user_agent='1'
)


def get_posts(sub, num_posts=3):
    """
    This function retrieves a certain number of posts from a specified Subreddit,
    using specified sorts (e.g. hot, top, new). It returns the post ID, poster's username, post time, number of up/down
    votes.
    :return: Hot posts of specified subreddit
    """

    sub = reddit.subreddit(sub)

    new = sub.new(limit=num_posts)

    return new


r = get_posts(sub_of_interest, num_posts=6)


# === Obtain the most active posters of a subreddit ===

# === Iterate over the users to see each user's most recent posts ===
def get_activity(subreddit_posts, n):
    """
    Get the posts and comments of each redditor from a subreddit and return a list of the author name,
    name of subreddit where they posted and commented to as list.
    :param subreddit_posts: posts from specified subreddit
    :param n: number of posts to retrieve
    :return: three lists: name of author, subreddit name to which author posted to, subreddit name to which author
    commented to
    """

    # --- Retrieve redditor usernames from posts not stickied in subreddit ---
    users = [s.author for s in subreddit_posts if not s.stickied]

    for user in users:
        print(user.name)
        print(25*'=')

    def get_author_names():
        # -- User names of the author --
        usernames = [author.name for author in users]

        return usernames

    def get_post_names():
        # -- New posts made by the author --
        subreddit_posted = [
            reddit.submission(id=p.id).subreddit.display_name
            for user in users
            for p in user.submissions.new(limit=n)
            if reddit.submission(id=p.id).subreddit.display_name != sub_of_interest
        ]

        print(subreddit_posted)

        return subreddit_posted

    def get_comment_subs():
        # -- New comments made by the author --
        subreddit_commented = [
            c.subreddit
            for user in users
            for c in user.submissions.new(limit=n)
            if c.subreddit != sub_of_interest
        ]

        print(subreddit_commented)

        return subreddit_commented

    return get_author_names(), get_post_names(), get_comment_subs()


redditor, posts, comments = get_activity(r, num)

# === Create dictionary to create the dataframe with ===
dataframe_dict = {
    "original_author": redditor,  # author obtained from subreddit of interest
    "submitted_to": posts,  # name of subreddit the author posted to (can be NaN)
    "commented_to": comments,  # name of subreddit the author commented on (only top-level comment)
}

# === Create pandas dataframe from the dictionary ===
reddit_network_df = pd.DataFrame(
    data={k: pd.Series(v) for k, v in dataframe_dict.items()}
)

# == Change datatype properly ==
rn_df = reddit_network_df.astype(
    {
        'original_author': 'string',
        "submitted_to": "category",
        "commented_to": 'category',
    }
)

print('----- Raw data ----- \n', reddit_network_df, '\n')

# === Define network map variables ===
# --- Summarise the posts and comments by counts into different lists ---
nodes_posts = rn_df['submitted_to'].value_counts().index.tolist()
weights_posts = rn_df['submitted_to'].value_counts().values.tolist()

print("length list:{}\nlength counts:{}".format(len(nodes_posts), len(weights_posts)))

nodes_comments = rn_df['commented_to'].value_counts().index.tolist()
weights_comments = rn_df['commented_to'].value_counts().values.tolist()

print("nodes_posts before: {}".format(nodes_posts))

for i, v in enumerate(nodes_comments):
    if nodes_comments[i] == nodes_posts[i]:
        weights_posts[i] += weights_comments[i]
    else:
        nodes_posts.append(nodes_comments[i].display_name)
        weights_posts.append(weights_comments[i])

print("nodes_posts after: {}".format(nodes_posts))

# --- Dictionary to hold map information ---
nodes_dict = {
    "source": [sub_of_interest for i in range(len(nodes_posts))],
    "posts_to": nodes_posts,
    "weights": weights_posts
}

df_posts = pd.DataFrame(
    nodes_dict
)

print('----- Map data ----- \n', df_posts, '\n')

# === Draw network map ===
G = nx.from_pandas_edgelist(
    df_posts,
    'source', 'posts_to', ['weights'],
    create_using=nx.MultiDiGraph()
)

nx.draw_networkx(G)

plt.show()
