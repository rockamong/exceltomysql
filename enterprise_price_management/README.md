# 企业价格库管理平台

本项目是一个简单的企业价格库管理平台，允许用户上传包含设备价格信息的Excel文件，并将数据存储到MySQL数据库中，同时提供查询价格和配置数据库连接的功能。

## 功能特性

*   通过Excel文件批量上传设备名称、参数和单价。
*   根据设备名称查询价格信息。
*   可配置的数据库连接（默认为本地MySQL）。
*   简单的Web界面进行操作。

## 项目结构

```
enterprise_price_management/
├── backend/                # 后端 Flask 应用
│   ├── app.py              # Flask 主应用，API接口
│   ├── db_connector.py     # 数据库连接和配置管理
│   ├── excel_parser.py     # Excel 文件解析逻辑
│   ├── requirements.txt    # Python 依赖库
│   ├── config.json.default # 默认数据库配置文件模板
│   └── (config.json)       # 实际数据库配置文件（自动生成或修改）
├── database/               # 数据库相关
│   └── schema.sql          # 数据库和表结构定义SQL脚本
├── frontend/               # 前端 HTML, CSS, JS 文件
│   ├── upload.html         # 上传文件页面
│   ├── search.html         # 查询价格页面
│   ├── db_config.html      # 数据库配置页面
│   └── style.css           # 通用样式表
└── README.md               # 本文档
```

## 环境要求

*   Python 3.7+
*   MySQL Server
*   Web浏览器 (如 Chrome, Firefox, Edge)

## 安装与运行

1.  **克隆或下载项目**
    *   将项目文件放置到您的本地计算机。

2.  **数据库设置**
    *   确保您的MySQL服务已启动。
    *   使用MySQL客户端（如 `mysql` 命令行工具, phpMyAdmin, MySQL Workbench等）连接到您的MySQL服务器。
    *   执行 `database/schema.sql` 脚本以创建 `EntPrice` 数据库和 `price` 表。
        ```bash
        mysql -u your_mysql_user -p < database/schema.sql
        ```
        (请替换 `your_mysql_user` 为您的MySQL用户名，之后会提示输入密码)
    *   **注意**: 默认数据库连接配置位于 `backend/config.json.default`。应用首次运行时，如果 `backend/config.json` 不存在，会基于此默认配置自动创建。您可以稍后通过前端的“数据库配置”页面修改这些设置，或直接编辑 `backend/config.json`（若已生成）。默认配置为：
        *   主机: `localhost`
        *   端口: `3306`
        *   用户: `root`
        *   密码: "" (空密码)
        *   数据库名: `EntPrice`
        如果您的MySQL设置不同（特别是用户和密码），请在运行应用前或通过配置页面更新。

3.  **后端服务启动**
    *   打开终端，进入 `backend` 目录:
        ```bash
        cd path/to/enterprise_price_management/backend
        ```
    *   创建Python虚拟环境 (推荐):
        ```bash
        python -m venv venv
        source venv/bin/activate  # Linux/macOS
        # venv\Scriptsctivate   # Windows
        ```
    *   安装依赖库:
        ```bash
        pip install -r requirements.txt
        ```
    *   启动Flask应用:
        ```bash
        python app.py
        ```
    *   服务默认运行在 `http://127.0.0.1:5000`。您应该能看到类似 " * Running on http://127.0.0.1:5000/ " 的输出。

4.  **前端页面访问**
    *   打开您的Web浏览器。
    *   直接通过文件系统打开 `frontend` 目录下的HTML文件，例如:
        *   `file:///path/to/enterprise_price_management/frontend/upload.html`
        *   `file:///path/to/enterprise_price_management/frontend/search.html`
        *   `file:///path/to/enterprise_price_management/frontend/db_config.html`
    *   **注意 (CORS)**: 如果在直接打开HTML文件时遇到连接后端API（如数据加载、上传失败）的问题，这可能是由于浏览器的跨域资源共享 (CORS) 策略。Flask后端默认可能没有配置CORS头。对于开发，一个简单的解决方案是使用支持禁用CORS的浏览器插件，或者修改后端 `app.py` 以允许来自 `file://` 源的请求（仅限开发用途）。更健壮的部署方式是将前端文件也通过一个简单的HTTP服务器提供服务，或者集成到Flask应用中。

## 使用说明

### 1. 数据库配置
*   首次运行或需要更改数据库连接时，访问 `db_config.html` 页面。
*   页面会尝试加载当前配置（密码字段除外）。
*   填写您的MySQL数据库连接信息，然后点击“保存配置”。

### 2. 上传Excel文件
*   访问 `upload.html` 页面。
*   点击“选择文件”按钮，选择一个 `.xls` 或 `.xlsx` 格式的Excel文件。
*   **Excel文件格式要求**:
    *   第一行为表头。
    *   必须包含以下三列，列名需完全匹配:
        *   `设备名称`
        *   `设备参数`
        *   `设备单价`
    *   示例:
        | 设备名称   | 设备参数              | 设备单价 |
        |------------|-----------------------|----------|
        | 服务器A    | 型号X, 16GB RAM, 1TB SSD | 12000.50 |
        | 交换机B    | 24口, 千兆            | 1500.75  |
        | 防火墙C    | 型号Y, 500Mbps吞吐    | 8800.00  |
*   点击“上传文件”按钮。页面会显示上传成功或失败的消息。

### 3. 查询价格
*   访问 `search.html` 页面。
*   在输入框中输入您想查询的设备名称（支持模糊查询）。
*   点击“查询”按钮。下方表格将显示查询结果。

## 注意事项
*   本项目为演示和学习用途，未进行详尽的安全加固和生产环境优化。
*   密码处理：数据库配置中的密码在保存到 `config.json` 时是明文存储的，请确保该文件的安全。前端页面在显示配置时不显示密码，提交新密码时会进行传输。
```
