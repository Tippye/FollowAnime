# FollowAnime
自动追番，下载视频

# 注意⚠️
1. 种子资源来自于[萌番组](https://bangumi.moe), 更新及不及时就看字幕组的大佬们了
2. 判断更新的逻辑使用[TheMovieDB](https://www.themoviedb.org)的数据，和tinyMediaManager一致
3. 新下载的视频会在对应季度的文件夹里
   
   比如我下载 派对浪客诸葛孔明第一季第二季，他就会放到`anime/派对浪客诸葛孔明 (2022)/Season 1`下面，但是还不会改名，只能沿用种子名，刮削器也能直接识别出来

# 使用
1. 创建数据库
   ```mysql
   create table follow
    (
        tmId          int                                            not null
            primary key,
        name          varchar(255)                                   null,
        create_time   timestamp   default CURRENT_TIMESTAMP          null,
        team          varchar(255)                                   null,
        bangumi_tag   varchar(255)                                   null,
        season        int         default 1                          null,
        language      varchar(30) default 'zh' null
    );
   ```
   - `tmId`在tinyMediaManager中能找到，或者去[TheMovieDB](https://www.themoviedb.org)找（在url最后面的数字部分）

   - `name`使用tmdb的名字，本地文件夹命名需要是`名字 (2022)`

   - `create_time`没啥用

   - `team`是字幕组的tag，可以在[team.json](https://github.com/Tippye/FollowAnime/blob/master/team.json)里找到，也可以用下面`bangumi_tag`的查找方法

   - `bangumi_tag`是萌番组搜索的tag值，比如约会大作战直接搜名字会搜不到，搜到的第一个还是第三季，所以填写这个可以搜索的更准确，查找方法放到下面，不填写默认使用所有字幕组

   - `language`只适配了`zh`，我觉得我这辈子应该不会去优先繁体字幕

   ![lavTa1](https://cdn.jsdelivr.net/gh/tippye/PicCloud@master/uPic/2022/04/24/lavTa1.png)
2. 安装aria2
    安装教程自己百度，需要打开RPC功能，代码中的`ARIAID`是`rpc-secret`(aria2.conf) 的值

   一个可视化面板[AriaNg](https://github.com/mayswind/AriaNg)
3. ~~追番最好先创建好文件夹，不然可能会报错，以后有空再改~~
   ![LQzn8T](https://cdn.jsdelivr.net/gh/tippye/PicCloud@master/uPic/2022/04/20/LQzn8T.png)
4. 安装必要的库
   ```shell
   source ./venv/bin/activate && pip3 install -r ./requirements.txt
   ```
5. 修改部分配置
   在`config.py`中
   
   修改里面的`TheMovieDBKey`(TMDB官网申请)，`LOCAL_PATH`，`DB_xxx`，`ARIAxx`
6. `THREAD_NUM`是多线程的最大线程数，根据自己情况可以修改，默认是5
7. 运行试试

   接着4. 使用虚拟环境
   ```shell
   python3 ./auto_follow.py
   ```
8. 设置定时任务每天自动执行
   
   macOS可以用`crontab`
   
   Windows有计划任务
9. jellyfin或kodi之类的会自动识别更改

# `bangumi_tag`查找方法
1. 打开[萌番组](https://bangumi.moe/search/index)
2. 打开控制台（右键检查），并切换到网络
3. 搜索框搜索想看的番剧名，在搜到的标签中点击目标标签
4. 在控制台中找到最后一个`search`并点击预览请求数据
5. `tag_id`中的值就是目标tag
   ![VEp2cl](https://cdn.jsdelivr.net/gh/tippye/PicCloud@master/uPic/2022/04/23/VEp2cl.png)