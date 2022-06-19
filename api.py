import json
import re
from time import sleep

import requests

import AnimeEpisode
from config import bangumiTagSearch, bangumiSearch
from utils import parse_bangumi_tag, parse_num

request_head = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
}

# 请求重试次数
_RETRY_NUM = 3


def _post(url, data):
    retry = _RETRY_NUM
    while retry > 0:
        try:
            return requests.post(url=url, data=data, headers=request_head)
        except ConnectionError:
            retry = retry - 1
            sleep(2)

    return None


def get_bangumi_search_tags(anime: AnimeEpisode):
    """
    获取萌番组搜索时用的tags
    :param anime:
    :return:
    """
    tags = []
    if anime.bangumi_tag:
        tags.append(anime.bangumi_tag)
        if anime.language:
            tags.append(parse_bangumi_tag(anime.language))
        if anime.team:
            tags.append(anime.team)
    else:
        data = json.dumps({
            "name": anime.name,
            "keyword": True,
            "multi": True
        })
        res = _post(bangumiTagSearch, data)
        if not res:
            return None
        res = json.loads(res.content)
        if res['success'] and res["found"]:
            tags.append(res['tag'][0]['_id'])
            if anime.language:
                tags.append(parse_bangumi_tag(anime.language))
            if anime.team:
                tags.append(anime.team)

    return tags


def bangumi_search(tag_id, episode: int, page: int = 1):
    """
    从萌番组搜索目标种子
    默认按种子数排序

    :param tag_id:  搜索参数
    :param episode: 查找集数
    :param page:    多页搜索用的页数
    :return:
    """
    result = {"magnet": None, "torrent": None}
    data = json.dumps({
        "tag_id": tag_id,
        "p": page
    })
    sleep(1)
    res = _post(bangumiSearch, data)
    if not res:
        return None
    res = json.loads(res.content)
    torrents = res["torrents"]

    def get_seeders(o):
        return o["seeders"]

    torrents.sort(key=get_seeders, reverse=True)
    for t in res["torrents"]:
        if re.search("(\[{}\])|(【{}】)|(\({}\))|(第{}集)|(\[{}\ ?[Vv]2\])|(【{}\ ?[Vv]2】)|(\ {}\ )".replace("{}", parse_num(
                episode)), t["title"]):
            if t["magnet"]:
                # 磁力链
                result["magnet"] = t["magnet"]
            result["torrent"] = "https://bangumi.moe/download/torrent/" + t["_id"] + "/" + t["title"].replace("/",
                                                                                                              "_") + ".torrent"
        if result["torrent"] is not None:
            break

    try:
        if result["torrent"] is None and page < res["page_count"]:
            return bangumi_search(tag_id, episode, page + 1)
    except KeyError:
        pass
    return result
