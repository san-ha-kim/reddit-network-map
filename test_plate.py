import praw

# ===== Instantiate Reddit instance =====
reddit = praw.Reddit(
    client_id='FE5apSBviVjlEQ',
    client_secret='4lOv7xDgIn-XzFBmyFeBB8REpkTQzQ',
    username='mrkillercow',
    password='S4nh4k1mi99e',
    user_agent='1'
)

sub_of_interest = 'FiftyFifty'

num = 2

# --- Retrieve non-stickied posts ---
sticky_count = 0
sub = reddit.subreddit(sub_of_interest)

s = []

# -- Check for stickied posts --
for sticky in sub.new(limit=num):
    if sticky.stickied:
        s.append(sticky)
        print("Pinned post ID: {}".format(sticky))

for submission in sub.hot(limit=num+len(s)):
    if not submission.stickied:
        print(submission)