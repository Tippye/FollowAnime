import http.client
import xmlrpc.client
from time import sleep

import requests
from loguru import logger

from scrape import scrape
from utils import parse_num


class AnimeEpisode:
    def __init__(self, name: str, season=1, episode=0, path: str = None, tm_id: str = None, language: str = "zh",
                 torrent_url: str = None, magnet: str = None, tmdb: object = None, bangumi_tag: str = None,
                 team: str = None):
        """
        剧集

        :param name: 动漫名称
        :param season: 季度
        :param episode: 集数
        :param path: 本地存储路径
        :param tm_id: TheMovieDB ID
        :param language: 语言
        :param torrent_url: 种子文件链接
        :param magnet: 磁力链接
        :param tmdb: TheMovieDB数据
        :param bangumi_tag: 萌番组搜索时优先使用此tag，没有则用name搜索取首位
        :param team: 字幕组tag
        """
        self.name = name
        self.season = season
        self.episode = episode
        self.path = path
        self.tm_id = tm_id
        self.language = language
        self.torrent_url = torrent_url
        self.magnet = magnet
        self.tmdb = tmdb
        self.bangumi_tag = bangumi_tag
        self.team = team
        self.format_name = "{} - S{}E{}".format(name, parse_num(season), parse_num(episode))

    def set_anime_data(self, data):
        if self.tmdb is None:
            self.tmdb = {"tv": None}
        self.tmdb["tv"] = data

    def set_season_data(self, data):
        self.tmdb["season"] = data

    def set_episode_data(self, data):
        self.tmdb["episode"] = data
        self.format_name = "{} - S{}E{} - {}".format(self.name, parse_num(self.season), parse_num(self.episode),
                                                     data["name"])

    def set_magnet(self, magnet):
        self.magnet = magnet

    def set_torrent(self, torrent_url):
        self.torrent_url = torrent_url

    def get_episode_name(self):
        if self.tmdb and self.tmdb["episode"]:
            return self.tmdb["episode"]["name"]
        return ""

    def downloading(self, client, gid):
        """
        下载完成后修改文件名

        :param client: aria2c
        :param gid: aria2 返回的gid
        :return:
        """
        infoHash = client.tellStatus(gid=gid)["infoHash"]
        new_gid = None
        a = None
        while new_gid is None:
            actives = client.tellActive()
            if len(actives) < 1:
                new_gid = "null"
                a = "null"
            for active in actives:
                # infoHash相同判断为同一个下载（会先下载种子在下载文件）
                # 文件大小大于 1Mb 判断为文件，否则当作种子
                if active["infoHash"] == infoHash and int(active["totalLength"]) > (1024 * 1000):
                    new_gid = active["gid"]
            if new_gid is None:
                sleep(5)

        while not (new_gid is None) and a is None:
            try:
                status = client.tellStatus(gid=new_gid)
                if status["status"] == "active":
                    logger.info(self.format_name + " 下载进度： " + str(
                        100 * int(status["completedLength"]) / int(status["totalLength"])) + "%")
                    sleep(10)
                else:
                    # 暂停时status=="paused"
                    a = "null"
            except xmlrpc.client.Fault:
                # GID xxx is not found
                a = "null"
            except http.client.CannotSendRequest or http.client.ResponseNotReady:
                sleep(10)

        if a == "null":
            logger.info("%s 下载已停止, 请手动启动下载任务，下载完成后请手动修改文件名" % self.format_name)
        else:
            scrape(self, a["files"][0]["path"])
            logger.info("下载完成：" + a["files"][0]["path"])
