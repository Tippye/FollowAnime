import json
import os
import re
import time

import aria2rpc
import pymysql
import requests
from loguru import logger
from tmdbv3api import TMDb, TV, Season, Episode

from AnimeEpisode import AnimeEpisode
from utils import parse_num, parse_bangumi_tag

# TheMovieDB开发者ID
TheMovieDBKey = '20ffbd1bc28eecd2425143d476472b22'

# 本地动漫媒体路径
LOCAL_PATH = ["/Users/tippy/Movies/media/anime"]

# 萌番组搜索api
bangumiTagSearch = "https://bangumi.moe/api/tag/search"
bangumiSearch = "https://bangumi.moe/api/torrent/search"

# 数据库
DB_ADDRESS = "tippy.icu"
DB_USER = "anime"
DB_PASSWORD = "maKyKiSn2YnbZ2mm"
DB_BASE = "anime"

# aria2
ARIAID = "tippy"
ARIAURL = "localhost"

# 输出的日志文件路径
LOG_FILE = "./logs.log"


def get_follow_list():
    """
    获取追番列表

    :return:
    """
    db = pymysql.connect(host=DB_ADDRESS, port=3306, user=DB_USER, password=DB_PASSWORD, database=DB_BASE)
    cursor = db.cursor()
    sql = "SELECT * FROM follow"
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
        follow_list = []
        logger.info("找到追番列表：")
        for r in result:
            logger.info("\t" + r[1])
            follow_list.append(AnimeEpisode(tm_id=r[0], name=r[1], bangumi_tag=r[4], season=r[5], language=r[6]))
        return follow_list
    except:
        return []
    finally:
        db.close()


def get_local_episodes(anime: AnimeEpisode):
    """
    获取本地已存储的剧集列表
    如果没有本地文件夹会在LOCAL_PATH第一个目录下创建

    :param anime: 要查找的动漫对象
    :return List{int}:
    """
    local_anime = []
    for path in LOCAL_PATH:
        try:
            for anime_name in os.listdir(path):
                if re.search("^" + anime.name + " ?(\(\d{4}\))?", anime_name):
                    anime.path = path + '/' + anime_name + "/Season " + str(anime.season)
                    if not os.path.isdir(anime.path):
                        os.mkdir(anime.path)
                    season_dir = os.listdir(anime.path)
                    for e_file in season_dir:
                        temp = re.findall("S0?" + str(anime.season) + "E(\d+).*?\.(mp4|mkv)$", e_file)
                        if len(temp) > 0:
                            local_anime.append(int(temp[0][0]))
                    break

        except FileNotFoundError as fe:
            print(fe)
    # 本地还没有动漫文件夹
    if anime.path is None:
        os.mkdir("{}/{}".format(LOCAL_PATH[0], anime.name))
        return get_local_episodes(anime)
        # anime.path = "{}/Season {}".format(anime.path, anime.season)
        # os.mkdir(anime.path)
    return local_anime


def get_tmdb_data(anime: AnimeEpisode):
    """
    获取tmdb的数据

    :param anime: 动漫对象
    :return: 所有已经发布但未下载但剧集对象
    """
    prepare_list = []
    local_episodes = get_local_episodes(anime)
    tmdb = TMDb()
    tmdb.language = "zh"
    tmdb.api_key = TheMovieDBKey
    anime.set_anime_data(TV().details(anime.tm_id))
    anime.set_season_data(Season().details(anime.tm_id, anime.season))
    for e in anime.tmdb["season"]["episodes"]:
        if e['air_date'] != "" and time.mktime(time.strptime(e['air_date'], '%Y-%m-%d')) < time.time() and \
                int(e['episode_number']) not in local_episodes:
            e = AnimeEpisode(anime.name, anime.season, int(e["episode_number"]), anime.path, anime.tm_id,
                             anime.language,
                             None, None, anime.tmdb,anime.bangumi_tag)
            e.set_episode_data(Episode().details(e.tm_id, e.season, e.episode))
            prepare_list.append(e)

    return prepare_list


def get_bangumi_search_tags(anime):
    """
    获取萌番组搜索时用的tags
    :param anime:
    :return:
    """
    tags = []
    if anime.bangumi_tag:
        tags.append(anime.bangumi_tag)
        tags.append(parse_bangumi_tag(anime.language))
    else:
        data = json.dumps({
            "name": anime.name,
            "keyword": True,
            "multi": True
        })
        res = requests.post(bangumiTagSearch, data=data)
        res = json.loads(res.content)
        if res['success'] and res["found"]:
            tags.append(res['tag'][0]['_id'])
            tags.append(parse_bangumi_tag(anime.language))

    # TODO: 字幕组标签
    return tags


def get_bangumi_download_link(anime):
    """
    获取萌番组下载链接

    :param anime:
    :return:
    """
    search_tags = get_bangumi_search_tags(anime)
    if len(search_tags) < 1:
        logger.info("Bangumi未搜索到" + anime.name)
        return
    data = json.dumps({
        "tag_id": search_tags
    })
    time.sleep(1)
    res = json.loads(requests.post(bangumiSearch, data=data).content)
    # TODO:多页搜索
    e_num = parse_num(anime.episode)
    if len(res) < 1:
        logger.info("Bangumi未搜索到" + anime.name)
        return
    for t in res["torrents"]:
        if re.search("([\[【第])" + e_num + "([]】话])", t["title"]):
            if t["magnet"]:
                # 磁力链
                anime.set_magnet(t["magnet"])
                logger.info("找到第" + e_num + "集磁力链接")
            anime.set_torrent(
                "https://bangumi.moe/download/torrent/" + t["_id"] + "/" + t["title"].replace("/", "_") + ".torrent")
            break
    if anime.magent is None and anime.torrent_url is None:
        logger.info("未找到 " + anime.name + "S" + parse_num(anime.season) + "E" + e_num + " 的下载链接")


def get_download_link(anime):
    """
    获取下载链接

    :param anime:
    :return:
    """
    get_bangumi_download_link(anime)


client = None


def download(anime):
    try:
        global client
        if client is None:
            client = aria2rpc.aria2_rpc_api(host=ARIAURL, secret=ARIAID)
        option = {
            "dir": anime.path,
            "out": anime.name + " - S" + parse_num(anime.season) + "E" + parse_num(anime.episode)
        }
        uris = []
        if anime.magent:
            uris.append(anime.magent)
        else:
            uris.append(anime.torrent_url)
        if len(uris) > 0:
            res = client.addUri(uris=uris, options=option)
            logger.info("开始下载" + option['out'])
            logger.info("下载ID为：" + res)
            anime.downloading(client, res)
        else:
            logger.info("未找到" + option['out'])
    except ConnectionError:
        logger.debug("网络异常，可能是未启动aria2")


def main():
    try:
        logger.add(LOG_FILE)
        follow_list = get_follow_list()
        for anime in follow_list:
            logger.info("开始查找" + anime.name)
            prepare_list = get_tmdb_data(anime)
            if len(prepare_list) < 1:
                logger.info(anime.name + "查找完成，没有未下载剧集")
            for p_anime in prepare_list:
                get_download_link(p_anime)
                if p_anime.magent:
                    download(p_anime)
    except KeyboardInterrupt:
        logger.info("程序已停止")
    except ConnectionError:
        logger.debug("网络异常，5秒后重试")
        time.sleep(5)
        main()


if __name__ == '__main__':
    main()
