#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GetQuicker用户动作数据统计工具
获取用户所有公开动作数据并统计点赞总数
"""

import requests
import json
import sys
import logging
import time
import pandas as pd
from lxml import html
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin


def setup_logger(debug: bool = False) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        debug (bool): 是否启用调试模式
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger('getquicker_actions_stats')
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


def get_page_content(url: str, logger: logging.Logger) -> Optional[str]:
    """
    获取页面HTML内容
    
    Args:
        url (str): 目标URL
        logger (logging.Logger): 日志记录器
    
    Returns:
        Optional[str]: 页面HTML内容，失败返回None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Referer': 'https://getquicker.net/Share',
    }
    
    try:
        logger.debug(f"正在访问: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.debug(f"✅ 成功获取页面！状态码: {response.status_code}")
            return response.text
        else:
            logger.error(f"❌ 获取页面失败！状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 请求异常: {e}")
        return None


def extract_actions_using_pandas(html_content: str, logger: logging.Logger) -> List[Dict[str, any]]:
    """
    使用pandas解析HTML表格中的动作数据
    
    Args:
        html_content (str): 页面HTML内容
        logger (logging.Logger): 日志记录器
    
    Returns:
        List[Dict[str, any]]: 动作数据列表
    """
    try:
        # 使用pandas读取HTML表格
        from io import StringIO
        tables = pd.read_html(StringIO(html_content))
        
        if not tables:
            logger.warning("❌ 未找到任何表格")
            return []
        
        # 找到动作表格（通常是第一个表格）
        action_table = tables[0]
        logger.info(f"✅ 找到表格，包含 {len(action_table)} 行数据")
        
        # 显示表格结构
        logger.debug(f"表格列名: {list(action_table.columns)}")
        logger.debug(f"表格形状: {action_table.shape}")
        
        actions = []
        
        # 处理每一行数据
        for index, row in action_table.iterrows():
            try:
                action_data = {}
                
                # 根据实际表格结构调整列映射
                # 根据之前的调试结果，表格结构是：
                # 第1列: 空
                # 第2列: 名称
                # 第3列: 适用于
                # 第4列: 分享人
                # 第5列: 大小
                # 第6列: 获赞（点赞数）
                # 第7列: 用户（下载数）
                # 第8列: 频度
                
                if len(row) >= 8:
                    # 获取完整的名称字段（包含动作名称和描述）
                    full_name = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
                    
                    # 尝试分离动作名称和描述
                    # 通常动作名称和描述用空格分隔，描述部分包含更多文字
                    name_parts = full_name.split('  ', 1)  # 最多分割一次
                    if len(name_parts) > 1:
                        action_data['name'] = name_parts[0].strip()
                        action_data['description'] = name_parts[1].strip()
                    else:
                        action_data['name'] = full_name.strip()
                        action_data['description'] = ''
                    
                    action_data['applicable'] = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ''
                    action_data['author'] = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ''
                    action_data['size'] = str(row.iloc[4]) if pd.notna(row.iloc[4]) else ''
                    
                    # 点赞数（第6列）
                    likes_value = row.iloc[5]
                    try:
                        if pd.notna(likes_value):
                            # 处理浮点数或整数
                            if isinstance(likes_value, (int, float)):
                                action_data['likes'] = int(likes_value)
                            else:
                                likes_text = str(likes_value).strip()
                                # 尝试转换为浮点数再转为整数
                                action_data['likes'] = int(float(likes_text))
                        else:
                            action_data['likes'] = 0
                    except (ValueError, TypeError):
                        action_data['likes'] = 0
                    
                    # 下载数（第7列）
                    downloads_value = row.iloc[6]
                    try:
                        if pd.notna(downloads_value):
                            # 处理浮点数或整数
                            if isinstance(downloads_value, (int, float)):
                                action_data['downloads'] = int(downloads_value)
                            else:
                                downloads_text = str(downloads_value).strip()
                                # 尝试转换为浮点数再转为整数
                                action_data['downloads'] = int(float(downloads_text))
                        else:
                            action_data['downloads'] = 0
                    except (ValueError, TypeError):
                        action_data['downloads'] = 0
                    
                    # 频度（第8列）
                    action_data['frequency'] = str(row.iloc[7]) if pd.notna(row.iloc[7]) else ''
                    
                    # 过滤掉表头行（通常包含"名称"、"适用于"等）
                    if not any(keyword in action_data['name'] for keyword in ['名称', '适用于', '分享人']):
                        actions.append(action_data)
                        logger.debug(f"提取动作: {action_data['name']} - 点赞: {action_data['likes']}")
                
            except Exception as e:
                logger.debug(f"处理第 {index+1} 行时出错: {e}")
                continue
        
        logger.info(f"✅ 成功提取 {len(actions)} 个动作数据")
        return actions
        
    except Exception as e:
        logger.error(f"❌ 使用pandas解析表格时出错: {e}")
        return []


def extract_actions_using_lxml(html_content: str, logger: logging.Logger) -> List[Dict[str, any]]:
    """
    使用lxml解析HTML表格中的动作数据（备用方法）
    
    Args:
        html_content (str): 页面HTML内容
        logger (logging.Logger): 日志记录器
    
    Returns:
        List[Dict[str, any]]: 动作数据列表
    """
    try:
        # 使用lxml解析HTML
        tree = html.fromstring(html_content)
        
        # 查找表格
        tables = tree.xpath('//table[@class="table table-bordered table-sm table-hover"]')
        
        if not tables:
            logger.warning("❌ 未找到动作表格")
            return []
        
        table = tables[0]
        actions = []
        
        # 查找所有行
        rows = table.xpath('.//tr')
        logger.info(f"找到 {len(rows)} 行数据")
        
        for i, row in enumerate(rows):
            try:
                # 获取所有单元格
                cells = row.xpath('.//td | .//th')
                
                if len(cells) >= 8:
                    action_data = {}
                    
                    # 提取文本内容
                    cell_texts = [cell.text_content().strip() for cell in cells]
                    
                    # 获取完整的名称字段（包含动作名称和描述）
                    full_name = cell_texts[1] if len(cell_texts) > 1 else ''
                    
                    # 尝试分离动作名称和描述
                    name_parts = full_name.split('  ', 1)  # 最多分割一次
                    if len(name_parts) > 1:
                        action_data['name'] = name_parts[0].strip()
                        action_data['description'] = name_parts[1].strip()
                    else:
                        action_data['name'] = full_name.strip()
                        action_data['description'] = ''
                    
                    action_data['applicable'] = cell_texts[2] if len(cell_texts) > 2 else ''
                    action_data['author'] = cell_texts[3] if len(cell_texts) > 3 else ''
                    action_data['size'] = cell_texts[4] if len(cell_texts) > 4 else ''
                    
                    # 点赞数
                    likes_text = cell_texts[5] if len(cell_texts) > 5 else '0'
                    try:
                        if likes_text and likes_text.strip():
                            # 尝试转换为浮点数再转为整数
                            action_data['likes'] = int(float(likes_text))
                        else:
                            action_data['likes'] = 0
                    except (ValueError, TypeError):
                        action_data['likes'] = 0
                    
                    # 下载数
                    downloads_text = cell_texts[6] if len(cell_texts) > 6 else '0'
                    try:
                        if downloads_text and downloads_text.strip():
                            # 尝试转换为浮点数再转为整数
                            action_data['downloads'] = int(float(downloads_text))
                        else:
                            action_data['downloads'] = 0
                    except (ValueError, TypeError):
                        action_data['downloads'] = 0
                    
                    # 频度
                    action_data['frequency'] = cell_texts[7] if len(cell_texts) > 7 else ''
                    
                    # 过滤掉表头行
                    if not any(keyword in action_data['name'] for keyword in ['名称', '适用于', '分享人']):
                        actions.append(action_data)
                        logger.debug(f"提取动作: {action_data['name']} - 点赞: {action_data['likes']}")
                
            except Exception as e:
                logger.debug(f"处理第 {i+1} 行时出错: {e}")
                continue
        
        logger.info(f"✅ 成功提取 {len(actions)} 个动作数据")
        return actions
        
    except Exception as e:
        logger.error(f"❌ 使用lxml解析表格时出错: {e}")
        return []


def get_total_pages(html_content: str, logger: logging.Logger) -> int:
    """
    获取总页数
    
    Args:
        html_content (str): 页面HTML内容
        logger (logging.Logger): 日志记录器
    
    Returns:
        int: 总页数，如果无法获取则返回1
    """
    try:
        tree = html.fromstring(html_content)
        
        # 查找分页导航中的页码链接
        page_links = tree.xpath('//nav//ul//li/a/text()')
        max_page = 1
        
        for link_text in page_links:
            try:
                if link_text.strip().isdigit():
                    page_num = int(link_text.strip())
                    max_page = max(max_page, page_num)
            except ValueError:
                continue
        
        logger.info(f"✅ 检测到总页数: {max_page}")
        return max_page
        
    except Exception as e:
        logger.debug(f"获取总页数时出错: {e}")
        return 1


def get_all_user_actions(user_id: str, logger: logging.Logger) -> Tuple[List[Dict[str, any]], Dict[str, any]]:
    """
    获取用户所有公开动作数据
    
    Args:
        user_id (str): 用户ID
        logger (logging.Logger): 日志记录器
    
    Returns:
        Tuple[List[Dict[str, any]], Dict[str, any]]: (动作列表, 统计信息)
    """
    base_url = f"https://getquicker.net/User/Actions/{user_id}"
    all_actions = []
    stats = {
        'total_actions': 0,
        'total_likes': 0,
        'total_downloads': 0,
        'total_pages': 0,
        'avg_likes': 0,
        'avg_downloads': 0
    }
    
    # 获取第一页并确定总页数
    logger.info("正在获取第1页...")
    first_page_content = get_page_content(base_url, logger)
    
    if not first_page_content:
        logger.error("❌ 无法获取第一页内容")
        return all_actions, stats
    
    total_pages = get_total_pages(first_page_content, logger)
    stats['total_pages'] = total_pages
    
    # 尝试使用pandas解析第一页
    first_page_actions = extract_actions_using_pandas(first_page_content, logger)
    
    # 如果pandas失败，使用lxml作为备用
    if not first_page_actions:
        logger.info("pandas解析失败，尝试使用lxml...")
        first_page_actions = extract_actions_using_lxml(first_page_content, logger)
    
    all_actions.extend(first_page_actions)
    
    # 获取剩余页面
    for page in range(2, total_pages + 1):
        logger.info(f"正在获取第{page}页...")
        page_url = f"{base_url}?p={page}"  # 注意：这里使用 ?p= 而不是 ?page=
        page_content = get_page_content(page_url, logger)
        
        if page_content:
            page_actions = extract_actions_using_pandas(page_content, logger)
            if not page_actions:
                page_actions = extract_actions_using_lxml(page_content, logger)
            all_actions.extend(page_actions)
        else:
            logger.warning(f"❌ 无法获取第{page}页内容")
        
        # 添加延迟避免请求过快
        time.sleep(1)
    
    # 统计信息
    stats['total_actions'] = len(all_actions)
    
    for action in all_actions:
        # 统计点赞数
        likes_count = action.get('likes', 0)
        stats['total_likes'] += likes_count
        
        # 统计下载数
        downloads_count = action.get('downloads', 0)
        stats['total_downloads'] += downloads_count
    
    # 计算平均值
    if stats['total_actions'] > 0:
        stats['avg_likes'] = round(stats['total_likes'] / stats['total_actions'], 2)
        stats['avg_downloads'] = round(stats['total_downloads'] / stats['total_actions'], 2)
    
    return all_actions, stats


def save_results(actions: List[Dict[str, any]], stats: Dict[str, any], user_id: str, logger: logging.Logger):
    """
    保存结果到文件
    
    Args:
        actions (List[Dict[str, any]]): 动作列表
        stats (Dict[str, any]): 统计信息
        user_id (str): 用户ID
        logger (logging.Logger): 日志记录器
    """
    try:
        # 保存详细动作数据
        actions_filename = f"user_actions_{user_id.replace('-', '_')}.json"
        with open(actions_filename, 'w', encoding='utf-8') as f:
            json.dump(actions, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 动作数据已保存到: {actions_filename}")
        
        # 保存统计信息
        stats_filename = f"user_stats_{user_id.replace('-', '_')}.json"
        with open(stats_filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 统计信息已保存到: {stats_filename}")
        
        # 注意：不保存单独的CSV文件，统一在推荐作者统计中保存
        
    except Exception as e:
        logger.error(f"❌ 保存文件时出错: {e}")


def print_summary(actions: List[Dict[str, any]], stats: Dict[str, any], logger: logging.Logger):
    """
    打印统计摘要
    
    Args:
        actions (List[Dict[str, any]]): 动作列表
        stats (Dict[str, any]): 统计信息
        logger (logging.Logger): 日志记录器
    """
    logger.info("=" * 60)
    logger.info("📊 统计摘要")
    logger.info("=" * 60)
    logger.info(f"总动作数: {stats['total_actions']}")
    logger.info(f"总页数: {stats['total_pages']}")
    logger.info(f"总点赞数: {stats['total_likes']}")
    logger.info(f"总下载数: {stats['total_downloads']}")
    logger.info(f"平均点赞数: {stats['avg_likes']}")
    logger.info(f"平均下载数: {stats['avg_downloads']}")
    
    logger.info("\n🏆 点赞数最高的动作:")
    top_actions = sorted(actions, key=lambda x: x.get('likes', 0), reverse=True)[:5]
    for i, action in enumerate(top_actions, 1):
        logger.info(f"  {i}. {action.get('name', 'Unknown')} - {action.get('likes', 0)} 点赞")


def main():
    """主函数"""
    # 解析命令行参数
    debug_mode = '--debug' in sys.argv
    if '--debug' in sys.argv:
        sys.argv.remove('--debug')
    
    # 设置日志记录器
    logger = setup_logger(debug=debug_mode)
    
    logger.info("=" * 60)
    logger.info("GetQuicker用户动作数据统计工具")
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
    
    # 获取所有动作数据
    logger.info("开始获取用户所有公开动作数据...")
    actions, stats = get_all_user_actions(user_id, logger)
    
    if not actions:
        logger.error("❌ 未获取到任何动作数据")
        return
    
    logger.info("-" * 60)
    
    # 打印统计摘要
    print_summary(actions, stats, logger)
    
    logger.info("-" * 60)
    
    # 保存结果
    logger.info("正在保存结果...")
    save_results(actions, stats, user_id, logger)
    
    logger.info("-" * 60)
    logger.info("🎉 任务完成！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
