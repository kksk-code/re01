#url = "http://member.bilibili.com/arcopen/fn/archive/viewlist"
#废弃原因，没有登上开发者平台，该平台还要上传公司信息才能注册。。

#以下是代码本体：
#说明：该代码用于爬取B站UP主的视频列表信息，并打印出视频标题、视频ID、播放量、上传时间等信息。
#但是用的是废弃api，api.bilibili.com/x/space/arc/search,能爬到信息，但是不稳定
#12.5.00：23爬出结果
#12.5.20：41 ——-返回值请求失败，错误信息：请求过于频繁，请稍后再试（打算每天都试一次，看看频率）
#12.8重试，成功，预计api接口冷却时间：3天 就是不知道为什么vscode会在一次运行后连带着再多运行几次
import requests


uid = 3546771443681290

# API 接口 URL
url = f'https://api.bilibili.com/x/space/arc/search'

# 请求参数
params = {
    'mid': uid,  
    'ps': 20,    
    'pn': 1,     
    'order': 'pubdate',  
    'platform': 'web', 
    'web_location': '1550101',  # Web 端的用户位置（后来改成web鉴权方式，要用到web签名）
}

# 请求头（模拟浏览器请求）
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}

# 请求cookie (需要登录B站获取的SESSDATA值)
cookies = {
    'SESSDATA': '7d9aa5c8%2C1748865845%2Cf39ad%2Ac1CjApkQ'  # 请替换为你自己的 SESSDATA
}

# 发送请求
response = requests.get(url, params=params, headers=headers, cookies=cookies)

# 检查请求是否成功
if response.status_code == 200:
    data = response.json()

    if data['code'] == 0:
        # 获取 UP 主的视频列表
        video_list = data['data']['list']['vlist']
        
        # 格式化输出为字典
        videos_dict = {video['title']: video['bvid'] for video in video_list}
        
        # 打印字典
        print(videos_dict)
    else:
        print(f"请求失败，错误信息：{data['message']}")
else:
    print(f"请求失败，状态码: {response.status_code}")
