import json
import logging
from urllib import request, parse
from urllib.error import URLError
from urllib.request import urlopen
import re
import ssl

import execjs
import requests


class TranslateSpider(object):

    def __init__(self):
        self.token = ''
        # 先打开首页，获取 token
        self.token = self.get_token()

    def crawl_word_means(self, word, sign, *, retry_times=3, charsets=('utf-8',)) -> tuple:
        """获取页面的HTML代码(通过递归实现指定次数的重试操作)"""
        page_json = None
        try:
            data = {
                'query': word,
                'from': 'en',
                'to': 'zh',
                'token': self.token,
                'sign': sign,
            }
            # print(data)

            headers = {
                'accept': '*/*',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8',
                # 'content-length': '82',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': 'BAIDUID=A9700867CB91C62BAA7D2A4BBD3DED38:FG=1; BIDUPSID=A9700867CB91C62BAA7D2A4BBD3DED38; PSTM=1554097330; BDSFRCVID=PD_OJeCmH6VsaxbwAoZvhbGhmmKK0gOTHllksQWhBPve-KuVJeC6EG0Ptf8g0KubFTPRogKK0gOTH6KF_2uxOjjg8UtVJeC6EG0P3J; H_BDCLCKID_SF=tRAOoC--JKvqKRopMtOhq4tehHRIhCr9WDTmLh6-bf82ebo6jf6hK4kVQPckKMni-CDe-pPKKR74Sp6m2MnHQMCvW4Rh5fke3mkjbn5zfn02OPKz0TKVX-4syP4eKMRnWnnRKfA-b4ncjRcTehoM3xI8LNj405OTt2LEoDKXJDtMhK-r5tjoM-jH-UnLqhj23eOZ0l8KtfcPJK3FyRtKyhL7MM5xW4TxLaFJ5MbmWIQHDnnF0RJjeMIuDl3K-RLeWm54KKJxWpCWeIJo5t5ObqIlhUJiB5JMBan7_pbIXKohJh7FM4tW3J0ZyxomtfQxtN4eaDFhfbT_eb59q45HMt00qxby26nQBbbeaJ5n0-nnhpcTbp5bQqDNj-oBaMbJfgc90xjuLJbf8tKRy6CaDTvLjaKfq-LXKD600PK8Kb7Vbpc90MnkbftWXfvw0j0Hbjv4bf782nonj-OzyURahjt7yajK2MR2X56jBMjj-M3pMn3ILp5pQT8ryb_OK5Oib4jgoj61ab3vOIOTXpO1jM0zBN5thURB2DkO-4bCWJ5TMl5jDh05y6TLeUrXKPQOHDrKBRbaHJOoDDkmXxQ5y4LdLp7xJMTM5arfKlj83bQ5sUIGeMjcbq_l0xObWRLeWJLH_KD2tDDbhKvRhPjMq44HhMrXK43ybK_XWJ52fMjpsh7_bfbVy5KZKUQO5JbCa26uBnoT2n6VOpkxbUnxy-AjMN0f2qFHLm7ma4OYQqcqEIQHQT3m5-5bbN3i-4jlQNRNWb3cWKJJ8UbSjxRPBTD02-nBat-OQ6npaJ5nJq5nhMtRy6CKjTo3DGLfJTneaKcJsJ78anT_eJbv5PI_h4L3en3RyMRZ5m7LaIQC-bjWH43qhp6-M-D1MMcLBMPj52OnanRs2-OGSnnt0bjqqfP0346-35543bRTLnLy5KJvfJoD3h3ChP-UyN3MWh37Je3lMKoaMp78jR093JO4y4Ldj4oxJp8eWJQ2QJ8BtK-WhKTP; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03206948066; MCITY=-%3A; BDUSS=DVqUzZPVzBuWmdwUjZhWHJkMFY5akN3UHZZRUExWHB1S0dwaTVWSzlDd01YSmhlSVFBQUFBJCQAAAAAAAAAAAEAAABW7G0EQ3lob2wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzPcF4Mz3Beb; H_WISE_SIDS=144938_142018_145114_145497_146368_144989_144134_145271_143935_131247_144682_137746_144742_144251_141941_127969_145968_140595_142421_143491_144607_145876_145998_131423_128701_145910_146002_145596_125581_146135_139909_146256_139884_144966_144534_145395_143855_145441_139914_110085; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1589100818,1589100925,1589100939,1589101336; delPer=0; H_PS_PSSID=1437_31671_21080_31590_30826_31605_31271_31463_31228_30823_22159; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ZD_ENTRY=baidu; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; __yjsv5_shitong=1.0_7_d003403b8cf62469bcfc1bce0d9e630e7979_300_1589680117611_59.42.55.145_0c48646c; PSINO=6; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1589683450; yjs_js_security_passport=671580707b2a7446d0da4ebc676842eb2b8136ed_1589683455_js; Hm_lvt_afd111fa62852d1f37001d1f980b6800=1589683459; Hm_lpvt_afd111fa62852d1f37001d1f980b6800=1589683459',
                'origin': 'https://fanyi.baidu.com',
                'referer': 'https://fanyi.baidu.com/',
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
                'x-requested-with': 'XMLHttpRequest',
            }

            res = requests.post(url=r'https://fanyi.baidu.com/basetrans', headers=headers, data=data)
            if res.status_code != 200:
                logging.error('request [%s] error: status_code=%d' % (word, res.status_code))
                return word, ''

            page_json = json.loads(res.text, encoding='utf-8')

            try:
                means = page_json['dict']['symbols'][0]
            except (KeyError, IndexError, TypeError):
                logging.error('[%s] 查找不到相应的解释' % word)
                means = ''

            return word, means

        except URLError as error:
            print('URL:', error)
            if retry_times > 0:
                return crawl_word_means(word, sign, retry_times=retry_times - 1, charsets=charsets)
            else:
                logging.error('request error: status_code=%d' % res.status_code)
                return word, ''

    def get_token(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8',
            'cookie': 'BAIDUID=A9700867CB91C62BAA7D2A4BBD3DED38:FG=1; BIDUPSID=A9700867CB91C62BAA7D2A4BBD3DED38; PSTM=1554097330; BDSFRCVID=PD_OJeCmH6VsaxbwAoZvhbGhmmKK0gOTHllksQWhBPve-KuVJeC6EG0Ptf8g0KubFTPRogKK0gOTH6KF_2uxOjjg8UtVJeC6EG0P3J; H_BDCLCKID_SF=tRAOoC--JKvqKRopMtOhq4tehHRIhCr9WDTmLh6-bf82ebo6jf6hK4kVQPckKMni-CDe-pPKKR74Sp6m2MnHQMCvW4Rh5fke3mkjbn5zfn02OPKz0TKVX-4syP4eKMRnWnnRKfA-b4ncjRcTehoM3xI8LNj405OTt2LEoDKXJDtMhK-r5tjoM-jH-UnLqhj23eOZ0l8KtfcPJK3FyRtKyhL7MM5xW4TxLaFJ5MbmWIQHDnnF0RJjeMIuDl3K-RLeWm54KKJxWpCWeIJo5t5ObqIlhUJiB5JMBan7_pbIXKohJh7FM4tW3J0ZyxomtfQxtN4eaDFhfbT_eb59q45HMt00qxby26nQBbbeaJ5n0-nnhpcTbp5bQqDNj-oBaMbJfgc90xjuLJbf8tKRy6CaDTvLjaKfq-LXKD600PK8Kb7Vbpc90MnkbftWXfvw0j0Hbjv4bf782nonj-OzyURahjt7yajK2MR2X56jBMjj-M3pMn3ILp5pQT8ryb_OK5Oib4jgoj61ab3vOIOTXpO1jM0zBN5thURB2DkO-4bCWJ5TMl5jDh05y6TLeUrXKPQOHDrKBRbaHJOoDDkmXxQ5y4LdLp7xJMTM5arfKlj83bQ5sUIGeMjcbq_l0xObWRLeWJLH_KD2tDDbhKvRhPjMq44HhMrXK43ybK_XWJ52fMjpsh7_bfbVy5KZKUQO5JbCa26uBnoT2n6VOpkxbUnxy-AjMN0f2qFHLm7ma4OYQqcqEIQHQT3m5-5bbN3i-4jlQNRNWb3cWKJJ8UbSjxRPBTD02-nBat-OQ6npaJ5nJq5nhMtRy6CKjTo3DGLfJTneaKcJsJ78anT_eJbv5PI_h4L3en3RyMRZ5m7LaIQC-bjWH43qhp6-M-D1MMcLBMPj52OnanRs2-OGSnnt0bjqqfP0346-35543bRTLnLy5KJvfJoD3h3ChP-UyN3MWh37Je3lMKoaMp78jR093JO4y4Ldj4oxJp8eWJQ2QJ8BtK-WhKTP; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03206948066; MCITY=-%3A; BDUSS=DVqUzZPVzBuWmdwUjZhWHJkMFY5akN3UHZZRUExWHB1S0dwaTVWSzlDd01YSmhlSVFBQUFBJCQAAAAAAAAAAAEAAABW7G0EQ3lob2wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzPcF4Mz3Beb; H_WISE_SIDS=144938_142018_145114_145497_146368_144989_144134_145271_143935_131247_144682_137746_144742_144251_141941_127969_145968_140595_142421_143491_144607_145876_145998_131423_128701_145910_146002_145596_125581_146135_139909_146256_139884_144966_144534_145395_143855_145441_139914_110085; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1589100818,1589100925,1589100939,1589101336; delPer=0; H_PS_PSSID=1437_31671_21080_31590_30826_31605_31271_31463_31228_30823_22159; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ZD_ENTRY=baidu; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; __yjsv5_shitong=1.0_7_d003403b8cf62469bcfc1bce0d9e630e7979_300_1589680117611_59.42.55.145_0c48646c; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1589680118; yjs_js_security_passport=7fa9bc56c893406cd934861f18dfc72b109ec980_1589680118_js; PSINO=6',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        }
        r = requests.get('https://fanyi.baidu.com/', headers=headers)
        self.token = re.findall("token: '(.*?)',", r.text)
        return self.token[0]

    def translate_spider_single(self, word) -> tuple:
        # 使用百度的 JS ，计算搜索词的 sign
        with open('static/js/get_sign.js', 'r', encoding='utf8') as f:
            js = f.read()
        js = execjs.compile(js)
        sign = js.call('e', word)

        word_means = self.crawl_word_means(word, sign, charsets=('utf-8', 'gbk', 'gb2312'))
        return word_means

