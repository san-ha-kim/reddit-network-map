import praw
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


r = get_posts(sub_of_interest, num_posts=num)


# === Obtain the most active posters of a subreddit ===
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

    def get_poster_names():
        # -- User names of the author --
        poster = [
            author.name
            for author in users
            for p in author.submissions.new(limit=n)
            if reddit.submission(id=p.id).subreddit.display_name != sub_of_interest
        ]

        for user in users:
            print(user.name)
            print(25*'=')

        return poster

    def get_commentor_names():
        # -- User names of the commentor --
        commentor = [
            author.name
            for author in users
            for c in author.comments.new(limit=n)
            if c.subreddit != sub_of_interest
        ]

        return commentor

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
            for c in user.comments.new(limit=n)
            if c.subreddit != sub_of_interest
        ]

        print(subreddit_commented)

        return subreddit_commented

    return get_poster_names(), get_commentor_names(), get_post_names(), get_comment_subs()


author, commentor, posts, comments = get_activity(r, num)

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
#df_counts_p['source'] = [sub_of_interest for i in range(len(df_posts.value_counts()))]
df_counts_p['target'] = df_posts['target_post'].value_counts().index
df_counts_p['weight'] = df_posts['target_post'].value_counts().values

df_counts_p = df_counts_p.astype(
    {
        'target': 'category',
        'weight': 'int64'
    }
)

print("----- Value count (post) data -----\n", df_counts_p,'\n')

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

print("----- Value count (comment) data -----\n", df_counts_c,'\n')

# - View information of dataframes -
print(df_counts_p.info())
print(df_counts_c.info())

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

# Examine the dataframe
print('----- Map data ----- \n', df_nx, '\n')

# - Send to Excel for quick view -
df_nx.to_excel('df_nx.xlsx')

# === Instantiate the graph object for network map ===
G = nx.from_pandas_edgelist(
    df_nx,
    'source', 'target', ['weight_total'],
    create_using=nx.MultiDiGraph()
)
# === Define the parameters for graph object ===
nx.draw_networkx(G)

plt.show()
