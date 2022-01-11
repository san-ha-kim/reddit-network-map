import praw
from prawcore.exceptions import Forbidden

sub_of_interest = "aww"

def get_users(sub=sub_of_interest, post_count=8, comment_count=12):
    """
    Finds the most recently active users in a subreddit. It's easier to comment than to post on a subreddit, so more comments are collected.
    :param subreddit: subreddit to crawl
    :param posts_count: number of posts to search for
    :param comments_count: number of comments to search for
    :return: List of usernames who were recently active in a subreddit
    """
    # === Obtain list of posters and commentors ===
    posters = []
    
    try:
        for s in reddit.subreddit(sub).new(limit=post_count):
            if s.author.name != "AutoModerator":
                posters.append(s.author.name)
            elif type(s.author.name) == None:
                pass
    except Forbidden:
        print("Tried to access Forbidden")
        #pass
    
    """posters = [
        s.author.name                                         #<- Redditor who posted
        for s in reddit.subreddit(sub).new(limit=post_count)  #<- from most recent posts
        if s.author.name != "AutoModerator"                   #<- remove auto moderator
    ]"""
    
    
    commentors = [] 
    
    try: 
        # --- Same with commentors ---
        for c in reddit.subreddit(sub).comments(limit=comment_count):
            if c.author.name != "AutoModerator":
                commentors.append(c.author.name)
            elif type(c.author.name) == None:
                pass
    except Forbidden:
        print("Tried to access Forbidden")
        #pass
    """
    commenters = [
        c.author.name
        for c in reddit.subreddit(sub).comments(limit=comment_count)  
        if c.author.name != "AutoModerator"
    ]"""
    
    # === Combine the posters and commentors ===
    redditors = posters + commentors    
    # --- Remove duplicates
    unique_redditors = list(set(redditors))
    
    return unique_redditors

def get_redditor_activity(subreddit, post_count=8, comment_count=12, filter_soi=True):
    """
    Get names of subreddits to which users have posted to.
    :param redditor_list: list of redditor usernames
    :param lim: number of posts to limit to; default 12
    """
    
    # === Define lists to store subreddits where redditor has posted and commented to ===
    posts_subreddits = []
    comments_subreddits = []
    
    # === 
    # Iterate over list of redditors and store the names of the subreddits where they posted and store 
    # them in the list to a certain length 
    # ===
    
    redditor_list = get_users(subreddit, post_count, comment_count)
    
    # -- Iterate over list of redditors --
    for r in redditor_list:

        posts = reddit.redditor(r).submissions.new(limit=post_count) #<- new submissions from redditors
        comments = reddit.redditor(r).comments.new(limit=comment_count)
        
        try:        
            # - Iterate over posts/submissions -
            for submission in posts:
                # Skip if they posted in the subreddit that we're scraping, otherwise store to list
                if submission.subreddit.display_name == sub_of_interest:
                    if filter_soi is True:
                        pass
                    else:
                        posts_subreddits.append(
                            {
                                "source": subreddit,
                                "target": submission.subreddit.display_name,
                                "type": "submission",
                                'weight': 3
                            }
                        )

                elif submission.subreddit.display_name != sub_of_interest:
                    posts_subreddits.append(
                        {
                            "source": subreddit,
                            "target": submission.subreddit.display_name,
                            "type": "submission",
                            'weight': 3                        
                        }
                    )

            for comment in comments:
                if comment.subreddit.display_name == sub_of_interest:
                    if filter_soi is True:
                        pass
                    else:
                        comments_subreddits.append(
                                {
                                    "source": subreddit,
                                    "target": comment.subreddit.display_name,
                                    "type": "comment",
                                    'weight': 1
                                }
                        )
                elif comment.subreddit.display_name != sub_of_interest:
                        comments_subreddits.append(
                            {
                                "source": subreddit,
                                "target": comment.subreddit.display_name,
                                "type": "comment",
                                'weight': 1
                            }
                        )
        except Forbidden:
            print("Forbidden")
            pass
    
    #activity_list = posts_subreddits + comments_subreddits
    
    return posts_subreddits + comments_subreddits


def remove_self_loops(dataframe, column_1, column_2):
    
    mask = dataframe.apply(lambda x: x[column_1] in x[column_2], axis=1)
    
    df = dataframe[~mask]
    
    return df