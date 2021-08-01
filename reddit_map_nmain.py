import praw
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ===== Create class object for users =====

"""class RedditDev:
    def __init__(self):
        # --- User ID and PW of the developer/admin ---
        self.user_name = "username_admin"
        self.password = "pw"
        

#class RedditUser:

# ===== Create class object for posts =====
#class RedditSub:"""

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

    hot = sub.hot(limit=num)

    return hot


r = get_posts(num=5, sub='TwoXChromosomes')

# --- Obtain the most active posters of a subreddit ---
users = [s.author for s in r if not s.stickied]

# --- Iterate over the users to see each user's most recent posts ---
for user in users:
    posts = user.submissions.new(limit=7)

    for p in posts:
        print(user)
        print(reddit.submission(id=p).subreddit)
        print(20*'-')

