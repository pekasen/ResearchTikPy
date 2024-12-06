"""ResearchTikPy - A Python package for TikTok Research API.

This module contains functions to fetch data from the TikTok Research API.
The functions are designed to fetch data for multiple users or videos at once
and compile them into a single DataFrame for further analysis.
"""

import time
from datetime import datetime
from time import sleep

from loguru import logger
import pandas as pd
import requests

from researchtikpy import endpoints
from researchtikpy.query_lang import Condition, Query, as_dict
from researchtikpy.utils import validate_access_token_object

# pylint: disable=too-many-arguments, too-many-locals, too-many-positional-arguments


def get_users_info(
    usernames,
    access_token,
    fields="display_name,bio_description,avatar_url,is_verified,"
           "follower_count,following_count,likes_count,video_count",
    verbose=True,
):
    """
    Fetches user information for a list of usernames.

    Parameters
    ----------
    usernames (list):
        List of TikTok usernames to fetch info for.
    access_token (str):
        Access token for TikTok's API.
    fields (str):
        Comma-separated string of user fields to retrieve.
    verbose (bool):
        If True, prints detailed logs; if False, suppresses most print statements.

    Returns
    -------
    pd.DataFrame
        DataFrame containing user information.
    """
    endpoint = endpoints.user_info
    headers = {
        "Authorization": f"Bearer {validate_access_token_object(access_token)}",
        "Content-Type": "application/json",
    }
    users_data = []
    session = requests.Session()  # Use session for improved performance

    for username in usernames:
        query_body = {"username": username}
        params = {"fields": fields}
        response = session.post(
            endpoint, headers=headers, json=query_body, params=params
        )

        if verbose:
            print(f"Fetching info for user: {username}")

        if response.status_code == 200:
            user_data = response.json().get("data", {})
            if user_data:  # Check if data is not empty
                users_data.append(user_data)
            else:
                if verbose:
                    print(f"No data found for user: {username}")
        else:
            if verbose:
                print(
                    f"Error for user {username}: {response.status_code}",
                    response.json(),
                )
            users_data.append(
                {"username": username, "error": "Failed to retrieve data"}
            )

    users_df = pd.DataFrame(users_data)

    if verbose:
        print("User info retrieval complete.")

    return users_df


def get_liked_videos(
    usernames,
    access_token,
    fields="id,video_description,create_time,username,like_count,"
           "comment_count,share_count,view_count,hashtag_names",
    max_count=100,
    verbose=True,
):
    """
    Fetch liked videos for multiple usernames and compile them into a single DataFrame.

    Parameters
    ----------
    usernames : list
        List of usernames to fetch liked videos for.
    access_token : str
        Access token for TikTok's API.
    fields : str, optional
        Comma-separated string of fields to retrieve for each liked video
        (default is "id,video_description,create_time,username,like_count,
        comment_count,share_count,view_count,hashtag_names").
    max_count : int, optional
        Maximum number of liked videos to retrieve per request (default is 100).
    verbose : bool, optional
        If True, prints detailed logs; if False, suppresses most print statements (default is True).

    Returns
    -------
    pd.DataFrame
        DataFrame containing all liked videos from the provided usernames.
    """
    endpoint = endpoints.liked_videos
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    liked_videos_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for username in usernames:
        has_more = True
        cursor = 0  # Start with initial cursor at 0

        while has_more:
            query_body = {
                "username": username,
                "max_count": max_count,
                "cursor": cursor,
            }
            response = session.post(
                f"{endpoint}?fields={fields}", headers=headers, json=query_body
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                user_liked_videos = data.get("user_liked_videos", [])

                if user_liked_videos:
                    current_df = pd.DataFrame(user_liked_videos)
                    liked_videos_df = pd.concat(
                        [liked_videos_df, current_df], ignore_index=True
                    )
                    if verbose:
                        print(
                            f"Successfully fetched {len(user_liked_videos)}"
                            f"liked videos for user {username}"
                        )
                else:
                    if verbose:
                        print(f"No liked videos found for user {username}")

                has_more = data.get("has_more", False)
                cursor = data.get(
                    "cursor", cursor + max_count
                )  # Use API provided cursor if available, else increment
            elif response.status_code == 403:
                if verbose:
                    print(
                        f"Access denied: User {username} has not enabled collecting liked videos."
                    )
                break  # Exit the loop for the current username if access is denied
            elif response.status_code == 429:
                if verbose:
                    print("Rate limit exceeded. Pausing before retrying...")
                sleep(60)  # Pause execution before retrying
                continue  # Optional: retry the last request
            else:
                if verbose:
                    print(
                        f"Error fetching liked videos for user {username}: {response.status_code}",
                        response.json(),
                    )
                break  # Stop fetching for current user in case of an error

    return liked_videos_df


def get_videos_info(
    usernames,
    access_token,
    start_date,
    end_date,
    max_count=100,
    verbose=True,
    total_max_count=1000,
    rate_limit_pause=60,
):
    """
    Fetches video information for given usernames within the specified date range.

    Parameters
    ----------
    usernames : list
        List of usernames to fetch videos for.
    access_token : str
        Authorization token for TikTok Research API.
    start_date : str
        Start date for the video search (format YYYYMMDD).
    end_date : str
        End date for the video search (format YYYYMMDD).
    max_count : int, optional
        Maximum number of videos to return per request (default is 100).
    verbose : bool, optional
        If True, prints detailed logs; if False, suppresses most print statements.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the video information.
    """

    query = {
            "and": [
            {
                "operation": "IN",
                "field_name": "username",
                "field_values": usernames,
            }
        ]
    }

    if verbose:
        print(
            f"Querying videos for {', '.join(usernames)} from "
            f"{start_date} to "
            f"{end_date}"
        )
    get_videos_query(
        query=query,
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        total_max_count=total_max_count,
        max_count=max_count,
        rate_limit_pause=rate_limit_pause,
    )


def get_videos_hashtag(
    hashtags,
    access_token,
    start_date,
    end_date,
    total_max_count,
    region_code=None,
    music_id=None,
    effect_id=None,
    max_count=100,
    rate_limit_pause=60,
):
    """
    Searches for videos by hashtag with optional filters for region code,
    music ID, or effect ID, and includes rate limit handling. All available
    fields are retrieved by default, queries are segmented if the range between
    start_date and end_date exceeds 30 days.

    Parameters
    ----------
    hashtags : list
        A list of hashtags to search for.
    access_token : str
        Your valid access token for the TikTok Research API.
    start_date : str
        The start date for the search (format YYYYMMDD).
    end_date : str
        The end date for the search (format YYYYMMDD).
    total_max_count : int
        The total maximum number of videos to collect.
    region_code : str, optional
        The region code to filter videos by.
    music_id : str, optional
        The music ID to filter videos by.
    effect_id : str, optional
        The effect ID to filter videos by.
    max_count : int, optional
        The maximum number of videos to return per request (up to 100).
    rate_limit_pause : int, optional
        Time in seconds to wait when a rate limit error is encountered.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the videos that match the given criteria.
    """
    query: dict = _create_query(hashtags, region_code, music_id, effect_id)
    return get_videos_query(
        query=query,
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        total_max_count=total_max_count,
        max_count=max_count,
        rate_limit_pause=rate_limit_pause,
    )


def _create_query(
    hashtags: list[str], region_code: str, music_id: str, effect_id: str
) -> dict:
    and_conditions = [
        Condition(operation="IN", field_name="hashtag_name", field_values=hashtags)
    ]
    if region_code:
        and_conditions.append(
            Condition(
                operation="EQ",
                field_name="region_code",
                field_values=[region_code],
            )
        )
    if music_id:
        and_conditions.append(
            Condition(operation="EQ", field_name="music_id", field_values= [music_id])
        )
    if effect_id:
        and_conditions.append(
            {"operation": "EQ", "field_name": "effect_id", "field_values": [effect_id]}
        )
    query = Query(and_conditions, [], [])

    return query


def get_videos_query(
    query: dict,
    access_token: str,
    start_date: str,
    end_date: str,
    total_max_count: int,
    max_count=100,
    rate_limit_pause=60,
) -> pd.DataFrame:
    """
    Like get_videos_hashtag(), but you can pass a custom `query` object
    For the `query` parameter, see the TikTok API documentation:
    https://developers.tiktok.com/doc/research-api-specs-query-videos/
    For the rest of parameters, see get_videos_hashtag()
    """
    query = Query(**query) if isinstance(query, dict) else query
    fields = (
        "id,video_description,create_time,region_code,share_count,view_count,like_count,"
        "comment_count,music_id,hashtag_names,username,effect_ids,playlist_id,voice_to_text"
    )
    endpoint = endpoints.query
    url_with_fields = f"{endpoint}?fields={fields}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {validate_access_token_object(access_token)}",
    }
    start_date_dt = datetime.strptime(start_date, "%Y%m%d")
    end_date_dt = datetime.strptime(end_date, "%Y%m%d")
    collected_videos = []
    has_more = True
    params = {
        "query": as_dict(query),
        "start_date": start_date_dt.strftime("%Y%m%d"),
        "end_date": end_date_dt.strftime("%Y%m%d"),
        "max_count": max_count,
    }

    while has_more is True and len(collected_videos) < total_max_count:

        logger.debug(f"Requesting POST: {url_with_fields } with params: {params}")

        response = requests.post(
            url_with_fields,
            headers=headers,
            json=params,
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json().get("data", {})
            videos = data.get("videos", [])
            collected_videos.extend(videos)
            if data.get("has_more", False) is True:
                has_more = data.get("has_more", False)
                if "cursor" in data:
                    params["cursor"] = data.get("cursor")
                    params["search_id"] = data.get("search_id")
            else:
                break
        elif response.status_code == 429:
            print("Rate limit exceeded. Pausing before retrying...")
            time.sleep(rate_limit_pause)
        else:
            raise ValueError(f"status_code={response.status_code}. {response.json()}")

    return pd.DataFrame(collected_videos)


def get_video_comments(
    videos_df,
    access_token,
    fields="id,video_id,text,like_count,reply_count, create_time, parent_comment_id",
    max_count=100,
    verbose=True,
):
    """
    Fetch comments for multiple videos and compile them into a single DataFrame.

    Parameters
    ----------
    videos_df : pd.DataFrame
        DataFrame with a column 'id' containing video IDs.
    access_token : str
        Access token for TikTok's API.
    fields : str, optional
        Comma-separated string of fields to retrieve for each comment.
        Defaults to a basic set of fields.
    max_count : int, optional
        Maximum number of comments to retrieve per request (default is 100).
    verbose : bool, optional
        If True (default), prints detailed logs; if False, suppresses most print statements.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all comments from the provided videos.
    """
    endpoint = endpoints.comments
    headers = {
        "Authorization": f"Bearer {validate_access_token_object(access_token)}",
        "Content-Type": "application/json",
    }
    all_comments_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for _, video in videos_df.iterrows():
        video_id = video["id"]
        has_more = True
        cursor = 0

        while has_more and cursor < 1000:  # To respect the API's limit
            body_params = {
                "video_id": video_id,
                "max_count": max_count,
                "cursor": cursor,
            }
            response = session.post(
                f"{endpoint}?fields={fields}", headers=headers, json=body_params
            )

            if verbose:
                print(f"Fetching comments for video {video_id} with cursor at {cursor}")

            if response.status_code == 200:
                data = response.json().get("data", {})
                comments = data.get("comments", [])

                if comments:
                    comments_df = pd.DataFrame(comments)
                    comments_df["video_id"] = (
                        video_id  # Add the video_id to each comment
                    )
                    all_comments_df = pd.concat(
                        [all_comments_df, comments_df], ignore_index=True
                    )

                has_more = data.get("has_more", False)
                cursor += max_count  # Increment cursor based on max_count
            elif response.status_code == 429:
                if verbose:
                    print("Rate limit exceeded. Pausing before retrying...")
                sleep(30)  # Pause execution before retrying
            else:
                if verbose:
                    print(
                        f"Error fetching comments for video {video_id}:"
                        f"{response.status_code}",
                        response.json(),
                    )
                break  # Stop the loop in case of an error

    return all_comments_df


def get_pinned_videos(
    usernames,
    access_token,
    fields="id,video_description,create_time,username,"
           "like_count,comment_count,share_count,view_count,hashtag_names",
    verbose=True,
):
    """
    Fetches pinned videos for multiple usernames and compiles them into a single DataFrame.

    Parameters
    ----------
    usernames (list):
        List of usernames to fetch pinned videos for.
    access_token (str):
        Access token for TikTok's API.
    fields (str):
        Comma-separated string of fields to retrieve for each pinned video.
    verbose (bool):
        If True, print additional logging information.

    Returns
    -------
    pd.DataFrame:
        DataFrame containing all pinned videos from the provided usernames.
    """
    endpoint = endpoints.pinned_videos
    headers = {
        "Authorization": f"Bearer {validate_access_token_object(access_token)}",
        "Content-Type": "application/json",
    }
    pinned_videos_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for username in usernames:
        query_body = {"username": username}
        response = session.post(
            f"{endpoint}?fields={fields}", headers=headers, json=query_body
        )

        if response.status_code == 200:
            data = response.json().get("data", {})
            pinned_videos = data.get("pinned_videos_list", [])

            if pinned_videos:
                temp_df = pd.DataFrame(pinned_videos)
                temp_df["username"] = username  # Include username for clarity
                pinned_videos_df = pd.concat(
                    [pinned_videos_df, temp_df], ignore_index=True
                )
                if verbose:
                    print(
                        f"Successfully fetched {len(pinned_videos)}"
                        f"pinned videos for user {username}"
                    )
            else:
                if verbose:
                    print(f"No pinned videos found for user {username}")
        else:
            if verbose:
                print(
                    f"Error fetching pinned videos for user {username}: {response.status_code}"
                )
                try:
                    print(response.json())
                except ValueError:  # handles the JSONDecodeError for non-JSON responses
                    print("No valid JSON response available.")

    return pinned_videos_df


def get_followers(
    usernames_list, access_token, max_count=100, total_count=None, verbose=True
):
    """
    Fetch followers for multiple users and compile them into a single DataFrame.

    It is advised to keep the list of usernames short to avoid longer runtimes.

    Parameters
    ----------
    usernames_list : list
        List of usernames to fetch followers for.
    access_token : str
        Access token for TikTok's API.
    max_count : int, optional
        Maximum number of followers to retrieve per request (default is 100).
    total_count : int, optional
        Maximum total number of followers to retrieve per user.
    verbose : bool, optional
        If True, prints detailed logs; if False, suppresses most print statements.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all followers from the provided usernames.

    Note
    ----
    You might encounter a varying number of followers fetched per request.
    This is due to how TikTok's API handles pagination and possibly how it 
    limits data per request. As you approach the total limit of followers you
    want to fetch (total_count), the API might return fewer followers per
    request,especially if the remaining number to reach the total is less than
    your specified max_count. This is normal behavior for APIs when handling
    paginated results close to the limit of a dataset. It however unnecessarily
    uses your daily quota faster than it should.
    We'll have to optimize that in the future.
    """
    all_followers_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance
    endpoint = endpoints.followers

    for username in usernames_list:
        followers_list = []
        cursor = 0  # Initialize cursor for pagination
        has_more = True
        retrieved_count = 0  # Track the count of retrieved followers
        effective_max_count = max_count  # Reset max_count for each user

        while has_more and (total_count is None or retrieved_count < total_count):
            # Adjust max_count based on remaining followers needed
            if total_count is not None:
                effective_max_count = min(max_count, total_count - retrieved_count)

            headers = {
                "Authorization": f"Bearer {validate_access_token_object(access_token)}",
                "Content-Type": "application/json",
            }
            query_body = {
                "username": username,
                "max_count": effective_max_count,
                "cursor": cursor,
            }

            response = session.post(endpoint, headers=headers, json=query_body)

            if response.status_code == 200:
                data = response.json().get("data", {})
                followers = data.get("user_followers", [])
                followers_list.extend(followers)
                retrieved_count += len(followers)
                has_more = data.get("has_more", False)
                cursor = data.get(
                    "cursor", cursor + effective_max_count
                )  # Update cursor based on response
                if verbose:
                    print(
                        f"Retrieved {len(followers)} followers for user"
                        f"{username} (total retrieved: {retrieved_count})"
                    )
            elif response.status_code == 429:
                if verbose:
                    print(
                        "Rate limit exceeded fetching followers"
                        f"for user {username}. Pausing before retrying..."
                    )
                sleep(
                    60
                )  # Adjust sleep time based on the API's rate limit reset window
                continue  # Continue to the next iteration without breaking the loop
            else:
                if verbose:
                    print(
                        f"Error fetching followers for user {username}: {response.status_code}",
                        response.json(),
                    )
                break  # Stop the loop for the current user

        if followers_list:
            followers_df = pd.DataFrame(followers_list)
            followers_df["target_account"] = (
                username  # Identify the account these followers belong to
            )
            all_followers_df = pd.concat(
                [all_followers_df, followers_df], ignore_index=True
            )

    return all_followers_df


def get_following(usernames_list, access_token, max_count=100, verbose=True):
    """
    Fetch accounts that a user follows. Each username in the list is used
    to fetch accounts they follow.

    Parameters
    ----------
    usernames_list : list
        List of usernames to fetch followed accounts for.
    access_token : str
        Access token for TikTok's API.
    max_count : int, optional
        Maximum number of followed accounts to retrieve per request
        (default is 100).
    verbose : bool, optional
        If True, prints detailed logs; if False, suppresses most
        print statements.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all followed accounts from the provided usernames.
    """
    all_following_df = pd.DataFrame()
    session = requests.Session()  # Use session for improved performance

    for username in usernames_list:
        following_list = []
        cursor = 0  # Initialize cursor for pagination
        has_more = True

        while has_more:
            endpoint = endpoints.followings
            headers = {
                "Authorization": f"Bearer {validate_access_token_object(access_token)}",
                "Content-Type": "application/json",
            }
            query_body = {
                "username": username,
                "max_count": max_count,
                "cursor": cursor,
            }

            response = session.post(endpoint, headers=headers, json=query_body)

            if response.status_code == 200:
                data = response.json().get("data", {})
                following = data.get("user_following", [])
                following_list.extend(following)
                has_more = data.get("has_more", False)
                cursor = data.get(
                    "cursor", cursor + max_count
                )  # Update cursor based on response
                if verbose:
                    print(f"Retrieved {len(following)}"
                          f"accounts for user {username}")
            elif response.status_code == 429:
                if verbose:
                    print(
                        "Rate limit exceeded fetching following for"
                        f"user {username}. Pausing before retrying..."
                    )
                sleep(
                    60
                )  # Adjust sleep time based on the API's rate limit reset window
                continue  # Continue to the next iteration without breaking the loop
            else:
                if verbose:
                    print(
                        f"Error fetching following for user {username}: {response.status_code}",
                        response.json(),
                    )
                break  # Stop the loop for the current user

        if following_list:
            following_df = pd.DataFrame(following_list)
            following_df["target_account"] = (
                username  # Identify the account these followings belong to
            )
            all_following_df = pd.concat(
                [all_following_df, following_df], ignore_index=True
            )

    return all_following_df
