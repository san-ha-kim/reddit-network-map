import praw
import numpy as np
import pandas as pd

sub_of_interest = 'TwoXChromosomes'
num = 7

# ===== Instantiate Reddit instance =====
reddit = praw.Reddit(
    client_id='FE5apSBviVjlEQ',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    username='mrkillercow',
    password='S4nh4k1mi99e',
    user_agent='1'
)


def get_posts(num=300, sub='conspiracy'):
    """
    This function retrieves a certain number of posts from a specified Subreddit,
    using specified sorts (e.g. hot, top, new). It returns the post ID, poster's username, post time, number of up/down
    votes.
    :return: Hot posts of specified subreddit
    """

    sub = reddit.subreddit(sub)

    hot = sub.new(limit=num)

    return hot


r = get_posts(num=5, sub=sub_of_interest)

# --- Obtain the most active posters of a subreddit ---
users = [s.author for s in r if not s.stickied]

# --- Iterate over the users to see each user's most recent posts ---
author = []
subreddit_posted = []
subreddit_commented = []
is_OP = []

for user in users:
    # -- New posts made by the author --
    posts_ = user.submissions.new(limit=num)
    # -- New comments made by the author ---
    comments_ = user.comments.new(limit=num)

    # -- Iterate over the posts to find the subreddit on which the redditor posted on --
    for p, c in zip(posts_, comments_):
        #print(user.name, p.id, c.submission.id)
        print(20 * '-')

        if p.id == c.submission.id:
            is_OP.append(True)
        else:
            is_OP.append(False)

        submission = reddit.submission(id=p.id).subreddit

        # - Append the relevant data -
        subreddit_commented.append(c.subreddit)  # comment subreddit
        author.append(user)  # author
        subreddit_posted.append(submission.display_name)  # post subreddit

dataframe_dict = {
    "original_author": author,  # author obtained from subreddit of interest
    "submitted_to": subreddit_posted,  # name of subreddit the author posted to (can be NaN)
    "commented_to": subreddit_commented,  # name of subreddit the author commented on (only top-level comment)
    "commented_is_OP": is_OP,  # checks if the redditor of the commented post and the author are the same
}

reddit_network_dataframe = pd.DataFrame.from_dict(
    dataframe_dict,
    orient='index'
).transpose()

# print(reddit_network_dataframe)

rn_df = reddit_network_dataframe[reddit_network_dataframe.commented_is_OP == False]

print(rn_df)

