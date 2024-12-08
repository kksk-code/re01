'''这个text4里放的代码全是用于爬取用户发布在空间的视频列表的，
用的都是新接口，web/search，都是defeat
#12.4修改
'''
#获取用户发布在空间的视频列表
#12.3
#失败，打印空列表
'''import requests
import datetime
import random
import time#

headers = {
    "Cookie": "b4c46ab5%2C1748612005%2C9a2d8%2Ac1CjCw",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Referer": "https://space.bilibili.com/3546771443681290/video",
    "Origin": "https://www.bilibili.com"
}

user_id = 3546771443681290
ps = 5  # 每次请求的数据量
max_pages = 5  # 最大页码数
video_data = []

for pn in range(1, max_pages + 1):
    url = f'https://api.bilibili.com/x/space/arc/search?mid={user_id}&ps={ps}&pn={pn}&order=pubdate&jsonp=jsonp'
    
    # 重试机制
    for attempt in range(3):  # 最多重试3次
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                info_list = json_data.get('data', {}).get('list', {}).get('vlist', [])
                for index in info_list:
                    data_time = str(datetime.datetime.fromtimestamp(index.get('created', 0)))
                    date, up_time = data_time.split(' ')
                    video_info = {
                        '标题': index.get('title', '未知标题'),
                        '播放量': index.get('play', 0),
                        '评论': index.get('comment', 0),
                        'bv号': index.get('bvid', '未知BV号'),
                        '日期': date,
                        '上传时间': up_time,
                    }
                    video_data.append(video_info)
                print(f"第 {pn} 页数据获取成功")
                break  # 成功获取数据，跳出重试循环
            else:
                print(f"状态码异常: {response.status_code}")
        except Exception as e:
            print(f"请求异常: {e}")
        time.sleep(random.uniform(10, 30))  # 重试前随机延时

# 打印最终数据
print(video_data)
'''
#本代码使用新接口https://api.bilibili.com/x/space/wbi/arc/search获取用户发布在空间的视频列表。
#该接口需要先获取用户的wbi_img信息，然后通过wbi_img信息和用户的uid、pn、ps、index等参数计算出w_rid，
# 并将这些参数和wbi_img信息一起发送给api.bilibili.com/x/space/wbi/arc/search接口。
#但是由于我看不懂web鉴权方式，，，所以defeat
#12.4
'''import requests#库

def get_wbi_images():#使用wib签名
    url = "https://api.bilibili.com/x/web-interface/nav"
    response = requests.get(url)
    data = response.json()
    img_url = data['data']['wbi_img']['img_url']
    sub_url = data['data']['wbi_img']['sub_url']
    return img_url, sub_url
def get_mixin_key(img_url, sub_url):
#获取最新的 img_key 和 sub_key。这两个密钥是动态变化的，每次访问时都会从接口中获取。
    import re
    img_key = re.search(r'(\w+)\.png', img_url).group(1)
    sub_key = re.search(r'(\w+)\.png', sub_url).group(1)
    mixin_key = img_key + sub_key
    mixin_key = ''.join([mixin_key[i] for i in [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
        27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
        37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
        22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52
    ]])
    return mixin_key[:32]
import hashlib
import time

def generate_wbi_params(params, mixin_key):
    wts = str(int(time.time()))
    params.update({'wts': wts})
    sorted_params = '&'.join(f"{k}={params[k]}" for k in sorted(params))
    w_rid = hashlib.md5((sorted_params + mixin_key).encode('utf-8')).hexdigest()
    params.update({'w_rid': w_rid})
    return params
def fetch_bilibili_videos(mid, page_number=1, page_size=10):
    img_url, sub_url = get_wbi_images()
    mixin_key = get_mixin_key(img_url, sub_url)
    
    params = {
        'mid': mid,
        'pn': page_number,
        'ps': page_size,
        'index': 1
    }
    
    params = generate_wbi_params(params, mixin_key)
    
    headers = {
        'Referer': f'https://space.bilibili.com/{mid}/video',
        'User-Agent': 'Mozilla/5.0'
    }
    
    url = "https://api.bilibili.com/x/space/wbi/arc/search"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

# 示例调用
mid = 3546771443681290  # 替换为目标用户的 UID
data = fetch_bilibili_videos(mid)
print(data)
'''
#本代码使用wbi签名获取用户发布在空间的视频列表。
#wbi签名的生成方法比较复杂，需要先获取用户的wbi_img信息，
# 然后通过wbi_img信息和用户的uid、pn、ps、index等参数计算出w_rid，
# 并将这些参数和wbi_img信息一起发送给api.bilibili.com/x/space/wbi/arc/search接口。
#这是了解了点hash算法，了解h5d等等，辅助gpt值做出的结果，
#但是还是一知半解
#12.4.
'''
import requests
import hashlib
import time

def calculate_md5(string):
    # 通过hashlib模块创建了一个MD5哈希算法的实例
    md5_hash = hashlib.md5()
    # 使用UTF-8编码将输入字符串转换为字节，并将其更新到哈希对象中
    md5_hash.update(string.encode('utf-8'))
    # 计算得到的MD5哈希值的十六进制表示
    return md5_hash.hexdigest()

for page in range(1, 14):#遍历1-13页
    date_time = int(time.time())
    f = [
        "dm_cover_img_str=QU5HTEUgKEludGVsLCBJbnRlbChSKSBVSEQgR3JhcGhpY3MgNjMwICgweDAwMDAzRTkyKSBEaXJlY3QzRDExIHZzXzVfMCBwc181XzAsIEQzRDExKUdvb2dsZSBJbmMuIChJbnRlbC",
        "dm_img_list=%5B%5D",
        "dm_img_str=V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ",
        "keyword=",
        "mid=3493110839511225",
        "order=pubdate",
        "order_avoided=true",
        "platform=web",
        f"pn={page}",
        "ps=30",
        "tid=0",
        "web_location=1550101",
        f"wts={date_time}"
    ]
    y = '&'.join(f)
    w_rid = calculate_md5(y + "ea1db124af3c7062474693fa704f4ff8")
    url = 'https://api.bilibili.com/x/space/wbi/arc/search'
    data = {
        'mid': '3493110839511225',
        'ps': '30',
        'tid': '0',
        'pn': page,
        'keyword': '',
        'order': 'pubdate',
        'platform': 'web',
        'web_location': '1550101',
        'order_avoided': 'true',
        'dm_img_list': '[]',
        'dm_img_str': 'V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ',
        'dm_cover_img_str': 'QU5HTEUgKEludGVsLCBJbnRlbChSKSBVSEQgR3JhcGhpY3MgNjMwICgweDAwMDAzRTkyKSBEaXJlY3QzRDExIHZzXzVfMCBwc181XzAsIEQzRDExKUdvb2dsZSBJbmMuIChJbnRlbC',
        'w_rid': w_rid,
        'wts': date_time,
    }
    headers = {
        "Cookie": "buvid3=41112443-E178-98D1-8D0E-DAD06D64F04B56600infoc; b_nut=1731587456; _uuid=5FDC67210-4BC1-511B-C966-6A4910A65379D57214infoc; buvid4=D6465891-D232-A009-894C-47B254E125FB57513-024111412-a6WeNhLswS3vCsBGEIiNFQ%3D%3D; enable_web_push=DISABLE; rpdid=|(u)YRJmuRu|0J'u~Jul)~l|); header_theme_version=CLOSE; fingerprint=f12cea7d6adf81497769561ebf22992b; buvid_fp_plain=undefined; PVID=1; bp_t_offset_3546799411300943=1004850960889020416; bsource_origin=bing_ogv; browser_resolution=1232-594; home_feed_column=4; CURRENT_QUALITY=64; bsource=search_bing; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzM0ODgyNjUsImlhdCI6MTczMzIyOTAwNSwicGx0IjotMX0.veLE_BasMr2aUHIBu6nE_Sy8dNiZFBqP8ACATbUKbSg; bili_ticket_expires=1733488205; CURRENT_FNVAL=4048; bp_t_offset_436623527=1007055765170552832; b_lsid=7ECBE210B_19391847BA4; SESSDATA=7d9aa5c8%2C1748865845%2Cf39ad%2Ac1CjApkQm0L47xAzxCk91UZyDoKnh-lyPh6fZDxGpFUSidrezmIdUxLVEQOUbRrFxZR14SVkhsUDNUekxUU21tejY2N2V0VHY5Q0Y0dTllNlVuWjdJNDZKTTZlc1VIeFBCU0NvcVhBZGJlTEV1MVpSRGt3YVNVTUFYWU1FWHprdjVNanAxbTFnWEpnIIEC; bili_jct=d123dcb6f7ffa308b260fe7f5bee8aaa; DedeUserID=436623527; DedeUserID__ckMd5=1912d2ddf1180499; buvid_fp=f12cea7d6adf81497769561ebf22992b; sid=6yf9j750",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url=url, params=data, headers=headers).json()
    print(response)
    print(w_rid)
'''
#网上找的一篇，但是那个文档是22年发布的，接口正确，但是F12扒到的数据发生了一些变化
# 新接口https://api.bilibili.com/x/space/wbi/arc/search获取用户发布在空间的视频列表。
#也是defat，不知道是不是因为我没找到wbi_img信息，导致签名计算失败
#12.5.2024
import requests
import csv
import datetime
import hashlib
import time
#明确需求，https://space.bilibili.com/3546771443681290/video
# 爬的是io社的的视频列表，需要获取视频标题、播放量、评论数、BV号、上传日期、上传时间
headers = {
    # 用户代理 表示浏览器基本身份信息
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}
#这个是别人的视频信息，但是我用F12扒的时候，并没有找到这个信息。。
string = f'keyword=&mid=517327498&order=pubdate&order_avoided=true&platform=web&pn=1&ps=30&tid=0&web_location=1550101&wts={int(time.time())}6eff17696695c344b67618ac7b114f92'
# 实例化对象
md5_hash = hashlib.md5()
md5_hash.update(string.encode('utf-8'))
# 请求链接
url = 'https://api.bilibili.com/x/space/wbi/arc/search'#新api接口
# 请求参数
data = {
    'mid': '517327498',
    'ps': '30',
    'tid': '0',
    'pn': '1',
    'keyword': '',
    'order': 'pubdate',
    'platform': 'web',
    'web_location': '1550101',
    'order_avoided': 'true',
    'w_rid': md5_hash.hexdigest(),
    'wts': int(time.time()),
}
# 发送请求 <Response [200]> 响应对象 表示请求成功
response = requests.get(url=url, params=data, headers=headers)
for index in response.json()['data']['list']['vlist']:
    # 时间戳 时间节点 --> 上传视频时间点
    date = index['created']
    dt = datetime.datetime.fromtimestamp(date)
    dt_time = dt.strftime('%Y-%m-%d')
    dit = {
        '标题': index['title'],
        '描述': index['description'],
        'BV号': index['bvid'],
        '播放量': index['play'],
        '弹幕': index['video_review'],
        '评论': index['comment'],
        '时长': index['length'],
        '上传时间': dt_time,
    }
    print(dit)