import os
import time
from xml.etree.ElementTree import Element, ElementTree

import requests
from loguru import logger

from utils import parse_num


def download_img(img_url: str, path: str):
    try:
        res = requests.get(img_url).content
        with open(path, "wb") as img:
            img.write(res)
        return path
    except:
        logger.debug(path.split('/')[-1] + "下载失败")
        return None


def add_episode_nfo(anime, file_path):
    episodedetails = Element("episodedetails")
    outline = Element("outline")
    lockdata = Element("lockdata")
    title = Element("title")
    originaltitle = Element("originaltitle")
    showtitle = Element("showtitle")
    season = Element("season")
    episode = Element("episode")
    # displayseason = Element("displayseason")
    # displayepisode = Element("displayepisode")
    # id = Element("id")
    year = Element("year")
    uniqueid_tmdb = Element("uniqueid", {"default": "true", "type": "tmdb"})
    ratings = Element("ratings")
    rating = Element("rating", {"default": "true", "max": "10", "name": "themoviedb"})
    value = Element("value")
    votes = Element("votes")
    # userrating = Element("userrating")
    plot = Element("plot")
    runtime = Element("runtime")
    # mpaa = Element("mpaa")
    # premiered = Element("premiered")
    aired = Element("aired")
    # watched = Element("watched")
    # playcount = Element("playcount")
    thumb = Element("thumb")
    # profile = Element("profile")
    # trailer = Element("trailer")
    dateadded = Element("dateadded")
    epbookmark = Element("epbookmark")
    code = Element("code")
    fileinfo = Element("fileinfo")
    streamdetails = Element("streamdetails")
    video = Element("video")
    codec = Element("codec")
    aspect = Element("aspect")
    width = Element("width")
    height = Element("height")
    durationinseconds = Element("durationinseconds")
    stereomode = Element("stereomode")
    audio = Element("audio")
    art = Element("art")
    poster = Element("poster")
    source = Element("source")
    original_filename = Element("original_filename")
    user_note = Element("user_note")
    tree = ElementTree(episodedetails)

    title.text = anime.tmdb["tv"]["name"]
    originaltitle.text = anime.tmdb["tv"]["original_name"]
    lockdata.text = "false"
    showtitle.text = anime.name
    season.text = str(anime.season)
    episode.text = str(anime.episode)
    plot.text = anime.tmdb["tv"]["overview"]
    dateadded.text = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    for p in anime.tmdb["episode"]["crew"]:
        if p["job"] == "Director":
            e = Element("director")
            e.text = p["name"]
            episodedetails.append(e)
        elif p["job"] == "Storyboard Artist" or p["job"] == "Writer":
            e = Element("writer")
            e.text = p["name"]
            episodedetails.append(e)
    year.text = anime.tmdb["episode"]["airdate"].split("-")[0]
    runtime.text = str(anime.tmdb["tv"]["episode_run_time"][0])
    for n in anime.tmdb['tv']['networks']:
        e = Element('studio')
        e.text = n['name']
        episodedetails.append(e)
    thumb.text = "https://image.tmdb.org/t/p/original" + anime.tmdb["episode"]["images"]["stills"][0]["file_path"]
    poster.text = download_img(thumb.text,
                               anime.path.replace(anime.path.split("/")[-1],
                                                  "%(name)s - S%(season)sE%(episode)s - %(e_name)s - thumb.%(format)s" % {
                                                      "name": anime.name, "season": parse_num(anime.season),
                                                      "episode": parse_num(anime.episode),
                                                      "e_name": anime.tmdb["episode"]["name"],
                                                      "format": anime.tmdb["episode"]["images"]["stills"][0][
                                                          "file_path"].split(".")[-1]}))
    uniqueid_tmdb.text = anime.tmdb["episode"]["id"]
    value.text = anime.tmdb["episode"]["vote_average"]
    votes.text = anime.tmdb["episode"]["vote_count"]
    aired.text = anime.tmdb["episode"]["air_date"]
    for p in anime.tmdb["season"]["credits"]["cast"]:
        actor_name = Element("name")
        actor_name.text = p["name"]
        actor_role = Element("role")
        actor_role.text = p["character"]
        actor_type = Element("type")
        actor_type.text = "Actor"
        actor_thumb = Element("thumb")
        actor = Element("actor")
        actor.append(actor_name)
        actor.append(actor_type)
        actor.append(actor_role)
        actor.append(actor_thumb)
        episodedetails.append(actor)
    source.text = "WEBRIP"
    original_filename.text = file_path.split("/")[-1]

    episodedetails.append(plot)
    episodedetails.append(outline)
    episodedetails.append(lockdata)
    episodedetails.append(dateadded)
    episodedetails.append(title)
    episodedetails.append(originaltitle)
    episodedetails.append(year)
    episodedetails.append(runtime)
    art.append(poster)
    episodedetails.append(art)
    episodedetails.append(episode)
    episodedetails.append(season)
    episodedetails.append(aired)
    # TODO:fileinfo
    episodedetails.append(showtitle)
    episodedetails.append(uniqueid_tmdb)
    rating.append(value)
    rating.append(votes)
    ratings.append(rating)
    episodedetails.append(ratings)
    episodedetails.append(thumb)
    episodedetails.append(epbookmark)
    episodedetails.append(code)
    episodedetails.append(source)
    episodedetails.append(original_filename)
    episodedetails.append(user_note)

    tree.write("%(name)s - S%(season)sE%(episode)s%(e_name)s.nfo" % {"name": anime.name,
                                                                     "season": parse_num(anime.season),
                                                                     "episode": parse_num(
                                                                         anime.episode),
                                                                     "e_name": " - " + anime.get_episode_name()},
               encoding="UTF-8", xml_declaration=True)


def scrape(anime, file_path):
    """
    刮削信息

    :param anime:
    :param file_path:
    :return:
    """
    # jellyfin可以配置自动刮削nfo文件和thumb图片，只需要修改文件名即可
    # add_episode_nfo(anime, file_path)
    anime.path = "{}/{}.{}".format(anime.path, anime.format_name, file_path.split(".")[-1])
    # new_path = file_path.replace(file_path.split("/")[-1].split(".")[0],anime.path)
    os.rename(file_path, anime.path)
