#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GetQuicker推荐页面作者统计工具
从推荐页面提取作者信息，获取每个作者的统计数据
"""

import requests
import json
import sys
import logging
import time
import pandas as pd
import re
from lxml import html
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
from get_user_actions import get_all_user_actions, setup_logger


def get_recommended_page_content(logger: logging.Logger) -> Optional[str]:
    """
    获取推荐页面HTML内容
    
    Args:
        logger (logging.Logger): 日志记录器
    
    Returns:
        Optional[str]: 页面HTML内容，失败返回None
    """
    url = "https://getquicker.net/Share/Recommended"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Referer': 'https://getquicker.net/Share',
    }
    
    try:
        logger.debug(f"正在访问推荐页面: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.debug(f"✅ 成功获取推荐页面！状态码: {response.status_code}")
            return response.text
        else:
            logger.error(f"❌ 获取推荐页面失败！状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 请求异常: {e}")
        return None


def extract_authors_from_recommended(html_content: str, logger: logging.Logger) -> List[Dict[str, str]]:
    """
    从推荐页面HTML中提取作者信息
    
    Args:
        html_content (str): 页面HTML内容
        logger (logging.Logger): 日志记录器
    
    Returns:
        List[Dict[str, str]]: 作者信息列表
    """
    try:
        tree = html.fromstring(html_content)
        authors = []
        
        # 查找所有作者链接
        # 根据页面结构，作者链接通常在表格中的分享人列
        author_links = tree.xpath('//a[contains(@href, "/User/")]')
        
        logger.info(f"找到 {len(author_links)} 个作者链接")
        
        for link in author_links:
            try:
                href = link.get('href', '')
                if '/User/' in href:
                    # 提取用户ID - 只取数字部分，去掉用户名
                    full_id = href.split('/User/')[-1].split('?')[0].split('#')[0]
                    # 如果包含用户名（如 113342/Cea），只取数字部分
                    if '/' in full_id:
                        user_id = full_id.split('/')[0] + '-'  # 添加连字符
                    else:
                        user_id = full_id
                    author_name = link.text_content().strip()
                    
                    # 避免重复
                    if not any(author['user_id'] == user_id for author in authors):
                        authors.append({
                            'user_id': user_id,
                            'author_name': author_name,
                            'profile_url': f"https://getquicker.net{href}"
                        })
                        logger.debug(f"提取作者: {author_name} (ID: {user_id})")
                
            except Exception as e:
                logger.debug(f"处理作者链接时出错: {e}")
                continue
        
        logger.info(f"✅ 成功提取 {len(authors)} 个唯一作者")
        return authors
        
    except Exception as e:
        logger.error(f"❌ 提取作者信息时出错: {e}")
        return []


def get_author_stats(author: Dict[str, str], logger: logging.Logger) -> Dict[str, any]:
    """
    获取单个作者的统计数据
    
    Args:
        author (Dict[str, str]): 作者信息
        logger (logging.Logger): 日志记录器
    
    Returns:
        Dict[str, any]: 作者统计数据
    """
    try:
        logger.info(f"正在获取作者 {author['author_name']} (ID: {author['user_id']}) 的统计数据...")
        
        # 使用现有的get_all_user_actions函数
        actions, stats = get_all_user_actions(author['user_id'], logger)
        
        # 构建作者统计信息
        author_stats = {
            'user_id': author['user_id'],
            'author_name': author['author_name'],
            'profile_url': author['profile_url'],
            'total_actions': stats['total_actions'],
            'total_likes': stats['total_likes'],
            'total_downloads': stats['total_downloads'],
            'total_pages': stats['total_pages'],
            'avg_likes': stats['avg_likes'],
            'avg_downloads': stats['avg_downloads'],
            'extraction_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"✅ {author['author_name']} - 动作数: {stats['total_actions']}, 总点赞: {stats['total_likes']}, 总下载: {stats['total_downloads']}")
        return author_stats
        
    except Exception as e:
        logger.error(f"❌ 获取作者 {author['author_name']} 统计数据时出错: {e}")
        return {
            'user_id': author['user_id'],
            'author_name': author['author_name'],
            'profile_url': author['profile_url'],
            'total_actions': 0,
            'total_likes': 0,
            'total_downloads': 0,
            'total_pages': 0,
            'avg_likes': 0,
            'avg_downloads': 0,
            'extraction_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e)
        }


def save_authors_stats_to_csv(authors_stats: List[Dict[str, any]], logger: logging.Logger):
    """
    将所有作者的统计数据保存到CSV文件
    
    Args:
        authors_stats (List[Dict[str, any]]): 作者统计数据列表
        logger (logging.Logger): 日志记录器
    """
    try:
        if not authors_stats:
            logger.warning("❌ 没有作者统计数据可保存")
            return
        
        # 创建DataFrame
        df = pd.DataFrame(authors_stats)
        
        # 重新排列列的顺序
        columns_order = [
            'author_name', 'user_id', 'profile_url', 'total_actions', 
            'total_likes', 'total_downloads', 'avg_likes', 'avg_downloads', 
            'total_pages', 'extraction_time'
        ]
        
        # 只包含存在的列
        existing_columns = [col for col in columns_order if col in df.columns]
        df = df[existing_columns]
        
        # 保存为CSV - 使用统一的文件名
        csv_filename = "recommended_authors_stats.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        
        logger.info(f"✅ 所有作者统计数据已保存到: {csv_filename}")
        logger.info(f"📊 共统计了 {len(authors_stats)} 个作者")
        
        # 显示统计摘要
        if len(authors_stats) > 0:
            total_actions = sum(author.get('total_actions', 0) for author in authors_stats)
            total_likes = sum(author.get('total_likes', 0) for author in authors_stats)
            total_downloads = sum(author.get('total_downloads', 0) for author in authors_stats)
            
            logger.info("=" * 60)
            logger.info("📊 推荐作者统计摘要")
            logger.info("=" * 60)
            logger.info(f"作者总数: {len(authors_stats)}")
            logger.info(f"总动作数: {total_actions}")
            logger.info(f"总点赞数: {total_likes}")
            logger.info(f"总下载数: {total_downloads}")
            
            # 显示点赞数最高的作者
            top_authors = sorted(authors_stats, key=lambda x: x.get('total_likes', 0), reverse=True)[:5]
            logger.info("\n🏆 点赞数最高的作者:")
            for i, author in enumerate(top_authors, 1):
                logger.info(f"  {i}. {author.get('author_name', 'Unknown')} - {author.get('total_likes', 0)} 点赞")
        
    except Exception as e:
        logger.error(f"❌ 保存CSV文件时出错: {e}")


def main():
    """主函数"""
    # 解析命令行参数
    debug_mode = '--debug' in sys.argv
    if '--debug' in sys.argv:
        sys.argv.remove('--debug')
    
    # 设置日志记录器
    logger = setup_logger(debug=debug_mode)
    
    logger.info("=" * 60)
    logger.info("GetQuicker推荐页面作者统计工具")
    logger.info("=" * 60)
    
    logger.debug(f"调试模式: {'启用' if debug_mode else '禁用'}")
    logger.info("-" * 60)
    
    # 第一步：获取推荐页面内容
    logger.info("步骤1: 获取推荐页面...")
    html_content = get_recommended_page_content(logger)
    
    if not html_content:
        logger.error("❌ 无法获取推荐页面内容，程序退出")
        return
    
    logger.info("-" * 60)
    
    # 第二步：提取作者信息
    logger.info("步骤2: 提取作者信息...")
    authors = extract_authors_from_recommended(html_content, logger)
    
    if not authors:
        logger.error("❌ 未找到任何作者信息，程序退出")
        return
    
    logger.info("-" * 60)
    
    # 第三步：获取每个作者的统计数据
    logger.info("步骤3: 获取作者统计数据...")
    authors_stats = []
    
    for i, author in enumerate(authors, 1):
        logger.info(f"进度: {i}/{len(authors)}")
        author_stats = get_author_stats(author, logger)
        authors_stats.append(author_stats)
        
        # 添加延迟避免请求过快
        if i < len(authors):
            logger.debug("等待1秒...")
            time.sleep(1)
    
    logger.info("-" * 60)
    
    # 第四步：保存结果到CSV
    logger.info("步骤4: 保存统计数据...")
    save_authors_stats_to_csv(authors_stats, logger)
    
    logger.info("-" * 60)
    logger.info("🎉 任务完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
