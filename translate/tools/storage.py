import datetime
import logging

from translate.tools.translateSpider import translate_spider
from translate.tools.translateSpiderBetter import TranslateSpider
from translate.models import WordMeans
import redis


class RedisClient(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._redis_pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)

    def get(self, words: list) -> (dict, list):
        dict_yes = {}
        list_no = []
        r = redis.Redis(connection_pool=self._redis_pool)
        ret = r.mget(*words)
        # print(type(ret))
        # print(ret)
        for i in range(0, len(words)):
            if ret[i] is not None:
                dict_yes[words[i]] = ret[i]
            else:
                list_no.append(words[i])
        return dict_yes, list_no

    def set(self, trans: dict):
        '''少量新增'''
        r = redis.Redis(connection_pool=self._redis_pool)
        r.msetnx(trans)  # 不存在的才写入

    def load(self, trans_iter: iter):
        '''从数据库大量加载'''
        r = redis.Redis(connection_pool=self._redis_pool)
        pipe = r.pipeline()
        for trans in trans_iter:
            pipe.setnx(trans[0], trans[1])
        pipe.execute()


class SqlClient(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def get_all_iterator():
        '''返回数据表所有内容，数据量很大，使用迭代器'''
        it = WordMeans.objects.all().iterator()
        for wm in it:
            yield wm.word, wm.means

    @staticmethod
    def insert(trans: dict):
        '''插入新查询的翻译，数据量小'''
        trans_list = []
        for k, v in trans.items():
            # wm = WordMeans()
            # wm.word = k
            # wm.means = v
            # trans_list.append(wm)
            trans_list.append(WordMeans.create(k, v))
        try:
            WordMeans.objects.bulk_create(trans_list)  # 注意 : not bluk_create
        except Exception as e:
            logging.error('=-=-=-=- sql insert error -=-=-=-=\n', e, '\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')


class Storage(object):
    re_cache_remain = 5

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    # 如果系统重启，要把数据库内容加载到缓存
    def __init__(self):
        self.sql = SqlClient()
        self.red = RedisClient()
        self.spider = TranslateSpider()
        self.re_cache_last_time = datetime.datetime.now()
        self.re_cache_ing = False

    # views 可直接调用
    def get_trans_better(self, words: list):
        dict_yes, list_no = self.red.get(words=words)

        # 取出来是 str， 要转成 dict
        for k, v in dict_yes.items():
            dict_yes[k] = eval(v)
            print('****************** found ****************** : ', k)

        for no in list_no:
            # 使用爬虫获取翻译
            wm_tuple = self.spider.translate_spider_single(no)  # 获得的是 dict

            # 要把 dict 中的每个 value ， 从 dict 转成 str
            if wm_tuple[1] != '':
                wm_str = {wm_tuple[0]: str(wm_tuple[1])}
                print('****** new ****** : %s\n' % wm_tuple[0], wm_tuple[1])

                # 写入缓存和数据库，要写入字符串
                self.sql.insert(trans=wm_str)
                self.red.set(trans=wm_str)

            else:
                print('查找不到解释： ', wm_tuple[0])

            # Todo: 可能查找不到，于是返回的个数不齐全
            dict_yes.update({wm_tuple[0]: wm_tuple[1]})

        return dict_yes

    # views 可直接调用
    def get_trans(self, words: list):
        dict_yes, list_no = self.red.get(words=words)

        # 取出来是 str， 要转成 dict
        if len(dict_yes) > 0:
            for k, v in dict_yes.items():
                dict_yes[k] = eval(v)
                print('****************** found ****************** : ', k)

        if len(list_no) > 0:
            # 使用爬虫获取翻译
            new_word_means_dict = translate_spider(list_no)  # 获得的是 dict

            # 要把 dict 中的每个 value ， 从 dict 转成 str
            word_means_str = {}
            for k, v in new_word_means_dict.items():
                if v != '':
                    word_means_str[k] = str(v)
                    print('****** new ******\n', k, ' -> ', v)
                    list_no.remove(k)
                else:
                    print('查找不到解释： ', k)

            # 写入缓存和数据库，要写入字符串
            if len(word_means_str) > 0:
                self.sql.insert(trans=word_means_str)
                self.red.set(trans=word_means_str)

            # 新、旧翻译合并
            dict_yes.update(new_word_means_dict)

            # Todo: 可能查找不到，于是返回的个数不齐全
            for no in list_no:
                dict_yes.update({no: ''})

        return dict_yes

    def can_re_cache(self):
        dur = datetime.datetime.now() - self.re_cache_last_time
        return dur.total_seconds() > 60

    def re_cache(self):
        '''把 SQL 数据 重新加载到 REDIS ， 通过网页后台输入密码调用'''
        self.re_cache_ing = True
        logging.info('\n============ re cache start ============')
        self.re_cache_last_time = datetime.datetime.now()

        pass  # Todo: 项目重启  不等于  数据库系统重启
        self.red.load(trans_iter=self.sql.get_all_iterator())

        self.re_cache_remain = 5
        self.re_cache_ing = False
        logging.info('============ re cache finish ============\n')


storage = Storage()
