import json
import time
from typing import Generator

import requests
from typing_extensions import Literal

type_property_map = {
    "videos": "videoRenderer",
    "streams": "videoRenderer",
    "shorts": "reelItemRenderer"
}

def get_search(
    query: str,
    mode : str,
    limit: int = None,
    sleep: int = 0.5,
     sort_by: Literal["relevance", "upload_date", "view_count", "rating"] = "upload_date",
    results_type: Literal["video", "channel", "playlist", "movie"] = "video",
) -> Generator[dict, None, None]:

    results_type_map = {
        "video": ["B", "videoRenderer"],
        "channel": ["C", "channelRenderer"],
        "playlist": ["D", "playlistRenderer"],
        "movie": ["E", "videoRenderer"],
    }
    sort_by_map = {
        "relevance": "A",
        "upload_date": "I",
        "view_count": "M",
        "rating": "E",
    }

    if mode == 'H' or  mode == 'h':
        url = f"https://www.youtube.com/results?search_query={query}&sp=CAASBAgBEAE%253D"
    elif mode == 'D' or  mode == 'd':
        url = f"https://www.youtube.com/results?search_query={query}&sp=CAISBAgCEAE%253D"
    elif mode == 'W' or  mode == 'w':
        url = f"https://www.youtube.com/results?search_query={query}&sp=CAISBAgDEAE%253D"
    elif mode == 'M' or  mode == 'm':
        url = f"https://www.youtube.com/results?search_query={query}&sp=CAISBAgEEAE%253D"
    elif mode == 'Y' or  mode == 'y':
        url = f"https://www.youtube.com/results?search_query={query}&sp=CAISBAgFEAE%253D"
    else:
        param_string = f"CA{sort_by_map[sort_by]}SAhA{results_type_map[results_type][0]}"
        url = f"https://www.youtube.com/results?search_query={query}&sp={param_string}"
    api_endpoint = "https://www.youtube.com/youtubei/v1/search"
    videos = get_videos(
        url, api_endpoint, results_type_map[results_type][1], limit, sleep
    )
    for video in videos:
        yield video



def get_video(
    id: str,
) -> dict:

    """Get a single video.

    Parameters:
        id (``str``):
            The video id from the video you want to get.
    """

    session = get_session()
    url = f"https://www.youtube.com/watch?v={id}"
    html = get_initial_data(session, url)
    client = json.loads(
        get_json_from_html(html, "INNERTUBE_CONTEXT", 2, '"}},') + '"}}'
    )["client"]
    session.headers["X-YouTube-Client-Name"] = "1"
    session.headers["X-YouTube-Client-Version"] = client["clientVersion"]
    data = json.loads(
        get_json_from_html(html, "var ytInitialData = ", 0, "};") + "}"
    )
    return next(search_dict(data, "videoPrimaryInfoRenderer"))



def get_videos(
    url: str, api_endpoint: str, selector: str, limit: int, sleep: int, sort_by: str = None
) -> Generator[dict, None, None]:
    session = get_session()
    is_first = True
    quit_it = False
    count = 0
    while True:
        if is_first:
            html = get_initial_data(session, url)
            client = json.loads(
                get_json_from_html(html, "INNERTUBE_CONTEXT", 2, '"}},') + '"}}'
            )["client"]
            api_key = get_json_from_html(html, "innertubeApiKey", 3)
            session.headers["X-YouTube-Client-Name"] = "1"
            session.headers["X-YouTube-Client-Version"] = client["clientVersion"]
            data = json.loads(
                get_json_from_html(html, "var ytInitialData = ", 0, "};") + "}"
            )
            next_data = get_next_data(data, sort_by)
            is_first = False
            if sort_by and sort_by != "newest": 
                continue
        else:
            data = get_ajax_data(session, api_endpoint, api_key, next_data, client)
            next_data = get_next_data(data)
        for result in get_videos_items(data, selector):
            try:
                count += 1
                yield result
                if count == limit:
                    quit_it = True
                    break
            except GeneratorExit:
                quit_it = True
                break

        if not next_data or quit_it:
            break

        time.sleep(sleep)

    session.close()


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    session.headers["Accept-Language"] = "en"
    return session

def get_initial_data(session: requests.Session, url: str) -> str:
    session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
    response = session.get(url, params={"ucbcb":1})

    html = response.text
    return html


def get_ajax_data(
    session: requests.Session,
    api_endpoint: str,
    api_key: str,
    next_data: dict,
    client: dict,
) -> dict:
    data = {
        "context": {"clickTracking": next_data["click_params"], "client": client},
        "continuation": next_data["token"],
    }
    response = session.post(api_endpoint, params={"key": api_key}, json=data)
    return response.json()


def get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(stop, pos_begin)
    return html[pos_begin:pos_end]


def get_next_data(data: dict, sort_by: str = None) -> dict:
    # Youtube, please don't change the order of these
    sort_by_map = {
        "newest": 0, 
        "popular": 1,
        "oldest": 2, 
    }
    if sort_by and sort_by != "newest":
        endpoint = next(
            search_dict(data, "feedFilterChipBarRenderer"), None)["contents"][sort_by_map[sort_by]]["chipCloudChipRenderer"]["navigationEndpoint"]
    else:
        endpoint = next(search_dict(data, "continuationEndpoint"), None)
    if not endpoint:
        return None
    next_data = {
        "token": endpoint["continuationCommand"]["token"],
        "click_params": {"clickTrackingParams": endpoint["clickTrackingParams"]},
    }

    return next_data


def search_dict(partial: dict, search_key: str) -> Generator[dict, None, None]:
    stack = [partial]
    while stack:
        current_item = stack.pop(0)
        if isinstance(current_item, dict):
            for key, value in current_item.items():
                if key == search_key:
                    yield value
                else:
                    stack.append(value)
        elif isinstance(current_item, list):
            for value in current_item:
                stack.append(value)


def get_videos_items(data: dict, selector: str) -> Generator[dict, None, None]:
    return search_dict(data, selector)
