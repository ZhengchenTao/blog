---
title: 简历
description: .NET 全栈工程师 / AI 应用与 AI Infra 方向
date: 2026-06-14
slug: resume
comments: false
license: false
---

# 陶政辰

**.NET 全栈工程师 / AI 应用与 AI Infra 方向**  
9 年 .NET + React 全栈经验，长期参与金融系统、企业级系统和多端业务系统交付；近期重点实践 AI agent 协作开发、OAuth / MCP 基础设施与 .NET 10 架构升级。

- 邮箱：zhengchen.tao@outlook.com
- GitHub：[zhengchentao](https://github.com/zhengchentao)
- 个人 Git：[git.zhengchentao.win](https://git.zhengchentao.win/)
- 博客：[blog.zhengchentao.win](https://blog.zhengchentao.win/)

## 个人优势

- **企业级系统经验**：参与 Green Dot 核心银行系统、BaaS 合作伙伴平台与统一 API Gateway 开发，支撑百万级日交易、KYC / AML 合规与高可用要求。
- **AI agent 协作交付**：使用 Claude Code / Codex 加速编码，本人负责需求定义、架构拆解、协议与安全边界判断、关键 Code Review、联调排障与最终验收。
- **AI Infra / MCP 实战**：独立设计并上线 .NET 10 OAuth 授权中心与 MCP 服务链路，支持 DCR、PKCE、PRM、YARP token 翻译层，并接入 Claude.ai Custom Connectors。
- **存量系统演进**：参与 .NET Framework / IIS 旧架构向 .NET 10 / Linux / Docker / Nginx 的迁移方案设计，熟悉复杂存量系统渐进式升级。

## 技术栈

**后端**：.NET Framework / Core / 6 / 8 / 10、ASP.NET Core、EF Core、REST API、QuestPDF、Scriban  
**前端**：React、Next.js、TypeScript、Vite、Ant Design、Vue、微信小程序  
**数据与云**：SQL Server、PostgreSQL、Redis、RabbitMQ、Azure APIM / Functions / AKS、Docker、Nginx  
**AI / Infra**：Claude Code、Codex、MCP、OAuth 2.0、DCR、PKCE、PRM、JWT、YARP、Gitea Actions

## 工作经历

**盛趣游戏 | .NET 全栈工程师 | 2026.03 - 至今**  
参与多款游戏活动开发、跨项目通用模块建设、.NET 10 架构升级验证与 AI 辅助研发。

**Green Dot Corporation（CLPS 驻场） | .NET 全栈工程师 | 2020.09 - 2025.09**  
嵌入 Green Dot 工程团队，参与核心银行、BaaS 合作伙伴平台、统一 API Gateway 与 Azure 云原生迁移。

**博彦科技 · Microsoft 项目组 | .NET 全栈工程师 | 2019.04 - 2020.09**  
在博彦 Microsoft 专项交付环境工作，参与 MVP/MSP 系统重构、数据迁移、Power BI 数据源与通用脚手架建设。

**上海龙进天下信息技术有限公司 | .NET 全栈工程师 | 2018.03 - 2019.03**  
参与政务系统开发，覆盖人员、排班、考勤、薪资等模块，并承担现场部署与性能优化。

**山东科华电力技术有限公司 | .NET 全栈工程师 | 2017.03 - 2018.03**  
参与电力监控与能效管理系统开发，完成告警、可视化与前后端交付。

## 代表项目

### 核心银行系统与 BaaS 合作伙伴平台 | Green Dot（CLPS 驻场） | 2020.09 - 2025.09

参与 Green Dot 核心银行系统与 BaaS 合作伙伴平台建设，为 Amazon Flex、Toast、Walmart、Crypto.com、Sesame Cash 等合作伙伴及自有产品提供账户、支付、交易、定期转账、透支保护等能力。

- 参与账户、支付、交易、定期转账、透支保护等核心金融功能开发，支持自有品牌与多个合作伙伴业务场景复用。
- 在既定通用模块架构下交付多合作伙伴复用能力，支持合作伙伴定制化接入，将新伙伴平均上线周期缩短 30% 以上。
- 参与统一 API Gateway 平台建设与接口安全能力建设，覆盖 Token 校验、reCAPTCHA、防刷、防重放、设备风险校验等场景。
- 参与 MuleSoft 至 Azure APIM + Functions + AKS 迁移，并开发团队自动化工具支持配置自动化和合作伙伴接入流程优化。

**关键词**：.NET Core / 6 / 8、React、Azure APIM、Azure Functions、AKS、Redis、RabbitMQ、Cosmos DB、SQL Server

### 真人肖像商业授权交易平台 | AI 产品项目 | 核心开发 / 架构设计 | 2026.04 - 至今

AI 产品商业化项目，面向个人肖像数字化授权交易场景，交付 PC、H5、微信小程序、运营后台、经纪商家端与 .NET 10 后端。

- 负责架构设计、模块边界、工程规范和 Code Review；使用 Claude Code 辅助完成功能实现，本人负责关键技术选型、数据模型、API 契约、联调排障和发布验收。
- 覆盖卖家入驻、身份核验、AI 写真、授权凭证、协议、议价、工单与权限控制等核心流程。
- 接入实名认证、对象存储、图像生成 / 编辑、微信小程序登录等第三方能力。
- 使用 QuestPDF + Markdig + Scriban 实现凭证模板、占位符渲染和 PDF 生成，减少浏览器渲染依赖。
- 建立数据结构迁移、接口契约同步、前后端联动修改、自动化检查等 AI 协作开发规范，降低生成代码回归风险。

**关键词**：.NET 10、EF Core、PostgreSQL、Redis、QuestPDF、Scriban、React、Next.js、Vite、微信小程序、Gitea Actions

### nas-auth + MCP Service Mesh | 个人独立项目 | 架构设计 / AI 协作实现 | 2026.04 - 2026.06

为个人生产数据源接入 Claude.ai Custom Connectors，自建 .NET 10 OAuth 授权中心与 MCP 服务链路。实现阶段大量使用 Claude Code / Codex 加速编码，本人负责协议选型、系统边界、安全模型、关键代码审查、联调排障与生产验收。

- 实现 DCR、Authorization Code + PKCE、PRM、Resource Indicators、JWT multi-audience、refresh token rotation 等 OAuth / MCP 关键链路。
- 上线 obsidian-mcp 与 gitea-mcp，支持 Claude 读写 Obsidian vault、只读访问 Gitea repo / file / code search / PR / issue / workflow run。
- 使用 YARP IHttpForwarder 做 token 翻译层，让 ezBookkeeping 这类 legacy token 系统无需改造即可接入 Claude.ai。

**关键词**：.NET 10、OAuth 2.0、MCP .NET SDK、JWT、YARP IHttpForwarder、SQLite、Argon2id、Docker Compose

### .NET 10 架构升级验证与通用模块 | 盛趣游戏 | 架构方案设计 / 技术验证 | 2026.03 - 至今

参与盛趣游戏旧系统向 .NET 10 / Linux / Docker / Nginx 演进的方案设计，并在活动开发中沉淀通用能力。

- 设计渐进式迁移路径，支持新旧系统并行、灰度 / 蓝绿、健康检查和快速回滚。
- 梳理公共组件与公共服务边界，将图片上传审核、预约数据接口、道具推送等能力沉淀为跨项目复用模块。
- 规划分层架构、定时任务、配置管理和后台权限模型，服务多活动、多游戏复用。

**关键词**：.NET 10、ASP.NET Core、EF Core、SQL Server、Vue、Docker、Nginx、GitLab CI、Serilog

### MVP / MSP 系统重构与数据迁移 | Microsoft 项目（博彦交付） | 2019.04 - 2020.09

在博彦 Microsoft 专项交付环境工作，参与 MVP / MSP 系统重构、数据迁移和报表数据源建设。项目环境由 Microsoft 在博彦内部搭建，使用 Microsoft 资产、独立安检与 Microsoft 网络接入。

- 使用 Azure Data Factory 编排数据流，为 Power BI 报表提供数据源。
- 基于 React / Redux / Fluent UI 配合 .NET API 完成前端页面和数据交互。
- 设计并实现通用快速启动框架，支持第三方登录、权限配置、租户隔离和 IdentityServer 集成。
- 参与跨团队联调、数据迁移验证、旧系统数据口径梳理和项目交付支持。

**关键词**：.NET Core、React、Redux、Fluent UI、Azure Data Factory、Power BI、SQL Server、IdentityServer

### 自建开发与 AI 实验基础设施 | 个人项目 | 2024 - 至今

围绕个人 NAS、Gitea、Obsidian、CI/CD、MCP 和 AI agent workflow 搭建长期自用研发环境，用于验证新技术、沉淀工程流程和支撑个人项目交付。

- 自建 Gitea、Gitea Actions、Docker Compose、反向代理、OAuth 授权中心和多服务部署环境，支撑个人项目持续迭代。
- 将 Obsidian 作为个人知识库与项目管理入口，通过 MCP 服务接入 Claude.ai，实现文档、代码仓库和任务流的 AI 辅助检索。
- 维护 nas-auth、obsidian-mcp、gitea-mcp、DockPilot 等 .NET / AI Infra 项目，验证 OAuth、MCP、Docker 运维面板和 AI agent 工作流。
- 沉淀 AI 协作开发规范，包括需求拆解、上下文约束、代码审查、自动化检查、最小复现和发布验收。

**关键词**：.NET 10、Docker Compose、Gitea Actions、OAuth、MCP、Obsidian、Claude Code、Codex、Nginx、Caddy

## 公开内容

- [我把家用 NAS 搭成了一套个人基础设施](/posts/homelab-nas-infrastructure/)：复盘个人 NAS / Gitea Actions / MCP / nas-auth / CI/CD 组合成长期基础设施的过程。
- [一份 AI 工程师的知识地图（2026 版）](/posts/ai-engineer-map/)：梳理 LLM、Prompt、RAG、MCP、Agent、AI 编码工具和企业级 AI 应用落地判断。

## 教育经历

山东财经大学 | 企业管理专业 | 本科 | 2014 - 2018
