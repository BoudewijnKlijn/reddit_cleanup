# Reddit Cleanup

This script removes all your Reddit posts and comments. 

Optionally keep items based on:
- time
- upvotes
- subreddit
- id


## Instructions

1. Install packages using `uv` or `pip`.
1. Register your personal Reddit app
    - [Reddit](https://ssl.reddit.com/prefs/apps/)
        - choose a name (not important)
        - choose a redirect URI (not important as long as Reddit accepts it) 
        - create the app and write down the `client secret`
1. Modify environment variables
    - rename `.env_example` to `.env`
    - replace values in `.env` with your real values
1. Optionally set filters in `filters.json` to keep items.
1. Run script: `script.py`
    - This may take a while depending on how many posts and comments you have. Reddit only allows for 60 requests per minute.


## Resources

- https://www.reddit.com/wiki/api
- https://www.reddit.com/dev/api
