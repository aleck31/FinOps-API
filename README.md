# AWS FinOps API

基于FastAPI构建的AWS财务运营仪表板，为监控平台提供成本、预算和资源使用情况的数据接口和API服务演示界面。

## API Endpoints - 五大核心FinOps指标

### 💰 成本管理
- `GET /api/v1/costs/daily` - 每日成本数据
- `GET /api/v1/costs/by-service` - 按服务分组成本
- `GET /api/v1/costs/by-tags` - 按标签分组成本
- `GET /api/v1/costs/forecast` - 成本预测

### 📊 预算监控
- `GET /api/v1/budgets` - 预算信息
- `GET /api/v1/budgets/{budget_name}` - 预算详情

### 📋 资源清单
- `GET /api/v1/inventory/ec2` - EC2实例清单
- `GET /api/v1/inventory/rds` - RDS实例清单
- `GET /api/v1/inventory/s3` - S3存储桶清单
- `GET /api/v1/inventory/lambda` - Lambda函数清单

### 📈 资源监控
- `GET /api/v1/metrics/ec2` - EC2指标
- `GET /api/v1/metrics/rds` - RDS指标
- `GET /api/v1/metrics/lambda` - Lambda指标

### 🎯 优化建议
- `GET /api/v1/optimization/trusted-advisor` - Trusted Advisor建议
- `GET /api/v1/optimization/compute-optimizer` - Compute Optimizer建议
- `GET /api/v1/optimization/reserved-instances` - 预留实例建议
- `GET /api/v1/optimization/savings-plans` - 节省计划建议

### 📋 综合报告
- `GET /api/v1/reports/cost-summary` - 成本汇总报告

## 项目结构

```
finops/
├── finops_api/     # API后端服务
│   ├── main.py                   # 主应用入口 (支持直接运行)
│   ├── config.py                 # 配置文件
│   ├── models/                   # 数据模型
│   │   └── response.py           # API响应模型
│   ├── dependencies/             # 依赖注入
│   │   └── clients/              # AWS客户端组件
│   └── routers/                  # API路由 (按FinOps类别组织)
│       ├── costs.py              # 💰 成本管理API
│       ├── budgets.py            # 📊 预算监控API
│       ├── metrics.py            # 📈 资源监控API
│       ├── inventory.py          # 📋 资源清单API
│       ├── optimization.py       # 🎯 优化建议API
│       └── reports.py            # 📋 综合报告API
├── webui/       # Web演示页面
├── tests/          # 测试脚本
├── logs/           # 日志文件
└── run.sh          # 启动脚本
```

## 快速开始

使用项目运行脚本 `run.sh` 进行服务管理：

```bash
# 统一管理
./run.sh start          # 启动所有服务
./run.sh stop           # 停止所有服务
./run.sh restart        # 重启所有服务
./run.sh status         # 检查服务状态

# API服务管理
./run.sh api            # 启动API服务器
./run.sh stop-api           # 停止API服务器
./run.sh restart-api        # 重启API服务器

# Web演示管理
./run.sh web            # 启动Web演示服务器
./run.sh stop-web       # 停止Web演示服务器
./run.sh restart-web    # 重启Web演示服务器

# 其他功能
./run.sh demo           # 运行完整演示
./run.sh test           # 运行测试套件
./run.sh help           # 查看帮助
```

## 访问地址

- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Web演示**: http://localhost:3000

## 配置

项目默认使用AWS profile `default`，可通过环境变量指定其他profile：

```bash
# 使用默认profile
./run.sh start

# 使用指定profile
export AWS_PROFILE=your-profile
./run.sh start

# 或者配置AWS凭证
aws configure
```

## 监控平台集成

```python
import requests

# 获取成本数据
response = requests.get("http://localhost:8000/api/v1/costs/daily?days=7")
data = response.json()
```
