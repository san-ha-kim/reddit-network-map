import praw
import numpy as np
import pandas as pd
import networkx as nx

sub_of_interest = 'TwoXChromosomes'
num = 5

# ===== Instantiate Reddit instance =====
reddit = praw.Reddit(
    client_id='FE5apSBviVjlEQ',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    username='mrkillercow',
    password='S4nh4k1mi99e',
    user_agent='1'
)


def get_posts(num_posts=300, sub='conspiracy'):
    """
    This function retrieves a certain number of posts from a specified Subreddit,
    using specified sorts (e.g. hot, top, new). It returns the post ID, poster's username, post time, number of up/down
    votes.
    :return: Hot posts of specified subreddit
    """

    sub = reddit.subreddit(sub)

    new = sub.new(limit=num_posts)

    return new


r = get_posts(num_posts=5, sub=sub_of_interest)

# === Obtain the most active posters of a subreddit ===
users = [s.author for s in r if not s.stickied]

# === Iterate over the users to see each user's most recent posts ===
author = []
subreddit_posted = []
subreddit_commented = []

for user in users:
    # -- New posts made by the author --
    posts_ = user.submissions.new(limit=num)
    # -- New comments made by the author ---
    comments_ = user.comments.new(limit=num)

    # -- Iterate over the posts to find the subreddit on which the redditor posted on --
    for p, c in zip(posts_, comments_):
        print("Redditor: {} \nPost ID: {} \nComment post ID: {}\n"\
              .format(user.name, p.id, c.submission.id), 20*'=')
        """
        if p.id == c.submission.id:
            is_OP.append(True)
        else:
            is_OP.append(False)
        """
        submission = reddit.submission(id=p.id).subreddit

        # - Append data about author activity -
        if not submission.display_name == sub_of_interest: # do not include data if post/comment is same as sub of
                                                           # interest.

            # Append name of subreddit where author posted
            subreddit_posted.append(submission.display_name)
            # Append name of subreddit where author commented
            subreddit_commented.append(c.subreddit)
            # Append author username
            author.append(user)

# === Create dictionary to create the dataframe with ===
dataframe_dict = {
    "original_author": author,  # author obtained from subreddit of interest
    "submitted_to": subreddit_posted,  # name of subreddit the author posted to (can be NaN)
    "commented_to": subreddit_commented,  # name of subreddit the author commented on (only top-level comment)
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

# === Count unique subreddits in posted and commented to's ===
rn_submits_count = pd.Series(rn_df['submitted_to'].value_counts())
rn_comments_count = pd.Series(rn_df['commented_to'].value_counts())
#rn_submits_cat = pd.Series(rn_df['submitted_to'].unique())
#rn_comments_cat = pd.Series(rn_df['commented_to'].unique())


# === Define network map variables ===
nodes = list(rn_submits_count.index)
weights = list(rn_submits_count.values)

print(weights)
