import pymysql

from config import *


class DBUtil:
    db = None
    cursor = None

    def __init__(self):
        self.db = pymysql.connect(host=DB_ADDRESS, port=3306, user=DB_USER, password=DB_PASSWORD, database=DB_BASE)
        self.cursor = self.db.cursor()

    def get_follows(self):
        """
        获取追番列表

        :return:
        """
        sql = "SELECT * FROM follow"
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except:
            return []

    def delete_follow(self, tmid):
        """
        删除一条数据
        :param tmid: 数据的tmId
        :return:
        """
        sql = "DELETE FROM follow where tmId=" + str(tmid)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def close(self):
        """
        关闭数据库

        :return:
        """
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
