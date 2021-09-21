import praw

# ===== Instantiate Reddit instance =====
reddit = praw.Reddit(
    client_id='FE5apSBviVjlEQ',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    username='mrkillercow',
    password='S4nh4k1mi99e',
    user_agent='1'
)

subreddit = 'FemaleDatingStrategy'
hard_limit = 6

users = [s.author for s in reddit.subreddit(subreddit).comments(limit=hard_limit)]

print(users)