# GetQuicker 用户信息获取工具

这是一个用于获取 GetQuicker 用户信息和动作数据的 Python 工具集。

## 🎯 功能特性

### 📝 用户信息获取 (`get_user_info.py`)
- 提取用户基本信息：用户名、推荐码、注册天数、专业版状态
- 绕过访问限制，使用正确的 Referer 头
- 多种提取方法：CSS选择器 + 正则表达式双重保障
- 不保存HTML文件，仅在内存中处理

### 📊 用户动作数据统计 (`get_user_actions.py`)
- 获取用户所有公开动作数据
- 统计总点赞数、下载数等信息
- 支持多页数据自动翻页
- 使用 pandas 和 lxml 高效解析HTML表格
- 输出多种格式：JSON、CSV

## 🚀 快速开始

### 安装依赖

使用 uv（推荐）：
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync
```

### 基本使用

1. **获取用户基本信息**：
```bash
# 使用默认用户ID
uv run python get_user_info.py

# 指定用户ID
uv run python get_user_info.py 123456-

# 指定用户主页URL
uv run python get_user_info.py https://getquicker.net/User/123456-

# 启用调试模式
uv run python get_user_info.py --debug
```

2. **获取用户动作数据**：
```bash
# 获取所有动作数据并统计
uv run python get_user_actions.py

# 指定用户ID
uv run python get_user_actions.py 123456-

# 指定用户主页URL
uv run python get_user_actions.py https://getquicker.net/User/Actions/123456-
uv run python get_user_actions.py https://getquicker.net/User/123456-

# 启用调试模式
uv run python get_user_actions.py --debug
```

## 📄 输出文件

### 用户信息
- `user_info_{user_id}.json` - 用户基本信息

### 动作数据
- `user_actions_{user_id}.json` - 详细动作数据
- `user_actions_{user_id}.csv` - CSV格式数据（便于Excel查看）
- `user_stats_{user_id}.json` - 统计信息

## 🔧 技术实现

### 绕过访问限制
GetQuicker服务器只允许从内部跳转访问用户页面，通过添加正确的 Referer 头解决：
```http
Referer: https://getquicker.net/Share
```

### HTML表格解析
使用多种库提供最佳解析效果：
- **pandas** - 主要解析方法，自动识别表格结构
- **lxml** - 备用解析方法，高性能XPath支持
- **BeautifulSoup** - CSS选择器支持

## 📊 示例输出

### 统计摘要
```
============================================================
📊 统计摘要
============================================================
总动作数: 94
总页数: 4
总点赞数: 6,672
总下载数: 86,373
平均点赞数: 70.98
平均下载数: 918.86

🏆 点赞数最高的动作:
  1. 剪贴板记录文件 - 5,510 点赞
  2. 捷径面板3.0 - 235 点赞
  3. 超级菜单 - 160 点赞
```

## 🛡️ 隐私保护

- 生成的用户数据文件已添加到 `.gitignore`
- 不会将个人数据提交到代码仓库
- HTML内容仅在内存中处理，不保存到磁盘

## 📚 更多资源

- [HTML表格解析库说明](HTML_TABLE_LIBRARIES.md) - 详细的库选择和使用指南
- [任务说明](task.md) - 开发任务和需求

## 🔄 更新日志

- **v2.0** - 添加动作数据统计功能，使用pandas+lxml解析
- **v1.0** - 基础用户信息获取功能
