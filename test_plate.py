from reddit_network_functions import *
import pandas as pd

df = pd.read_csv("reddit_network.csv")

print(df.head())

subs = df.target.unique()

for s in subs:
    print(reddit.subreddit(s).over18)