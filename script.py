import json
import os
import time

from dotenv import load_dotenv

import connect

load_dotenv()

AGENT_NAME = f"personal-bot/0.1 by {os.environ['REDDIT_USERNAME']}"
BASE_URL = "https://oauth.reddit.com"
USER = os.environ["REDDIT_USERNAME"]


def get_ids_from_response(response):
    keep = [
        "id",
        "permalink",
        "score",
        "created_utc",
        "subreddit",
    ]
    info_list = list()
    children = response.json().get("data", {}).get("children", [])
    for child in children:
        info = {k: child.get("data")[k] for k in keep}
        post_id = info["permalink"].split("/")[4]
        age_seconds = int(time.time()) - info["created_utc"]

        # Keep certain posts/comments if they match criteria.
        if (
            info["subreddit"] in FILTERS["exclude_subreddits"]
            or info["id"] in FILTERS["exclude_post_ids"]
            or info["id"] in FILTERS["exclude_comment_ids"]
            # keep comments for posts which are kept.
            or post_id in FILTERS["exclude_post_ids"]
            or (
                FILTERS["exclude_score_above"] is not None
                and info["score"] > FILTERS["exclude_score_above"]
            )
            or (
                FILTERS["exclude_older_than"] is not None
                and age_seconds > FILTERS["exclude_older_than"]
            )
            or (
                FILTERS["exclude_younger_than"] is not None
                and age_seconds < FILTERS["exclude_younger_than"]
            )
        ):
            print("skip", info)
            continue
        else:
            info_list.append(info["id"])

    return info_list


def get_comments_and_posts(user):
    """This retrieves comments AND posts."""
    params = {
        "limit": 100,
    }
    url = f"{BASE_URL}/user/{user}"
    response = conn.get_request(url=url, params=params, headers=conn.headers)
    return get_ids_from_response(response)


def editusertext(thing_id, new_text="deleted", is_post=False):
    data = {
        "thing_id": f"t3_{thing_id}" if is_post else f"t1_{thing_id}",
        "text": new_text,
    }
    url = f"{BASE_URL}/api/editusertext"
    print(f"EDIT: {thing_id=}")
    conn.post_request(url=url, data=data, headers=conn.headers)


def editusertexts(thing_ids, is_post=False):
    for thing_id in thing_ids:
        editusertext(thing_id=thing_id, is_post=is_post)


def delete_thing_id(thing_id, is_post=False):
    data = {
        "id": f"t3_{thing_id}" if is_post else f"t1_{thing_id}",
    }
    url = f"{BASE_URL}/api/del"
    print(f"DELETE: {thing_id=}")
    conn.post_request(url=url, data=data, headers=conn.headers)


def delete_thing_ids(thing_ids, is_post=False):
    for thing_id in thing_ids:
        delete_thing_id(thing_id=thing_id, is_post=is_post)


def get_posts(user):
    url = f"{BASE_URL}/user/{user}/submitted"
    response = conn.get_request(url=url, headers=conn.headers)
    return get_ids_from_response(response)


def main():
    post_ids = get_posts(user=USER)
    while post_ids:
        editusertexts(post_ids, is_post=True)
        delete_thing_ids(post_ids, is_post=True)
        post_ids = get_posts(user=USER)

    comment_ids = get_comments_and_posts(user=USER)
    while comment_ids:
        editusertexts(comment_ids)
        delete_thing_ids(comment_ids)
        comment_ids = get_comments_and_posts(user=USER)


if __name__ == "__main__":
    conn = connect.Connection()

    # Keep certain posts/comments by defining filters.
    with open("filters.json", "r") as f:
        FILTERS = json.load(f)

    main()
