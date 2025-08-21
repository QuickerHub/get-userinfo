#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GetQuicker用户页面访问 - 最简化版本
关键：只需要正确的Referer头就能绕过安全限制
"""

import requests
import sys

def get_user_page(user_id):
    """
    获取用户页面 - 最简化版本
    
    Args:
        user_id (str): 用户ID，例如 "113342-"
    
    Returns:
        str: 页面HTML内容
    """
    
    url = f"https://getquicker.net/User/Actions/{user_id}"
    
    # 最简化的请求头 - 关键是Referer
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Referer': 'https://getquicker.net/Share'  # 这是关键！
    }
    
    print(f"访问: {url}")
    print(f"Referer: {headers['Referer']}")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ 成功！状态码: {response.status_code}")
        return response.text
    else:
        print(f"❌ 失败！状态码: {response.status_code}")
        return None

if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "113342-"
    
    print("=" * 40)
    print("GetQuicker用户页面访问工具")
    print("=" * 40)
    
    content = get_user_page(user_id)
    
    if content:
        # 保存文件
        filename = f"user_{user_id.replace('-', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已保存到: {filename}")
    else:
        print("❌ 获取失败")
