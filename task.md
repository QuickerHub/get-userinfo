# GetQuicker用户信息获取任务

## 任务目标
分析getquicker.net网站的安全限制机制，并提取用户页面的关键信息。

## 任务步骤

### 第一步：安全限制分析
1. 打开 getquicker.net 网页
2. 模拟页面内跳转到目标网址：https://getquicker.net/User/Actions/113342-
3. 分析服务器安全限制机制
4. 提取最简化的HTTP请求头信息来绕过安全限制

### 第二步：信息提取
根据HTTP请求返回的内容，提取以下用户信息：

1. **推荐码**：`body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > a.font14.text-secondary.cursor-pointer.mr-3`

2. **注册天数**：`document.querySelector("body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > span.text-muted.mr-3")`

3. **专业版标识**：`body > div.body-wrapper > div > div.d-flex.align-items-center.justify-content-between.p-3 > h2 > div.d-inline-block.flex-grow-1 > div.font14.mt-2 > span:nth-child(3) > i`
   - 如果存在这个图片元素，表示用户是专业版

## 技术实现
1. 使用浏览器自动化工具获取页面信息
2. 通过Python脚本解析HTML内容，提取指定元素的信息
3. 验证绕过安全限制的有效性

## 预期结果
- 成功绕过getquicker.net的安全限制
- 提取到用户的推荐码、注册天数和专业版状态
- 生成可复用的Python脚本用于批量信息提取
