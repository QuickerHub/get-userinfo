# GetQuicker用户信息获取工具

这个工具可以绕过GetQuicker网站的安全限制，自动获取用户页面并提取关键信息。

## 项目特性

- ✅ **绕过安全限制**：使用正确的Referer头绕过服务器限制
- ✅ **自动信息提取**：提取推荐码、注册天数、专业版状态等
- ✅ **多种提取方法**：CSS选择器 + 正则表达式备用方案
- ✅ **完整自动化**：一键获取页面并提取信息
- ✅ **环境管理**：使用uv进行Python环境管理

## 安全限制分析

GetQuicker服务器有一个安全规则：**只允许从getquicker.net内部跳转访问用户页面**。

- ❌ 直接访问：返回 404 Not Found
- ✅ 带Referer访问：返回 200 OK

## 关键发现

**最简化的绕过方法**：只需要在HTTP请求头中添加正确的`Referer`字段：

```http
Referer: https://getquicker.net/Share
```

## 环境设置

### 1. 使用uv管理环境

```bash
# 初始化项目
uv init --python 3.11

# 安装依赖
uv add requests beautifulsoup4
```

### 2. 传统pip方式

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 完整自动化工具（推荐）

```bash
# 使用默认用户ID (113342-)
uv run python get_user_info_complete.py

# 指定用户ID
uv run python get_user_info_complete.py 123456-
```

### 2. 分步执行

```bash
# 步骤1: 获取页面
uv run python simple_get_user.py

# 步骤2: 提取信息
uv run python extract_user_info.py
```

### 3. 完整版本（带更多请求头）

```bash
uv run python get_user_actions.py [用户ID]
```

## 提取的信息

工具会自动提取以下用户信息：

1. **推荐码**：`Ta的推荐码：113342-5249`
2. **注册天数**：`2010天`
3. **专业版状态**：`true/false`
4. **用户名**：`Cea`

## 文件说明

### 核心脚本
- `get_user_info_complete.py` - **完整自动化工具**（推荐使用）
- `simple_get_user.py` - 最简化版本，只包含必要的请求头
- `get_user_actions.py` - 完整版本，包含更多请求头和错误处理
- `extract_user_info.py` - 信息提取工具

### 配置文件
- `pyproject.toml` - uv项目配置
- `requirements.txt` - 传统pip依赖（备用）

### 输出文件
- `user_info_113342_.json` - 提取的用户信息（JSON格式）
- `user_113342_.html` - 下载的页面内容

## 技术原理

### 安全限制绕过
服务器通过检查HTTP请求的`Referer`头来判断请求来源：
- 如果Referer是getquicker.net域名下的页面，则允许访问
- 否则返回404错误

这是典型的**Referer检查**安全机制，用于防止直接外部访问。

### 信息提取方法
1. **主要方法**：使用CSS选择器精确定位元素
2. **备用方法**：使用正则表达式提取文本内容
3. **容错处理**：多种方法确保信息提取的可靠性

## 示例输出

```json
{
  "referral_code": "Ta的推荐码：113342-5249",
  "registration_days": "2010天",
  "is_pro_user": true,
  "username": "Cea"
}
```

## 注意事项

- 仅用于学习和研究目的
- 请遵守网站的使用条款
- 不要用于恶意目的
- 建议合理控制请求频率

## 故障排除

### 常见问题

1. **404错误**：检查Referer头是否正确设置
2. **提取失败**：页面结构可能发生变化，检查CSS选择器
3. **网络超时**：检查网络连接，适当增加超时时间

### 调试方法

```bash
# 启用详细输出
uv run python get_user_info_complete.py --debug

# 保存HTML文件进行手动检查
# HTML文件会自动保存，可以查看页面结构
```
