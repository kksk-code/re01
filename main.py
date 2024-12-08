import requests
import time
import json
import requests
#就终端那一次成功了，之后就没有成功过。。
from datetime import datetime
import random

def get_videos(uid, page_size=30):
    """
    获取指定用户的所有视频列表并按时间排序
    :param uid: 用户ID
    :param page_size: 每页视频数量
    :return: 包含所有视频信息的列表
    """
    base_url = "https://api.bilibili.com/x/space/wbi/arc/search"
   
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'application/json','SESSDATA': 'b4c46ab5%2C1748612005%2C9a2d8%2Ac1CjCw'
}


    videos = []
    page = 1  # 从第一页开始

    while True:
        print(f"正在抓取第 {page} 页数据...")
        params = {
            "mid": uid,
            "ps": page_size,
            "pn": page,
            "tid": 0,
            "keyword": "",
            "order": "pubdate",
            "jsonp": "jsonp"
        }
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()

            # 如果返回状态码为 429，说明请求过多，需要休息
            if response.status_code == 429:
                print("遇到请求限制，等待一段时间后重试...")
                time.sleep(random.randint(10, 30))  # 随机等待 10 到 30 秒
                continue

            data = response.json()

            # 检查是否有视频列表
            video_list = data.get("data", {}).get("list", {}).get("vlist", [])
            if not video_list:  # 没有更多数据
                print("所有视频数据抓取完毕。")
                break

            # 收集视频信息
            for video in video_list:
                created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(video.get("created")))
                videos.append({
                    "title": video.get("title"),
                    "bvid": video.get("bvid"),
                    "aid": video.get("aid"),
            
                    "url": f"https://www.bilibili.com/video/{video.get('bvid')}"
                })

            # 下一页
            page += 1

            # 在每次请求之间引入随机延迟，避免被封号
            sleep_time = random.uniform(2, 5)  # 随机延迟 2 到 5 秒
            print(f"等待 {sleep_time:.2f} 秒以避免被封号...")
            time.sleep(sleep_time)

        except requests.exceptions.RequestException as e:
            print(f"抓取时出现错误：{e}")
            break

    # 按时间降序排序
    videos.sort(key=lambda x: x['created'], reverse=True)
    return videos


def get_video_data(uid):
    """
    获取指定用户的所有视频信息
    :param uid: 用户ID
    :return: 视频信息的列表（返回值为 JSON 格式的数据）
    """
    print(f"开始抓取用户 {uid} 的视频列表...")
    videos = get_videos(uid)

    # 返回抓取到的视频数据
    return videos


# 固定用户ID
UID = 3546771443681290

# 调用获取视频数据的函数
video_data = get_video_data(UID)

# 输出结果
if video_data:
    print(f"共抓取到 {len(video_data)} 个视频。")
    for video in video_data:
        print(f"发布时间: {video['created']}, 标题: {video['title']}, BV号: {video['bvid']}, URL: {video['url']}")
else:
    print("未找到任何视频。")


