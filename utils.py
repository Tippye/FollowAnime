def parse_num(num: int):
    """
    数字转为字符串，个位数补0

    :param num:
    :return:
    """
    if -1 < num < 10:
        return "0" + str(num)
    return str(num)


def parse_bangumi_tag(tag: str):
    if tag == "zh" or tag == "简体中文":
        return '548ee0ea4ab7379536f56354'
