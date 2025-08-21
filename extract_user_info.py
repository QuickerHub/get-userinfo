#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GetQuicker用户信息提取脚本
从HTML页面中提取用户的推荐码、注册天数和专业版状态
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, Optional


def extract_user_info(html_content: str) -> Dict[str, any]:
    """
    从HTML内容中提取用户信息
    
    Args:
        html_content (str): 页面的HTML内容
    
    Returns:
        Dict[str, any]: 包含用户信息的字典
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    user_info = {}
    
    try:
        # 1. 推荐码 - 使用CSS选择器
        referral_element = soup.select_one('body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > a.font14.text-secondary.cursor-pointer.mr-3')
        if referral_element:
            user_info['referral_code'] = referral_element.get_text(strip=True)
            print(f"✅ 推荐码: {user_info['referral_code']}")
        else:
            print("❌ 未找到推荐码")
            user_info['referral_code'] = None
        
        # 2. 注册天数 - 使用CSS选择器
        days_element = soup.select_one('body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > span.text-muted.mr-3')
        if days_element:
            user_info['registration_days'] = days_element.get_text(strip=True)
            print(f"✅ 注册天数: {user_info['registration_days']}")
        else:
            print("❌ 未找到注册天数")
            user_info['registration_days'] = None
        
        # 3. 专业版标识 - 使用CSS选择器
        pro_element = soup.select_one('body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > span:nth-child(3) > i')
        if pro_element:
            user_info['is_pro_user'] = True
            print("✅ 专业版用户: 是")
        else:
            user_info['is_pro_user'] = False
            print("❌ 专业版用户: 否")
        
        # 4. 用户名
        username_element = soup.select_one('body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.mt-1 > span')
        if username_element:
            user_info['username'] = username_element.get_text(strip=True)
            print(f"✅ 用户名: {user_info['username']}")
        else:
            print("❌ 未找到用户名")
            user_info['username'] = None
        
        # 5. 备用方法：使用正则表达式提取推荐码
        if not user_info['referral_code']:
            referral_pattern = r'Ta的推荐码：(\d+-\d+)'
            match = re.search(referral_pattern, html_content)
            if match:
                user_info['referral_code'] = match.group(1)
                print(f"✅ 推荐码(备用方法): {user_info['referral_code']}")
        
        # 6. 备用方法：使用正则表达式提取注册天数
        if not user_info['registration_days']:
            days_pattern = r'(\d+天)'
            match = re.search(days_pattern, html_content)
            if match:
                user_info['registration_days'] = match.group(1)
                print(f"✅ 注册天数(备用方法): {user_info['registration_days']}")
        
        # 7. 备用方法：检查专业版标识
        if not user_info['is_pro_user']:
            if 'fas fa-crown' in html_content and 'pro-user-icon' in html_content:
                user_info['is_pro_user'] = True
                print("✅ 专业版用户(备用方法): 是")
        
        return user_info
        
    except Exception as e:
        print(f"❌ 提取信息时出错: {e}")
        return {}


def main():
    """主函数"""
    print("=" * 50)
    print("GetQuicker用户信息提取工具")
    print("=" * 50)
    
    # 从文件读取HTML内容
    try:
        with open('user_113342_.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 提取用户信息
        user_info = extract_user_info(html_content)
        
        if user_info:
            print("\n" + "=" * 50)
            print("提取结果:")
            print("=" * 50)
            for key, value in user_info.items():
                print(f"{key}: {value}")
            
            # 保存结果到JSON文件
            import json
            with open('user_info.json', 'w', encoding='utf-8') as f:
                json.dump(user_info, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 结果已保存到 user_info.json")
        else:
            print("❌ 未能提取到用户信息")
            
    except FileNotFoundError:
        print("❌ 未找到HTML文件，请先运行 simple_get_user.py 获取页面内容")
    except Exception as e:
        print(f"❌ 处理文件时出错: {e}")


if __name__ == "__main__":
    main()
