import demjson
from urllib import request, parse
from urllib.error import URLError
from urllib.request import urlopen
import re
import ssl
import requests


# ====================================================================================================

def decode_page(page_bytes, charsets=('utf-8',)):
    """通过指定的字符集对页面进行解码(不是每个网站都将字符集设置为utf-8)"""
    page_html = None
    for charset in charsets:
        try:
            page_html = page_bytes.decode(charset)
            break
        except UnicodeDecodeError:
            pass
            # logging.error('Decode:', error)
    return page_html


def get_page_html(word, sign, token, *, retry_times=3, charsets=('utf-8',)):
    """获取页面的HTML代码(通过递归实现指定次数的重试操作)"""
    page_html = None
    try:
        '''
        【headers】
        :authority: fanyi.baidu.com
        :method: POST
        :path: /v2transapi?from=en&to=zh
        :scheme: https
        accept: */*
        accept-encoding: gzip, deflate, br
        accept-language: zh-CN,zh-TW;q=0.9,zh;q=0.8
        '''
        data = {
            'from': 'en',
            'to': 'zh',
            'query': word,
            'transtype': 'realtime',
            'simple_means_flag': '3',
            'sign': sign,
            'token': '6c3778c4794887cec965ea0a208df1e1',
            'domain': 'common',
        }
        print(data)
        headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8',
            'content-length': '139',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': r'BAIDUID=A9700867CB91C62BAA7D2A4BBD3DED38:FG=1; BIDUPSID=A9700867CB91C62BAA7D2A4BBD3DED38; PSTM=1554097330; BDSFRCVID=PD_OJeCmH6VsaxbwAoZvhbGhmmKK0gOTHllksQWhBPve-KuVJeC6EG0Ptf8g0KubFTPRogKK0gOTH6KF_2uxOjjg8UtVJeC6EG0P3J; H_BDCLCKID_SF=tRAOoC--JKvqKRopMtOhq4tehHRIhCr9WDTmLh6-bf82ebo6jf6hK4kVQPckKMni-CDe-pPKKR74Sp6m2MnHQMCvW4Rh5fke3mkjbn5zfn02OPKz0TKVX-4syP4eKMRnWnnRKfA-b4ncjRcTehoM3xI8LNj405OTt2LEoDKXJDtMhK-r5tjoM-jH-UnLqhj23eOZ0l8KtfcPJK3FyRtKyhL7MM5xW4TxLaFJ5MbmWIQHDnnF0RJjeMIuDl3K-RLeWm54KKJxWpCWeIJo5t5ObqIlhUJiB5JMBan7_pbIXKohJh7FM4tW3J0ZyxomtfQxtN4eaDFhfbT_eb59q45HMt00qxby26nQBbbeaJ5n0-nnhpcTbp5bQqDNj-oBaMbJfgc90xjuLJbf8tKRy6CaDTvLjaKfq-LXKD600PK8Kb7Vbpc90MnkbftWXfvw0j0Hbjv4bf782nonj-OzyURahjt7yajK2MR2X56jBMjj-M3pMn3ILp5pQT8ryb_OK5Oib4jgoj61ab3vOIOTXpO1jM0zBN5thURB2DkO-4bCWJ5TMl5jDh05y6TLeUrXKPQOHDrKBRbaHJOoDDkmXxQ5y4LdLp7xJMTM5arfKlj83bQ5sUIGeMjcbq_l0xObWRLeWJLH_KD2tDDbhKvRhPjMq44HhMrXK43ybK_XWJ52fMjpsh7_bfbVy5KZKUQO5JbCa26uBnoT2n6VOpkxbUnxy-AjMN0f2qFHLm7ma4OYQqcqEIQHQT3m5-5bbN3i-4jlQNRNWb3cWKJJ8UbSjxRPBTD02-nBat-OQ6npaJ5nJq5nhMtRy6CKjTo3DGLfJTneaKcJsJ78anT_eJbv5PI_h4L3en3RyMRZ5m7LaIQC-bjWH43qhp6-M-D1MMcLBMPj52OnanRs2-OGSnnt0bjqqfP0346-35543bRTLnLy5KJvfJoD3h3ChP-UyN3MWh37Je3lMKoaMp78jR093JO4y4Ldj4oxJp8eWJQ2QJ8BtK-WhKTP; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a03206948066; MCITY=-%3A; BDUSS=DVqUzZPVzBuWmdwUjZhWHJkMFY5akN3UHZZRUExWHB1S0dwaTVWSzlDd01YSmhlSVFBQUFBJCQAAAAAAAAAAAEAAABW7G0EQ3lob2wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzPcF4Mz3Beb; H_WISE_SIDS=144938_142018_145114_145497_146368_144989_144134_145271_143935_131247_144682_137746_144742_144251_141941_127969_145968_140595_142421_143491_144607_145876_145998_131423_128701_145910_146002_145596_125581_146135_139909_146256_139884_144966_144534_145395_143855_145441_139914_110085; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=1437_21080_31422_31341_31271_31463_31228_30823_31163_31473_22159; delPer=0; PSINO=6; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1586339419,1586789521,1588755778,1588775577; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1588819047; __yjsv5_shitong=1.0_7_d003403b8cf62469bcfc1bce0d9e630e7979_300_1588819037887_183.36.81.119_e7dadb5e; yjs_js_security_passport=c797ec51da2c2823d7912aa8063fd5df495b0a53_1588819052_js',
            'origin': 'https://fanyi.baidu.com',
            'referer': 'https://fanyi.baidu.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        if True:
            res = requests.post(url=r'https://fanyi.baidu.com/v2transapi', headers=headers, data=data)
            print('status_code: ', res.status_code)

            pat = re.compile(r'"simple_means":(.*?),"lang"', re.DOTALL | re.MULTILINE)
            page_html = pat.findall(res.content.decode())[0]
            # page_html = json.loads(page_html)  # , encoding='utf-8')
            page_html = demjson.decode(page_html)

            res_dict = {
                'name': word
            }

            try:
                res_dict['means'] = page_html['symbols'][0]
            except (KeyError, IndexError):
                res_dict['means'] = '【Error】查找不到相应的解释'

            try:
                res_dict['memory'] = page_html['memory_skill']
            except KeyError:
                pass

            return res_dict

            # with open('t.json', 'w', encoding='utf-8') as f:
            #     json.dump(page_html, f, indent=4, ensure_ascii=False)
        else:
            postData = parse.urlencode(data)
            req = request.Request(r'https://fanyi.baidu.com/v2transapi', headers=headers)
            page_b = urlopen(req, data=postData.encode('utf-8')).read()
            with open('t.htm', 'wb') as f:
                f.write(page_b)
            page_html = decode_page(page_b, charsets)
    except URLError as error:
        print('URL:', error)
        if retry_times > 0:
            return get_page_html(word, sign, retry_times=retry_times - 1,
                                 charsets=charsets)
        else:
            return 'URLError'
    return page_html



# def unicode_convert(input):
#     if isinstance(input, dict):
#         return {unicode_convert(key): unicode_convert(value) for key, value in input.iteritems()}
#     elif isinstance(input, list):
#         return [unicode_convert(element) for element in input]
#     elif isinstance(input, unicode):
#         return input.encode('utf-8')
#     else:
#         return input


def get_matched_parts(page_html, pattern_str, pattern_ignore_case=re.I):
    """从页面中提取需要的部分(通常是链接也可以通过正则表达式进行指定)"""
    pattern_regex = re.compile(pattern_str, pattern_ignore_case)
    return pattern_regex.findall(page_html) if page_html else []


def translate_spider(data) -> list:
    # pat = re.compile(......);
    ssl._create_default_https_context = ssl._create_unverified_context

    lst = []
    for word, sign in data.items():
        page_html = get_page_html(word, sign, 0, charsets=('utf-8', 'gbk', 'gb2312'))
        lst.append(page_html)
    print(lst)
    return lst

