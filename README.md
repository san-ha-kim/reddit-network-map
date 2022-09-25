# Network map of Reddit: who visits where?
## Introduction
### What is Reddit?
Reddit is a social networking site (SNS) that is somewhat different from more popular SNS such as Facebook, Instagram, Snapchat, etc. On Reddit, users (known as redditors) enter into smaller communities (known as subreddits) onto which submissions (or posts) are made, which include pictures, text posts (much like a common forum), links to other websites (such as YouTube, news outlets etc.), or videos. It is closer to a forum more so than Facebook or Twitter, in that users usually choose which subreddit to subscribe to.

The subreddits are formed based on a specific theme. This theme can be as generic as r/worldnews, which is a subreddit about news around the world; r/pics which is a subreddit where users simply submit whatever pictures they'd like; the theme of a subreddit can be geographical (e.g. r/Italy, r/Boston), around hobbies (e.g. r/gaming, r/leagueoflegends), even meta-ironic commentary of redditors' behaviors (e.g. r/gamingcirclejerk). Simply, a Reddit is a host of vast subreddits, which can be just about anything.

Reddit's ability to create new subreddits by anyone has let some subreddits with unsavory themes, such as [misogyny, rape and others](https://www.newsweek.com/reddit-bans-men-going-their-own-way-forums-violating-hate-speech-rules-1616379). Reddit's administrative team has taken efforts to ban such subreddits, but with more than [400 million monthly users, and 1 billion visits](https://www.statista.com/topics/5672/reddit/), Reddit admin team simply cannot ban and police redditors' ability to create harmful subreddits.

### (Social) Network Analysis

Network analysis (NA) is a technique often employed in social sciences to depict interaction among entities (e.g. individuals, corporates, cliques). NA depicts how individual entities are connected with each other, allowing visualization and analysis of networks such as the flow of information, power, diseases, money, or memes. The whole topic of network theory is out of my expertise, so I will stop the discussion here.

### Network Analysis of Reddit: where do redditors visit?

In this project, a small network analysis will be done to see which subreddits are popular to redditors who visit particular subreddits, and how these subreddits are connected as a network.

## Motivation
Curiosity drove this project. There are many subreddits, and I was curious to see what kind of other subreddits the redditors of the particular subreddits would dwell.

## Dependency
- Python Reddit API Wrapper (PRAW)
- Pandas
- PyVis
- NetworkX

## How it works

### 1. Designate the subreddit of interest and find the most recent comments and posts
Anyone can post (provided they follow the rules of the subreddit) and comment on any post. First step is the specify which subreddit to scrape over, and to find users who have recently posted and/or commented.

### 2. Find recent posts and comments made by the obtained user list
Next, find to which subreddits the users have commented and posted to, and calculate how often.

### 3. Visualize
Define the nodes and edges to visualize the network, with the subreddit of interest at its center.
