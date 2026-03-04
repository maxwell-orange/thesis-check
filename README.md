# 本科毕业论文检查系统

山东财经大学本科毕业论文格式与内容质量自动检查系统。

## 功能特性

- **格式检查**：自动检查论文格式规范
  - 页面设置（页边距、纸张大小）
  - 标题格式（章、节、小节）
  - 正文格式（字体、字号、行距、缩进）
  - 摘要格式
  - 参考文献格式
  - 图表格式

- **AI 内容检查**：基于大模型的内容质量检查
  - 语言表达（语法、用词、语句通顺）
  - 学术规范（术语、论述严谨性）
  - 内容质量（摘要、结论一致性）
  - 引用规范

- **支持的 AI 服务商**：
  - 智谱AI (glm-4, glm-4-flash 等)
  - Kimi (moonshot-v1 系列)
  - DeepSeek (deepseek-chat, deepseek-reasoner)
  - 豆包 (doubao-pro, doubao-lite)

## 快速开始

### 1. 环境要求

- Python 3.8+
- Node.js 16+

### 2. 安装后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装前端

```bash
cd frontend
npm install
```

### 4. 启动服务

**启动后端**（终端 1）：
```bash
cd backend
python app.py
```

**启动前端**（终端 2）：
```bash
cd frontend
npm run dev
```

### 5. 访问系统

打开浏览器访问：http://localhost:5173

## 使用指南

### 第一步：上传论文

1. 点击或拖拽上传 Word 文档（.docx 格式）
2. 文件大小限制：10MB

### 第二步：配置 API

1. 选择 AI 服务商
2. 输入 API Key
3. 选择模型（推荐使用免费模型 glm-4-flash）
4. 选择要启用的检查项

**获取 API Key**：
- 智谱AI：https://www.bigmodel.cn/ （注册即送免费额度）
- Kimi：https://platform.moonshot.cn/
- DeepSeek：https://platform.deepseek.com/
- 豆包：https://www.volcengine.com/product/doubao

### 第三步：开始检查

点击"开始检查"按钮，系统将自动进行：
1. 文档解析
2. 格式检查
3. AI 内容检查
4. 生成报告

### 第四步：查看报告

检查完成后，您可以：
- 查看问题统计概览
- 查看详细的格式问题列表
- 查看 AI 检查发现的建议和问题
- 根据建议进行修改

## 项目结构

```
thesis-check/
├── backend/                    # 后端代码
│   ├── app.py                 # Flask 应用入口
│   ├── config.py              # 配置文件
│   ├── requirements.txt       # Python 依赖
│   ├── services/              # 业务服务
│   │   ├── doc_parser.py      # Word 文档解析
│   │   ├── format_checker.py  # 格式检查
│   │   └── ai_checker.py      # AI 内容检查
│   ├── models/                # 数据模型
│   │   ├── check_rules.py     # 检查规则定义
│   │   └── report.py          # 报告数据结构
│   └── utils/                 # 工具函数
│       ├── llm_client.py      # 大模型统一客户端
│       └── file_handler.py    # 文件处理
│
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── App.jsx            # 主应用
│   │   ├── main.jsx           # 入口
│   │   ├── components/        # 组件
│   │   │   ├── UploadForm.jsx # 文件上传
│   │   │   ├── ApiConfig.jsx  # API 配置
│   │   │   ├── CheckProgress.jsx # 检查进度
│   │   │   └── ReportViewer.jsx  # 报告展示
│   │   ├── services/          # API 服务
│   │   │   └── api.js
│   │   └── styles/            # 样式
│   │       └── App.css
│   ├── package.json
│   └── vite.config.js
│
└── docs/                       # 文档
    ├── api.md                 # API 文档
    └── format_rules.md        # 格式规则说明
```

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 前端 | React + Ant Design | React 18, Antd 5.x |
| 后端 | Python + Flask | Flask 3.x |
| 文档解析 | python-docx | 0.8.11+ |
| 大模型 API | OpenAI 兼容 SDK | - |

## 检查规则

系统根据山东财经大学本科毕业论文格式要求进行以下检查：

### 页面设置
- A4 纸张，纵向
- 上 2.5cm，下 2cm，左 2.5cm，右 2cm

### 标题格式
- **章标题**：黑体三号居中，段前段后 0.5 行
- **节标题**：黑体四号左对齐，段前段后 0.5 行
- **小节标题**：黑体小四，首行缩进 2 字符，段前段后 0.5 行

### 正文格式
- 中文字体：宋体
- 英文字体：Times New Roman
- 字号：小四 (12pt)
- 行距：1.5 倍
- 首行缩进：2 字符

### 摘要
- 中文 300 字左右
- 需有对应的英文摘要

### 参考文献
- 数量 ≥ 10 篇
- 近三年文献 ≥ 30%
- 格式符合 GB/T 7714 规范

## 已知限制

1. **文档格式**：仅支持 .docx 格式（Word 2007+），.doc 格式需先转换
2. **页眉页脚**：python-docx 无法读取页眉页脚内容
3. **页码检查**：可能不够准确
4. **复杂表格**：格式识别能力有限

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎反馈。
