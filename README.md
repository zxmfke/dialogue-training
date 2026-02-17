# 🎯 话术演练场

基于 OpenClaw Agent 架构的完整 Web 应用 - 医院咨询师话术陪练系统。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务
```bash
python scripts/start_api.py
```

### 3. 访问应用
- **咨询师端**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin
- **API 文档**: http://localhost:8000/docs

## 📁 项目结构

```
话术演练场/
├── PRD.md                    # 产品需求文档
├── README.md                 # 项目说明
├── requirements.txt          # 依赖包
├── config/
│   └── agent.yaml           # Agent 配置文件
├── src/
│   ├── agent/               # OpenClaw Agent 核心
│   │   ├── coach_agent.py   # 主 Agent 逻辑
│   │   └── tools/           # 工具模块
│   │       ├── knowledge.py    # 知识库管理
│   │       ├── evaluation.py   # 对话评估
│   │       ├── scenario.py     # 场景生成
│   │       └── notification.py # 消息通知
│   ├── api/
│   │   └── main.py          # FastAPI 后端
│   ├── webapp/              # 前端界面
│   │   ├── index.html       # 咨询师端
│   │   └── admin.html       # 管理后台
│   └── knowledge/           # 知识库目录
└── scripts/
    └── start_api.py         # 启动脚本
```

## 🎨 功能特性

### 咨询师端 (http://localhost:8000)
- ✅ **场景化训练** - 医美/口腔/体检科项目话术练习
- ✅ **AI 患者角色** - 模拟不同性格患者（犹豫型/价格敏感型/冲动型）
- ✅ **实时对话** - 多轮交互，还原真实咨询场景
- ✅ **即时反馈** - 专业度/共情力/转化力/合规性四维评估
- ✅ **训练报告** - 个人成长曲线和能力分析
- ✅ **碎片化学习** - 3-5分钟完成一次训练

### 管理后台 (http://localhost:8000/admin)
- 📊 **数据概览** - 团队练习趋势、能力分布雷达图
- 👥 **成员管理** - 咨询师列表、成绩排名、需关注人员
- 🎭 **场景管理** - 训练场景配置、难度设置
- 📚 **知识库** - 话术文档上传、敏感词配置
- 📈 **培训报告** - 周报/月报导出

## 🔧 技术架构

| 层级 | 技术 | 说明 |
|-----|------|-----|
| **前端** | 原生 HTML/JS/CSS | 移动端优先，响应式设计 |
| **后端** | FastAPI | Python 异步 Web 框架 |
| **Agent** | OpenClaw Agent | AI 陪练核心 |
| **LLM** | GPT-4/Claude | 对话生成和评估 |
| **存储** | SQLite/JSON | 轻量级数据存储 |

## 🛠️ 开发计划

- [x] 核心 Agent 逻辑
- [x] API 接口开发
- [x] 咨询师端 Web 界面
- [x] 管理后台界面
- [ ] 语音输入/输出
- [ ] 微信小程序适配
- [ ] 企业微信机器人
- [ ] 私有化部署方案

## 📱 界面预览

### 咨询师端
- 首页：统计数据、场景选择、快速开始
- 对话页：AI 患者角色扮演、实时对话
- 报告页：四维能力分析、成长曲线

### 管理后台
- 仪表盘：团队数据概览、趋势图表
- 成员页：咨询师管理、成绩排名
- 场景页：训练场景配置
- 知识库：话术文档管理

## 🔐 合规特性

- ✅ 敏感词自动检测（医疗广告法）
- ✅ 违规话术实时提醒
- ✅ 数据本地存储（支持私有化）
- ✅ 患者隐私保护

## 📝 配置说明

编辑 `config/agent.yaml`：

```yaml
# LLM 配置
llm:
  provider: "openai"
  model: "gpt-4"

# 评估维度
evaluation:
  dimensions:
    - name: "专业度"
      weight: 25
    - name: "共情力"
      weight: 25
    - name: "转化力"
      weight: 25
    - name: "合规性"
      weight: 25

# 敏感词库
sensitive_words:
  - "最好"
  - "第一"
  - "根治"
  - "保证治愈"
```

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

MIT License
