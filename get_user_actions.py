#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GetQuicker用户动作页面访问脚本
绕过服务器安全限制：只能从getquicker.net内部跳转访问
"""

import requests
import sys
from urllib.parse import urljoin

def get_user_actions(user_id):
    """
    获取指定用户的动作页面
    
    Args:
        user_id (str): 用户ID，例如 "113342-"
    
    Returns:
        str: 页面HTML内容，如果失败返回None
    """
    
    # 目标URL
    target_url = f"https://getquicker.net/User/Actions/{user_id}"
    
    # 设置请求头，关键是要有正确的Referer
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Referer': 'https://getquicker.net/Share',  # 关键：模拟从动作库页面跳转
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        print(f"正在访问: {target_url}")
        print(f"使用Referer: {headers['Referer']}")
        
        # 发送请求
        response = requests.get(target_url, headers=headers, timeout=10)
        
        # 检查响应状态
        if response.status_code == 200:
            print(f"✅ 成功访问！状态码: {response.status_code}")
            return response.text
        else:
            print(f"❌ 访问失败！状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return None

def main():
    """主函数"""
    
    # 默认用户ID
    default_user_id = "113342-"
    
    # 从命令行参数获取用户ID，如果没有提供则使用默认值
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = default_user_id
        print(f"使用默认用户ID: {user_id}")
    
    print("=" * 50)
    print("GetQuicker用户动作页面访问工具")
    print("=" * 50)
    
    # 获取页面内容
    html_content = get_user_actions(user_id)
    
    if html_content:
        # 保存到文件
        filename = f"user_actions_{user_id.replace('-', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 页面内容已保存到: {filename}")
        print(f"文件大小: {len(html_content)} 字符")
        
        # 简单的内容分析
        if "Cea" in html_content:
            print("✅ 页面包含用户信息")
        if "动作" in html_content:
            print("✅ 页面包含动作列表")
            
    else:
        print("❌ 获取页面失败")

if __name__ == "__main__":
    main()
