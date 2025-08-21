# HTML表格解析库推荐

## 1. pandas - 最强大的表格处理库

### 优点：
- **自动识别表格结构**：能自动解析HTML表格并转换为DataFrame
- **强大的数据处理能力**：支持复杂的数据操作、过滤、排序等
- **多种输出格式**：可以轻松导出为CSV、Excel、JSON等格式
- **处理复杂表格**：能处理合并单元格、嵌套表格等复杂结构

### 安装：
```bash
uv add pandas
```

### 基本用法：
```python
import pandas as pd
from io import StringIO

# 解析HTML表格
html_content = "<table>...</table>"
tables = pd.read_html(StringIO(html_content))

# 获取第一个表格
df = tables[0]
print(df.head())

# 导出为CSV
df.to_csv('output.csv', index=False, encoding='utf-8-sig')
```

### 适用场景：
- 需要复杂数据分析的场景
- 需要导出多种格式的场景
- 表格结构相对标准的场景

---

## 2. lxml - 高性能XML/HTML解析库

### 优点：
- **性能优异**：比BeautifulSoup快很多
- **XPath支持**：强大的XPath查询能力
- **内存效率高**：适合处理大型HTML文档
- **精确控制**：可以精确控制解析过程

### 安装：
```bash
uv add lxml
```

### 基本用法：
```python
from lxml import html

# 解析HTML
tree = html.fromstring(html_content)

# 使用XPath查找表格
tables = tree.xpath('//table[@class="table-bordered"]')

# 提取表格数据
for table in tables:
    rows = table.xpath('.//tr')
    for row in rows:
        cells = row.xpath('.//td | .//th')
        cell_texts = [cell.text_content().strip() for cell in cells]
        print(cell_texts)
```

### 适用场景：
- 需要高性能解析的场景
- 需要精确控制解析过程的场景
- 复杂的HTML结构解析

---

## 3. BeautifulSoup - 易用的HTML解析库

### 优点：
- **易于使用**：API简单直观
- **容错性强**：能处理格式不规范的HTML
- **丰富的选择器**：支持CSS选择器和多种查找方法
- **文档完善**：学习资源丰富

### 安装：
```bash
uv add beautifulsoup4
```

### 基本用法：
```python
from bs4 import BeautifulSoup

# 解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 查找表格
table = soup.find('table', class_='table-bordered')

# 提取数据
rows = table.find_all('tr')
for row in rows:
    cells = row.find_all(['td', 'th'])
    for cell in cells:
        print(cell.get_text(strip=True))
```

### 适用场景：
- 快速原型开发
- HTML结构不规范的场景
- 需要容错性的场景

---

## 4. html-table-parser - 专门解析HTML表格

### 优点：
- **专门用途**：专门为解析HTML表格设计
- **简单易用**：API简洁明了
- **自动处理**：自动处理表头、数据行等

### 安装：
```bash
pip install html-table-parser
```

### 基本用法：
```python
from html_table_parser import HTMLTableParser

# 创建解析器
p = HTMLTableParser()

# 解析HTML
p.feed(html_content)

# 获取表格数据
for table in p.tables:
    print(table)
```

---

## 推荐使用策略

### 1. 主要推荐：pandas + lxml
- **pandas**：用于表格数据的主要处理
- **lxml**：作为备用方案和精确控制

### 2. 性能优先：lxml
- 当需要处理大量数据时
- 当需要精确控制解析过程时

### 3. 开发效率优先：pandas
- 快速原型开发
- 需要复杂数据分析时

### 4. 容错性优先：BeautifulSoup
- HTML格式不规范时
- 需要最大兼容性时

## 实际应用示例

在我们的项目中，我们使用了 **pandas + lxml** 的组合：

```python
def extract_actions_using_pandas(html_content: str) -> List[Dict]:
    """使用pandas解析HTML表格"""
    try:
        from io import StringIO
        tables = pd.read_html(StringIO(html_content))
        # 处理表格数据...
    except Exception as e:
        # 如果pandas失败，使用lxml作为备用
        return extract_actions_using_lxml(html_content)

def extract_actions_using_lxml(html_content: str) -> List[Dict]:
    """使用lxml解析HTML表格（备用方法）"""
    tree = html.fromstring(html_content)
    tables = tree.xpath('//table[@class="table-bordered"]')
    # 处理表格数据...
```

这种组合提供了：
- **高成功率**：pandas处理标准表格，lxml处理特殊情况
- **高性能**：lxml提供快速解析
- **灵活性**：可以根据需要选择最适合的方法
