---
title: 简历
description: AI 应用方向 .NET 全栈工程师
date: 2026-06-01
slug: resume
comments: false
license: false
---

# 陶政辰

**AI 应用方向 .NET 全栈工程师**  
9 年 .NET + React 全栈经验，做过金融系统、游戏后端、企业架构迁移、AI 协作开发与 AI 应用落地。

- 邮箱：zhengchen.tao@outlook.com
- GitHub：[zhengchentao](https://github.com/zhengchentao)
- Blog：[blog.zhengchentao.win](https://blog.zhengchentao.win/)
- Git：[git.zhengchentao.win](https://git.zhengchentao.win/)

## 个人优势

- **AI 应用落地**：在早期 AI 产品项目中担任核心开发，负责架构设计、模块边界、工程规范与 Code Review，将 Claude Code agent 纳入“需求拆解、生成实现、人审验收、CI 校验”的开发流程。
- **AI 协作开发规范**：沉淀数据结构迁移、接口契约同步、自动化检查、代码审查、最小复现等规则，降低生成代码的回归风险；本人负责关键技术选型、边界判断、审查与最终验收。
- **企业级系统经验**：曾参与 Green Dot 核心银行系统、BaaS 平台与统一 API Gateway 开发，支撑百万级日交易、KYC / AML 合规与高可用要求；参与 MuleSoft 至 Azure cloud-native 架构迁移，年度许可及运维成本降低约 40%。
- **架构升级经验**：设计 .NET Framework / IIS 旧架构至 .NET 10 / Linux / Docker / Nginx 的迁移方案与分阶段落地路径，有复杂存量系统渐进式演进经验。

## 技术栈

- **AI 工程**：Claude Code / Cursor agent workflow、AI 协作开发规范、AI 协作下的 CI/CD、本地模型与知识库工作流实验
- **身份与集成**：JWT / Token-based auth、YARP、REST API、第三方开放平台集成、对象存储、实名认证、图像生成服务接入
- **后端**：.NET Framework / Core / 6 / 8 / 10、ASP.NET Core、Entity Framework Core、Npgsql、微服务、QuestPDF、Scriban、ImageSharp
- **前端**：React、Next.js、TypeScript、Vite、pnpm monorepo、Ant Design / Ant Design Mobile / Ant Design Pro、Vue、微信小程序原生
- **数据与基建**：SQL Server、PostgreSQL、SQLite、Redis、RabbitMQ、Azure APIM / Functions / AKS / Cosmos DB / Data Factory、Docker、Nginx、Caddy、Gitea Actions、GitLab CI、Linux

## 工作经历

**盛趣游戏 | .NET 全栈工程师 | 2026.03 - 至今**  
参与多款游戏活动开发，推进跨项目通用模块、.NET 10 架构升级验证与 AI 辅助研发。

**Green Dot Corporation（CLPS 驻场） | .NET 全栈工程师 | 2020.09 - 2025.09**  
嵌入 Green Dot 工程团队，参与核心银行、BaaS、统一 API Gateway 与 Azure 云原生迁移。

**博彦科技 · Microsoft 项目组 | .NET 全栈工程师 | 2019.04 - 2020.09**  
驻场 Microsoft 项目组，参与 MVP/MSP 系统重构、数据迁移、Power BI 数据源与通用脚手架建设。

**上海龙进天下信息技术有限公司 | .NET 全栈工程师 | 2018.03 - 2019.03**  
参与政务系统开发，覆盖人员、排班、考勤、薪资等模块，并承担现场部署与性能优化。

**山东科华电力技术有限公司 | .NET 全栈工程师 | 2017.03 - 2018.03**  
参与电力监控与能效管理系统开发，完成告警、可视化与前后端交付。

## 代表项目

### AI 产品多端业务系统

面向个人肖像数字化授权交易场景，交付 PC、H5、微信小程序、运营后台与 .NET 10 后端，覆盖实名认证、AI 写真、授权凭证、协议、议价、工单与权限控制等核心流程。

- 负责架构设计、工程规范、模块边界与 Code Review；Claude Code agent 用于实现加速，本人负责关键技术选型、数据模型、API 契约、PR 质量与发布验收。
- 接入实名认证、对象存储、图像生成 / 编辑与微信小程序登录等外部能力，完成开发、测试到发布前验收。
- 采用 QuestPDF + Markdig + Scriban 构建凭证模板管理、占位符渲染与后台实时预览能力，减少浏览器渲染依赖，降低部署体积与运行复杂度。
- 通过工程规范固化数据结构迁移、接口契约同步、前后端联动修改等规则；结合自动化检查、代码审查与最小复现流程，提升生成代码的可维护性。

**技术栈**：.NET 10、ASP.NET Core、EF Core、PostgreSQL、Redis、QuestPDF、ImageSharp、Scriban、Markdig、React、Next.js、Vite、Ant Design、微信小程序原生、Docker、Caddy、Gitea Actions

### .NET 10 架构升级验证与通用化模块

设计从 .NET Framework / IIS 老架构向 .NET 10 / Linux / Docker / Nginx 新架构迁移的方案，形成系统升级架构、分阶段落地路径与新系统代码组织方案。

- 设计按业务隔离的新系统部署单元，规划蓝绿部署、健康检查、快速回滚与渐进式路由切换，支持老系统保留、新流量逐步迁移。
- 提出“公共组件解决代码复用 + 公共服务解决状态共享”的两层架构，明确公共组件与公共服务边界。
- 通过适配层隔离历史接口中的固定参数、命名歧义、弱类型返回与错误码差异，为渐进式迁移降低耦合。
- 规划分层架构、按业务功能组织代码、自研定时任务框架、数据库配置中心与后台权限模型，服务后续多活动、多项目复用。

**技术栈**：.NET 10、ASP.NET Core、EF Core、SQL Server、Vue、Docker、Nginx、GitLab CI、Serilog

### 核心银行系统与统一 API Gateway

参与 Green Dot 核心银行、BaaS 平台与统一 API Gateway 建设，为合作伙伴及自有产品提供账户、支付、交易、定期转账、透支保护等能力，支撑百万级日交易与金融监管要求。

- 聚合多个下游核心系统接口，完成数据整合、转换与裁剪，为前端、自有产品及合作伙伴提供统一 API 入口。
- 在既定通用模块架构下交付多合作伙伴复用能力，支持合作伙伴定制化接入，将新伙伴平均上线周期缩短 30% 以上。
- 参与 Token 校验、reCAPTCHA、防刷、防重放、设备风险校验等接口层能力建设，保障高并发访问下的安全性、稳定性与数据一致性。
- 参与 MuleSoft 至 Azure APIM + Functions + AKS 迁移，年度许可及运维成本降低约 40%；开发团队自动化工具，减少人工配置错误率约 50%。

**技术栈**：.NET Core / 6 / 8、React、Azure API Management、Azure Functions、AKS、Redis、RabbitMQ、Cosmos DB、SQL Server

### MVP/MSP 系统重构与数据迁移

参与 Microsoft MVP / MSP 系统重构与数据迁移，覆盖需求确认、系统开发、数据流编排、报表数据源建设与跨团队联调。

- 使用 Azure Data Factory 编排数据流，为 Power BI 报表提供可靠数据源，保障数据完整性与报表准确性，业务分析效率提升约 30%。
- 基于 React / Redux / Fluent UI 配合 .NET API 完成前端界面与数据交互，支持业务团队进行报表分析与数据管理。
- 设计并实现第三方登录、可配置权限、租户隔离与 IdentityServer 集成能力，将新项目基础环境搭建时间缩短 1-2 周。

**技术栈**：.NET Core、React、Redux、Fluent UI、Azure Data Factory、Power BI、SQL Server

### 自建开发与 AI 实验基础设施

基于群晖 NAS、OpenWrt、家庭网络与自托管 CI/CD 环境，长期维护个人开发、写作与 AI 实验环境，主要用于验证基础设施、自动化交付与问题排查方案。

- 自建 Gitea、自托管构建节点、镜像仓库、反向代理、远程访问等基础设施，支撑个人项目的代码托管、自动构建、镜像发布与安全访问。
- 运行 Ollama / KoboldCPP 等本地模型实验环境，并围绕 Obsidian / Gitea 做知识库检索、代码仓库检索和移动端访问等工作流实验。
- 沉淀 20+ 技术排障文档，记录网络、基础设施与自动化部署相关问题的排查过程。

## 教育经历

山东财经大学 | 企业管理专业 | 本科
