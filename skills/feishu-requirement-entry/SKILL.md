---
name: feishu-requirement-entry
description: 飞书需求管理技能。自动捕获飞书消息中的需求，智能评估并录入需求池，生成分析报告。触发词：录入、需求写入、需求录入。
metadata:
  version: 1.0
  author: 红温
  created: 2026-04-15
---

# 飞书需求管理技能

自动捕获飞书消息中的需求，智能评估并录入飞书多维表格需求池，生成分析报告。

## 触发机制

### 1. 自动触发

**飞书群聊消息**（关键词匹配）：
- `录入`
- `需求写入`
- `需求录入`

**私聊消息**：所有消息自动处理

### 2. 手动触发

```bash
# 手动录入需求
openclaw requirement add --title "需求标题" --desc "详细描述"

# 查看需求池
openclaw requirement list
```

---

## 引导流程

当用户触发此 skill 时，按以下流程引导用户填写需求信息：

### 第一步：输出引导信息

```text
👋 好的，我来帮你录入新需求！

请提供以下信息（带*为必填，可直接回复或逐项填写）：

* 需求名称：简短描述需求核心
  例：增加数据导出功能

* 一级模块：需求所属大模块
  可选：数据模块、用户模块、内容模块、消息模块、设置模块、性能模块、界面模块、其他

* 二级模块：具体功能点
  例：报表功能、登录流程、文章管理

* 状态：当前进展
  可选：需求阶段、评审中、开发中、测试中、已上线、已搁置

* 重要性：优先级
  可选：高（紧急阻断）、中（正常需求）、低（优化建议）

* 提出时间：日期即可
  例：2026-04-15 或 今天

* 相关人员：产品/技术负责人
  例：产品 - 张三，开发 - 李四

* 标签：需求类型标记
  可选：产品、技术、设计、运营、其他

  有用链接：相关文档/原型/讨论（可选）
  例：https://xxx.feishu.cn/docx/...

  补充描述：其他想说的（可选）

💡 偷懒技巧：直接一句话描述需求，我帮你自动提取字段！
  例："希望能加个导出功能，现在复制太麻烦了"
```

### 第二步：处理用户输入

**方式 1：用户完整填写**
→ 直接提取字段，进入确认环节

**方式 2：用户一句话描述**
→ 自动提取字段（关键词匹配 + 智能分类），展示提取结果让用户确认

**方式 3：用户部分填写**
→ 自动补全缺失字段，标出待确认项

### 第三步：确认反馈

```text
✅ 需求信息已确认，正在录入...

需求 ID: REQ-20260415-008
标题：增加数据导出功能
模块：数据模块 > 报表功能
优先级：高
提出时间：2026-04-15
相关人员：产品 - 张三，开发 - 李四
链接：https://xxx.feishu.cn/docx/ABC123

✅ 已录入飞书需求池！
```

### 第四步：智能评估报告

录入完成后，执行智能评估并输出报告（4 个核心功能）：

```text
📊 智能评估报告

1️⃣ 语义去重
✅ 未发现相似需求
或
⚠️ 发现相似需求：
   - REQ-20260410-003: "希望能导出 Excel 数据"（相似度 92%）
   - REQ-20260405-012: "需要数据导出功能"（相似度 88%）
   建议：合并到现有需求或标记为重复

2️⃣ 自动分类
📋 一级模块：数据模块
   二级模块：报表功能
   依据：关键词匹配 ["数据", "导出", "报表"]

3️⃣ 优先级初判
🎯 优先级评估：高
   依据：包含关键词 ["紧急", "无法使用"]

4️⃣ 责任人推荐
👤 产品负责人：产品 A
   技术负责人：后端组
   依据：数据模块 → 默认分配规则

💡 建议下一步：
- 邀请产品 A、后端组参与评审
- 补充详细需求描述和原型
- 安排需求评审会议
```

**智能评估逻辑**：

- **语义去重**：使用语义相似度比对历史需求，相似度 > 0.85 判定为重复
- **自动分类**：根据 `MODULE_KEYWORDS` 关键词匹配判断模块归属
- **优先级初判**：根据 `PRIORITY_KEYWORDS` 紧急程度词汇标记优先级
- **责任人推荐**：根据 `OWNER_MAPPING` 模块 - 负责人映射推荐

### 用户填写示例

**完整填写：**
```text
需求名称：增加数据导出功能
一级模块：数据模块
二级模块：报表功能
状态：需求阶段
重要性：高
提出时间：2026-04-15
相关人员：产品 - 张三，开发 - 李四
有用链接：https://xxx.feishu.cn/docx/ABC123
补充描述：支持导出 Excel 和 CSV 格式
```

**一句话描述：**
```text
希望能增加数据导出功能，现在每次都要手动复制太麻烦了，急需解决！
```

**部分填写：**
```text
需求名称：暗黑模式
重要性：中
其他你帮我填一下
```

---

## 核心功能

### 1. 需求捕获与字段提取

**自动提取字段**：

| 字段 | 提取方式 | 示例 |
|------|---------|------|
| 需求标题 | 从消息首句或关键词后提取 | "希望能增加导出功能" → "增加导出功能" |
| 详细描述 | 整条消息内容 | 用户原始消息 |
| 提出人 | 飞书消息 sender | "张三" |
| 提出时间 | 消息时间戳 | "2026-04-15 15:30" |
| 来源渠道 | 消息来源类型 | "群聊" / "私聊" / "手动录入" |

**提取逻辑**：

```python
def extract_requirement(message):
    # 关键词匹配
    keywords = ['录入', '需求写入', '需求录入']
    
    # 提取标题（去除关键词）
    title = message.text
    for kw in keywords:
        if kw in title:
            title = title.replace(kw, '').strip()
            break
    
    # 提取提出人和时间（从飞书消息元数据）
    proposer = message.sender_name
    propose_time = message.timestamp
    
    # 判断来源渠道
    channel = "群聊" if message.is_group else "私聊"
    
    return {
        "title": title,
        "description": message.text,
        "proposer": proposer,
        "propose_time": propose_time,
        "channel": channel
    }
```

### 2. 智能评估

**功能点**：

#### 1. 语义去重

与历史需求比对，识别相似需求：

```python
def check_duplicate(new_requirement, history):
    """
    使用语义相似度比对历史需求
    相似度 > 0.85 判定为重复
    """
    from sklearn.metrics.pairwise import cosine_similarity
    
    # 向量化新需求
    new_vec = vectorize(new_requirement['title'])
    
    # 与历史需求比对
    similarities = []
    for req in history:
        hist_vec = vectorize(req['title'])
        sim = cosine_similarity(new_vec, hist_vec)
        similarities.append((req, sim))
    
    # 返回相似需求
    duplicates = [r for r, s in similarities if s > 0.85]
    
    return duplicates
```

**输出示例**：
```
⚠️ 发现相似需求：
- REQ-20260410-003: "希望能导出 Excel 数据"（相似度 92%）
- REQ-20260405-012: "需要数据导出功能"（相似度 88%）

建议：合并到现有需求或标记为重复
```

#### 2. 自动分类

根据关键词判断模块归属：

```python
MODULE_KEYWORDS = {
    "数据模块": ["数据", "导出", "导入", "报表", "统计", "分析"],
    "用户模块": ["用户", "登录", "注册", "权限", "账号"],
    "内容模块": ["内容", "文章", "发布", "编辑", "删除"],
    "消息模块": ["消息", "通知", "推送", "提醒"],
    "设置模块": ["设置", "配置", "选项", "偏好"],
    "性能模块": ["慢", "卡顿", "优化", "速度", "性能"],
    "界面模块": ["界面", "UI", "样式", "布局", "美观"],
}

def classify_requirement(title, description):
    text = (title + " " + description).lower()
    
    scores = {}
    for module, keywords in MODULE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        scores[module] = score
    
    # 返回得分最高的模块
    primary_module = max(scores, key=scores.get)
    secondary_module = sorted(scores.items(), key=lambda x: x[1], reverse=True)[1][0]
    
    return {
        "primary": primary_module,
        "secondary": secondary_module
    }
```

**输出示例**：
```
📋 自动分类结果：
- 一级模块：数据模块
- 二级模块：报表功能
```

#### 3. 优先级初判

根据紧急程度词汇标记优先级：

```python
PRIORITY_KEYWORDS = {
    "高": ["紧急", "立刻", "马上", "严重", "崩溃", "无法使用", "阻断"],
    "中": ["希望", "最好", "建议", "需要", "想要"],
    "低": ["可以", "考虑", "有空", "后续", "优化"]
}

def assess_priority(text):
    scores = {"高": 0, "中": 0, "低": 0}
    
    for priority, keywords in PRIORITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[priority] += 1
    
    # 返回最高优先级
    return max(scores, key=scores.get)
```

**输出示例**：
```
🎯 优先级评估：高
依据：包含关键词 ["紧急", "无法使用"]
```

#### 4. 责任人推荐

根据需求类型推荐产品/技术负责人：

```python
OWNER_MAPPING = {
    "数据模块": {"product": "产品 A", "tech": "后端组"},
    "用户模块": {"product": "产品 B", "tech": "后端组"},
    "内容模块": {"product": "产品 C", "tech": "前端组"},
    "消息模块": {"product": "产品 A", "tech": "后端组"},
    "设置模块": {"product": "产品 B", "tech": "全栈组"},
    "性能模块": {"product": "产品 A", "tech": "架构组"},
    "界面模块": {"product": "产品 C", "tech": "前端组"},
}

def recommend_owner(module):
    return OWNER_MAPPING.get(module, {"product": "产品 A", "tech": "开发组"})
```

**输出示例**：
```
👤 责任人推荐：
- 产品负责人：产品 A
- 技术负责人：后端组
```

### 3. 纳入需求池

**存储位置**：飞书多维表格 - 需求池表

**自动填充字段**：

| 字段名 | 类型 | 自动生成规则 |
|--------|------|-------------|
| 需求 ID | 文本 | `REQ-YYYYMMDD-NNN`（按当日序号） |
| 需求标题 | 文本 | 提取的标题 |
| 详细描述 | 文本 | 原始消息 |
| 提出人 | 文本 | 飞书 sender |
| 提出时间 | 日期 | 消息时间 |
| 提测时间 | 日期 | 留空（后续填写） |
| 原定上线时间 | 日期 | 留空（后续填写） |
| 实际上线时间 | 日期 | 留空（后续填写） |
| 一级模块 | 单选 | 自动分类结果 |
| 二级模块 | 单选 | 自动分类结果 |
| 初步优先级 | 单选 | 低/中/高 |
| 状态 | 单选 | 默认"需求阶段" |
| 产品负责人 | 人员 | 责任人推荐 |
| 技术负责人 | 人员 | 责任人推荐 |
| 来源渠道 | 单选 | 群聊/私聊/手动录入 |
| 相似需求 | 文本 | 去重检测结果 |

**需求 ID 生成逻辑**：

```python
def generate_requirement_id():
    from datetime import datetime
    
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"REQ-{today}-"
    
    # 查询今日已有需求数量
    existing = query_bitable(f"需求 ID 包含 '{prefix}'")
    next_num = len(existing) + 1
    
    return f"{prefix}{next_num:03d}"
```

**录入飞书多维表格**：

```python
def add_to_bitable(requirement):
    from feishu.client import FeishuClient
    
    client = FeishuClient(
        app_id="your_app_id",
        app_secret="your_app_secret"
    )
    
    # 生成需求 ID
    req_id = generate_requirement_id()
    
    # 准备数据
    record = {
        "fields": {
            "需求 ID": req_id,
            "需求标题": requirement['title'],
            "详细描述": requirement['description'],
            "提出人": requirement['proposer'],
            "提出时间": requirement['propose_time'],
            "一级模块": requirement['classification']['primary'],
            "二级模块": requirement['classification']['secondary'],
            "初步优先级": requirement['priority'],
            "状态": "需求阶段",
            "产品负责人": requirement['owner']['product'],
            "技术负责人": requirement['owner']['tech'],
            "来源渠道": requirement['channel'],
            "相似需求": requirement.get('duplicates', '无')
        }
    }
    
    # 调用飞书 API 创建记录
    response = client.bitable.create_record(
        app_token="your_app_token",
        table_id="your_table_id",
        record=record
    )
    
    return response
```

**录入成功反馈**：

```
✅ 需求已录入需求池

📝 需求 ID: REQ-20260415-008
📋 标题：增加导出功能
👤 提出人：张三
📅 提出时间：2026-04-15 15:30
📊 模块：数据模块 > 报表功能
🎯 优先级：高
👥 负责人：产品 A / 后端组
🔗 来源：群聊

📎 查看需求池：https://my.feishu.cn/base/your_app_token
```



## 配置说明

### 飞书应用配置

```json
{
  "appId": "your_app_id",
  "appSecret": "your_app_secret",
  "bitable": {
    "appToken": "your_app_token",
    "tableId": "your_table_id"
  }
}
```

### 触发词配置

可在技能配置中自定义触发词：

```json
{
  "triggerKeywords": ["录入", "需求写入", "需求录入"]
}
```

### 模块分类配置

可根据实际业务调整模块分类和关键词：

```python
MODULE_KEYWORDS = {
    "你的模块名": ["关键词 1", "关键词 2", ...],
    ...
}
```

## 使用示例

### 示例 1：群聊自动捕获

**群聊消息**：
```
@机器人 #需求 希望能增加数据导出功能，现在每次都要手动复制，太麻烦了
```

**机器人响应**：
```
✅ 需求已捕获并录入需求池

📝 需求 ID: REQ-20260415-008
📋 标题：增加数据导出功能
👤 提出人：张三
🎯 优先级：中
📊 模块：数据模块
👥 负责人：产品 A / 后端组

⚠️ 发现相似需求：
- REQ-20260410-003: "希望能导出 Excel 数据"（相似度 92%）

📎 查看：https://my.feishu.cn/base/your_app_token
```

### 示例 2：私聊自动处理

**私聊消息**：
```
建议优化一下登录流程，现在步骤太多了
```

**机器人响应**：
```
✅ 需求已录入需求池

📝 需求 ID: REQ-20260415-009
📋 标题：优化登录流程
👤 提出人：李四
🎯 优先级：中
📊 模块：用户模块
👥 负责人：产品 B / 后端组

📎 查看：https://my.feishu.cn/base/your_app_token
```

### 示例 3：手动录入

**命令**：
```bash
openclaw requirement add \
  --title "增加暗黑模式" \
  --desc "用户反馈晚上使用太刺眼" \
  --proposer "王五" \
  --channel "手动录入"
```

**响应**：
```
✅ 需求已录入需求池

📝 需求 ID: REQ-20260415-010
📋 标题：增加暗黑模式
👤 提出人：王五
🎯 优先级：低
📊 模块：界面模块
👥 负责人：产品 C / 前端组

📎 查看：https://my.feishu.cn/base/your_app_token
```



## 注意事项

1. **权限配置**：确保飞书应用有读取和写入多维表格的权限
2. **去重阈值**：语义相似度阈值默认为 0.85，可根据实际情况调整
3. **责任人映射**：需根据实际团队结构配置 `OWNER_MAPPING`
4. **定期清理**：建议定期归档已关闭需求，保持需求池整洁

## 扩展功能（可选）

- [ ] 需求状态变更通知
- [ ] 需求评审会议自动安排
- [ ] 需求与任务关联
- [ ] 需求满意度调研
- [ ] 需求价值评估模型
