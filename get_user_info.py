#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GetQuicker用户信息获取完整工具
自动获取页面并提取用户信息
"""

import requests
import re
import json
import sys
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional


def setup_logger(debug: bool = False) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        debug (bool): 是否启用调试模式
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建logger
    logger = logging.getLogger('getquicker_user_info')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # 创建格式化器
    if debug:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter('%(message)s')
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_user_page(user_id: str, logger: logging.Logger) -> Optional[str]:
    """
    获取用户页面HTML内容
    
    Args:
        user_id (str): 用户ID，例如 "113342-"
        logger (logging.Logger): 日志记录器
    
    Returns:
        Optional[str]: 页面HTML内容，失败返回None
    """
    url = f"https://getquicker.net/User/Actions/{user_id}"
    
    # 关键：使用正确的Referer头绕过安全限制
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Referer': 'https://getquicker.net/Share'  # 这是关键！
    }
    
    logger.info(f"正在访问: {url}")
    logger.debug(f"使用Referer: {headers['Referer']}")
    logger.debug(f"请求头: {headers}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        logger.debug(f"响应状态码: {response.status_code}")
        logger.debug(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            logger.info(f"✅ 成功获取页面！状态码: {response.status_code}")
            logger.debug(f"响应内容长度: {len(response.text)} 字符")
            return response.text
        else:
            logger.error(f"❌ 获取页面失败！状态码: {response.status_code}")
            logger.debug(f"错误响应内容: {response.text[:200]}...")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 请求异常: {e}")
        return None


def extract_user_info(html_content: str, logger: logging.Logger) -> Dict[str, any]:
    """
    从HTML内容中提取用户信息
    
    Args:
        html_content (str): 页面的HTML内容
        logger (logging.Logger): 日志记录器
    
    Returns:
        Dict[str, any]: 包含用户信息的字典
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    user_info = {}
    
    try:
        logger.debug("开始解析HTML内容...")
        
        # 1. 推荐码 - 使用CSS选择器
        referral_selector = 'body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > a.font14.text-secondary.cursor-pointer.mr-3'
        referral_element = soup.select_one(referral_selector)
        if referral_element:
            user_info['referral_code'] = referral_element.get_text(strip=True)
            logger.info(f"✅ 推荐码: {user_info['referral_code']}")
            logger.debug(f"推荐码选择器: {referral_selector}")
        else:
            logger.warning("❌ 未找到推荐码")
            logger.debug(f"推荐码选择器未匹配: {referral_selector}")
            user_info['referral_code'] = None
        
        # 2. 注册天数 - 使用CSS选择器
        days_selector = 'body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > span.text-muted.mr-3'
        days_element = soup.select_one(days_selector)
        if days_element:
            user_info['registration_days'] = days_element.get_text(strip=True)
            logger.info(f"✅ 注册天数: {user_info['registration_days']}")
            logger.debug(f"注册天数选择器: {days_selector}")
        else:
            logger.warning("❌ 未找到注册天数")
            logger.debug(f"注册天数选择器未匹配: {days_selector}")
            user_info['registration_days'] = None
        
        # 3. 专业版标识 - 使用CSS选择器
        pro_selector = 'body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > span:nth-child(3) > i'
        pro_element = soup.select_one(pro_selector)
        if pro_element:
            user_info['is_pro_user'] = True
            logger.info("✅ 专业版用户: 是")
            logger.debug(f"专业版选择器: {pro_selector}")
        else:
            user_info['is_pro_user'] = False
            logger.info("❌ 专业版用户: 否")
            logger.debug(f"专业版选择器未匹配: {pro_selector}")
        
        # 4. 用户名
        username_selector = 'body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.mt-1 > span'
        username_element = soup.select_one(username_selector)
        if username_element:
            user_info['username'] = username_element.get_text(strip=True)
            logger.info(f"✅ 用户名: {user_info['username']}")
            logger.debug(f"用户名选择器: {username_selector}")
        else:
            logger.warning("❌ 未找到用户名")
            logger.debug(f"用户名选择器未匹配: {username_selector}")
            user_info['username'] = None
        
        # 5. 备用方法：使用正则表达式提取推荐码
        if not user_info['referral_code']:
            logger.debug("尝试使用正则表达式提取推荐码...")
            referral_pattern = r'Ta的推荐码：(\d+-\d+)'
            match = re.search(referral_pattern, html_content)
            if match:
                user_info['referral_code'] = match.group(1)
                logger.info(f"✅ 推荐码(备用方法): {user_info['referral_code']}")
                logger.debug(f"推荐码正则表达式: {referral_pattern}")
            else:
                logger.debug(f"推荐码正则表达式未匹配: {referral_pattern}")
        
        # 6. 备用方法：使用正则表达式提取注册天数
        if not user_info['registration_days']:
            logger.debug("尝试使用正则表达式提取注册天数...")
            days_pattern = r'(\d+天)'
            match = re.search(days_pattern, html_content)
            if match:
                user_info['registration_days'] = match.group(1)
                logger.info(f"✅ 注册天数(备用方法): {user_info['registration_days']}")
                logger.debug(f"注册天数正则表达式: {days_pattern}")
            else:
                logger.debug(f"注册天数正则表达式未匹配: {days_pattern}")
        
        # 7. 备用方法：检查专业版标识
        if not user_info['is_pro_user']:
            logger.debug("尝试使用文本搜索检查专业版标识...")
            if 'fas fa-crown' in html_content and 'pro-user-icon' in html_content:
                user_info['is_pro_user'] = True
                logger.info("✅ 专业版用户(备用方法): 是")
                logger.debug("在HTML中找到专业版标识文本")
            else:
                logger.debug("在HTML中未找到专业版标识文本")
        
        logger.debug(f"提取完成，用户信息: {user_info}")
        return user_info
        
    except Exception as e:
        logger.error(f"❌ 提取信息时出错: {e}")
        logger.debug(f"异常详情: {type(e).__name__}: {str(e)}")
        return {}


def save_results(user_info: Dict[str, any], user_id: str, logger: logging.Logger):
    """
    保存结果到文件（仅保存JSON，不保存HTML）
    
    Args:
        user_info (Dict[str, any]): 用户信息
        user_id (str): 用户ID
        logger (logging.Logger): 日志记录器
    """
    try:
        # 保存JSON结果
        json_filename = f"user_info_{user_id.replace('-', '_')}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(user_info, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 用户信息已保存到: {json_filename}")
        logger.debug(f"JSON文件大小: {len(json.dumps(user_info, ensure_ascii=False))} 字符")
        
        logger.info("ℹ️ HTML内容仅在内存中处理，未保存到文件")
            
    except Exception as e:
        logger.error(f"❌ 保存文件时出错: {e}")
        logger.debug(f"保存异常详情: {type(e).__name__}: {str(e)}")


def main():
    """主函数"""
    # 解析命令行参数
    debug_mode = '--debug' in sys.argv
    if '--debug' in sys.argv:
        sys.argv.remove('--debug')
    
    # 设置日志记录器
    logger = setup_logger(debug=debug_mode)
    
    logger.info("=" * 60)
    logger.info("GetQuicker用户信息获取完整工具")
    logger.info("=" * 60)
    
    # 默认用户ID
    default_user_id = "113342-"
    
    # 从命令行参数获取用户ID或URL
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
        
        # 检查是否是URL
        if user_input.startswith('http'):
            # 从URL中提取用户ID
            if '/User/Actions/' in user_input:
                user_id = user_input.split('/User/Actions/')[-1].split('?')[0].split('#')[0]
            elif '/User/' in user_input:
                user_id = user_input.split('/User/')[-1].split('?')[0].split('#')[0]
            else:
                logger.error("❌ 无法从URL中提取用户ID")
                return
            logger.info(f"从URL提取用户ID: {user_id}")
        else:
            user_id = user_input
    else:
        user_id = default_user_id
        logger.info(f"使用默认用户ID: {user_id}")
    
    logger.info(f"目标用户: {user_id}")
    logger.debug(f"调试模式: {'启用' if debug_mode else '禁用'}")
    logger.info("-" * 60)
    
    # 第一步：获取页面内容
    logger.info("步骤1: 获取用户页面...")
    html_content = get_user_page(user_id, logger)
    
    if not html_content:
        logger.error("❌ 无法获取页面内容，程序退出")
        return
    
    logger.info("-" * 60)
    
    # 第二步：提取用户信息
    logger.info("步骤2: 提取用户信息...")
    user_info = extract_user_info(html_content, logger)
    
    if not user_info:
        logger.error("❌ 无法提取用户信息，程序退出")
        return
    
    logger.info("-" * 60)
    
    # 第三步：保存结果
    logger.info("步骤3: 保存结果...")
    save_results(user_info, user_id, logger)
    
    logger.info("-" * 60)
    logger.info("🎉 任务完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
