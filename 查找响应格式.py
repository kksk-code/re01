import requests
#12.5. 20:24
#失败，运用api.bilibili.com/x/space/wbi/arc/search接口，获取不了
#web鉴权
import requests
from bilibili_api import sync

async def get_bilibili_data():
    # 设置请求的相关参数
    mid = "3546771443681290"
    url = f"https://api.bilibili.com/x/space/wbi/arc/search?mid={mid}&ps=30&pn=1&tid=0&keyword=&order=pubdate&jsonp=jsonp"
    
    # 使用 Bilibili API 客户端
    result = await sync.get_bilibili_api_data(url)
    print(result)

# 异步调用
import asyncio
asyncio.run(get_bilibili_data())

