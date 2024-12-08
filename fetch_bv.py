#12.3日，由队友云创建，本意是想一步步搞懂爬虫的基本原理层，这个代码是爬取网页数据用的。
#结果：失败，原因：web鉴权
#我猜是因为调用网页数据的方法不对，网页get请求不到信息
import requests

# API URL
url = "https://api.bilibili.com/x/space/wbi/arc/search?mid=3546771443681290"

# 自定义请求头
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/json',
        
    }

# 调用 GET API
response = requests.get(url, headers=headers)

# 检查响应状态码
if response.status_code == 200:
    # 解析响应数据
    print("Response Data:", response.json())  # 如果返回 JSON 数据
else:
    print("Failed to fetch data. Status code:", response.status_code)
    print("Error message:", response.text)
