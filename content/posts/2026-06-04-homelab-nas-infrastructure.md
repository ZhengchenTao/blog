---
title: 我把家用 NAS 搭成了一套个人基础设施
slug: homelab-nas-infrastructure
date: 2026-06-04
tags: [NAS, Homelab, OpenWrt, Docker, Gitea, CI/CD, Cloudflare, MCP]
categories: [工程实践]
description: "一次家用 NAS 的 homelab 架构复盘：从 OpenWrt、Cloudflare、Nginx Proxy Manager 到 Gitea Actions、MCP 和 nas-auth，记录它如何从存储设备长成个人基础设施。"
draft: false
---

# 我把家用 NAS 搭成了一套个人基础设施

一开始买 NAS，我想的其实很简单：存照片、存文件、做个家庭云盘。

但真正开始折腾以后，事情很快就不只是“存储”了。

我开始把域名接进来，把内外网访问统一起来，把 Git 仓库和 CI/CD 跑起来，把博客部署进去，把照片、媒体、记账、开发数据库、自建 AI 工具都放上去。到最后，这台 NAS 已经不太像一块硬盘，更像是一套小型个人基础设施。

这篇不是手把手教程，也不是“我的服务清单大公开”。我更想记录的是：一台家用 NAS，怎样一步步从“存储设备”长成一个能持续运行、持续部署、持续积累的个人平台。

所以文中会刻意省略真实域名、IP、端口和密钥细节，只保留架构关系和踩坑逻辑。

## 一、目标不是堆服务，而是建立一个可控的系统

很多 NAS 折腾帖最后都会变成服务列表：

- 照片用什么
- 下载用什么
- 影视用什么
- 反代用什么
- 内网穿透用什么
- 备份用什么

这些当然重要，但如果只按服务看，很容易陷入“装了很多容器”的幻觉。

真正的分水岭不是装了多少服务，而是这些服务之间有没有形成系统。

我现在这套 NAS 的目标大概有四个：

1. 数据长期留在自己手里
2. 内网和外网尽量用统一入口访问
3. 代码、部署、博客、文档能形成闭环
4. AI 工具可以直接读取我的最新资料，而不是每次靠手动复制粘贴

所以这台 NAS 承担的角色已经不只是文件服务器，而是：

- 存储中心
- 家庭网络入口
- 反向代理网关
- Git 和 CI/CD 平台
- 个人博客发布平台
- AI 上下文服务端
- 一部分开发环境

听起来有点夸张，但拆开看，其实每一层都很朴素。

## 二、整体拓扑

现在的物理结构大概是这样：

```text
光猫（桥接）
  ↓
OpenWrt 主路由（PPPoE / DHCP / DNS / 透明代理）
  ↓
2.5G 交换机
  ├── NAS（双 2.5G 网口链路聚合）
  └── 台式机 / 其他有线设备
```

外网访问链路：

```text
用户访问 https://service.example.com
  ↓
Cloudflare DNS
  ↓
Cloudflare Origin Rule 改写到非标准 HTTPS 端口
  ↓
家庭公网入口
  ↓
OpenWrt 端口转发
  ↓
NAS 上的 Nginx Proxy Manager
  ↓
具体 Docker 服务
```

内网访问链路：

```text
内网设备访问 https://service.example.com
  ↓
OpenWrt dnsmasq 把 *.example.com 解析到 NAS 内网地址
  ↓
NAS 本机端口重定向
  ↓
Nginx Proxy Manager
  ↓
具体 Docker 服务
```

也就是说，外网和内网看到的是同一套域名，只是路径不同。

外网经过 Cloudflare、路由器端口转发和 NPM；内网通过 dnsmasq 直接打到 NAS，再由 NPM 分发。

这个设计的好处是：使用体验统一。

无论我在家里 WiFi、公司网络，还是手机 5G，只要访问同一个子域名，就能进到同一个服务。应用配置也不用区分“内网地址”和“公网地址”。

代价是网络层复杂度会上去，尤其是证书、端口、IPv6、透明代理和 Docker 容器出站流量交织在一起以后，坑会非常具体。

后面会讲几个。

## 三、服务分层

如果按用途分，这套 NAS 可以分成几层。

### 1. 存储层

最基础的一层还是 NAS 本职工作：

- SMB：局域网文件共享
- WebDAV：Obsidian 多端同步
- 照片：Synology Photos + Immich 双服务分工
- 媒体：Jellyfin 管影视库和电视端播放
- 下载：qBittorrent 容器负责 BT 下载

这一层的原则是：能用 DSM 原生能力解决的，不一定要上容器。

比如局域网文件共享，DSM 的 SMB 就够了；个人云盘也可以优先考虑 DSM File Station / Drive Server。不是所有东西都值得 Nextcloud 化。

照片是个例外。我最后没有把它压成单一服务，而是保留 Synology Photos，同时运行 Immich。一个更像 DSM 生态里的稳定相册入口，另一个更适合现代照片管理、移动端备份和后续 AI 能力。媒体则交给 Jellyfin，BT 下载单独用 qBittorrent 容器，不把照片、影视、下载混在同一个服务里。

这也是后来砍掉一堆方案后的结论：Paperless、Seafile、KodBox、Nextcloud 看起来都很强，但如果真实场景只是“我自己存文件、偶尔手机访问”，它们带来的维护成本未必划算。

### 2. 网络入口层

这一层包括：

- OpenWrt 主路由
- dnsmasq 内网域名重写
- Passwall 透明代理
- Cloudflare DNS
- Nginx Proxy Manager
- Let's Encrypt DNS Challenge

这层是整套系统的地基。

我最后选择 Nginx Proxy Manager，不是因为它最优雅，而是因为它对 homelab 足够省心：Web UI 配反代、自动申请证书、每个子域名单独管理。对单人维护来说，NPM 的性价比非常高。

Caddy 和裸 Nginx 更适合配置文件进 Git、多人协作、IaC 管理的场景。但家用 NAS 的第一优先级通常不是“最工程化”，而是“稳定跑起来，半年后自己还能看懂”。

这里还有一个群晖特有的前提：DSM 自带一套系统级 nginx，会占住 80/443。它服务的是 DSM 管理界面、套件入口和群晖自己的反向代理能力。

我没有把这套自带 nginx 当作总入口，而是另起了一个 Nginx Proxy Manager 来统一管理所有自建服务。这样做的好处是清晰：自建服务都进 NPM，证书、反代、WebSocket、上传限制都在同一个地方配置。

但代价也很明确：NPM 没法直接绑定宿主机的 80/443，只能监听别的端口。后面很多证书和访问问题，其实都来自这个选择：

```text
DSM 自带 nginx 占住 80/443
  ↓
自建 NPM 只能监听其他端口
  ↓
外网要靠 Cloudflare / 路由器把流量转到 NPM
  ↓
内网要靠 dnsmasq + NAS 本机端口重定向进 NPM
  ↓
证书、IPv6、Docker 容器出站流量开始互相影响
```

所以这不是单纯“证书配置麻烦”，而是“绕开群晖自带入口，自己接管入口”之后产生的一整串工程后果。

### 3. 开发基础设施层

这一层是我后来最满意的部分：

- Gitea：自托管 Git 仓库
- Gitea Actions Runner：自建 CI/CD
- Container Registry：自家镜像发布通道
- PostgreSQL / Redis：开发调试环境
- Hugo blog：push 后自动 build 和部署

博客就是第一个完整落地的 CI/CD 场景：

```text
本地写文章
  ↓
push 到 Gitea
  ↓
Gitea Actions 触发 Hugo build
  ↓
runner 把 public 目录同步到 NAS 上的 nginx 静态目录
  ↓
blog.example.com 上线
```

后面自建服务也复用同一套模式：

```text
push
  ↓
build Docker image
  ↓
push 到 Gitea Container Registry
  ↓
NAS 上 docker compose pull
  ↓
docker compose up -d
```

这一层让 NAS 从“运行服务的机器”变成了“可以持续交付的机器”。

差别很大。

手动 SSH 上去改 compose 是运维；push 代码自动构建、自动部署，才开始像一套基础设施。

### 4. AI 上下文层

最近又加了一层和 AI 相关的东西：

- nas-auth：轻量 OAuth 授权中心
- obsidian-mcp：让 AI 读写 Obsidian vault
- gitea-mcp：让 AI 读取 Gitea 仓库、commit、issue、workflow
- ezBookkeeping MCP proxy：把开源记账工具自带的 MCP 接到统一授权入口后面

这层的目标不是“把 AI 放在 NAS 上跑”，而是让 AI 能安全访问我的上下文。

过去和 AI 协作时，经常需要手动贴文档、贴代码、贴仓库结构。现在思路变了：让 AI 通过标准协议访问我的资料源。

Obsidian 负责长期记忆，Gitea 负责代码事实，nas-auth 负责统一授权。这样 AI 工具不再是孤立聊天窗口，而是可以接入个人基础设施的一部分。

ezBookkeeping 这里还有一个很典型的工程缝合点：它本身是一个开源记账工具，并且已经自带 MCP 端点。但它的 MCP token 体系不符合 Claude custom connector 需要的 OAuth 流程，不能直接拿来完成 DCR、PKCE、resource、aud 这一整套握手。

所以我没有去大改 ezBookkeeping 的认证逻辑，而是在 nas-auth 里做了一层 proxy。Claude 先按标准 OAuth 流程拿 nas-auth 签发的 JWT，再请求 nas-auth 的 proxy 端点；nas-auth 验完 JWT 以后，把请求转发给 ezBookkeeping 自带 MCP，并在内部替换成 ezBookkeeping 能识别的 MCP token。

这样外面对 AI 客户端是标准 OAuth，里面对 ezBookkeeping 还是它原来的认证方式。代价是多了一层翻译，但好处是不用把第三方 fork 改得太深。

这也是我后来越来越觉得 NAS 有意思的地方：它不只是保存数据，也开始保存和暴露“我自己的上下文”。

## 四、几个关键取舍

### 1. 内外网为什么用同一套域名

最简单的方案是：

- 内网访问内网 IP
- 外网访问公网域名

但这种方案会让每个客户端都出现两套配置。手机 App、桌面客户端、浏览器书签、API callback，都要区分场景。

所以我更倾向于统一入口：

- 外网：域名走 Cloudflare 和路由器转发
- 内网：同一个域名被 dnsmasq 重写到 NAS 内网地址

这样上层应用不需要知道自己在哪里。

这也是很多复杂度的来源，但它换来的是长期使用上的简单。

这里有一个边界：Tailscale 仍然保留，用来做基础的远程 TCP/SSH 访问；但我没有继续做 Tailscale Subnet Router + Split DNS，把 tailnet 设备也伪装成同一套域名入口。那条路和路由器上的透明代理、DNS 分流会缠在一起，收益没有大到值得长期维护。

### 2. 为什么不用 Cloudflare Tunnel

Cloudflare Tunnel 很适合没有公网 IP、不能端口转发、只想快速把服务暴露出去的人。

但我的场景里已经有可控的公网入口，而且希望保留更多网络控制权。Tunnel 会引入一条额外链路，排障时也多一个黑盒。

所以最终选择了更传统的方案：

```text
Cloudflare DNS → 家庭公网入口 → OpenWrt 端口转发 → NPM
```

这条路更“土”，但可解释性更强。

我能明确知道每一跳在哪里，出问题也能按层排。

### 3. 为什么 Gitea Actions runner 改成 host 模式

Gitea Actions 一开始按默认思路跑：runner 再拉一个 job 容器，每个 step 在第二层容器里执行。

这在云服务器上很正常，但在 NAS 上很快遇到问题：runner 容器挂载的目录，job 容器看不到。

比如博客部署时，我希望 workflow 直接把 Hugo 产物同步到 NAS 上的静态目录。挂载点在 runner 容器里有，但第二层 job 容器并不会自动继承。

最后改成 host 模式：

```text
act_runner 容器
  └── 直接在 runner 容器内执行 step
        ├── hugo build
        ├── rsync
        └── docker compose pull / up
```

这不是最隔离的方案，但对单人可信代码场景足够实用。

工程上经常是这样：最标准的方案不一定最适合当前约束。NAS 不是 Kubernetes 集群，没必要把每件事都做成企业平台。

### 4. 为什么很多服务最后被砍掉

NAS 折腾到后面，一个重要能力不是“会装”，而是“会砍”。

我先后放弃过一些方案：

- AdGuard Home：最后用 OpenWrt dnsmasq 一条规则替代
- Cloudflare Tunnel：公网入口已有，保留传统链路
- Tailscale Split DNS：Tailscale 保留作基础远程访问，但放弃 Subnet Router + Split DNS + 统一域名入口
- Seafile / Nextcloud / KodBox：真实文件访问需求没那么复杂
- Paperless：没有稳定的文档归档场景
- Jellyfin 管照片：照片交给 Synology Photos + Immich，Jellyfin 只管影视

这些放弃不是失败，而是系统逐渐收敛。

一个可维护的 homelab，不应该靠“服务越多越强”来证明价值。真正长期跑得住的系统，往往是不断删掉不必要的部分以后留下来的。

## 五、真实运行后才会遇到的问题

这套 NAS 真正让我长经验的，不是服务装起来，而是几个非常具体的坑。

### 1. 绕开群晖自带 nginx 后，端口重定向一定要限制目标地址

群晖 DSM 自己占着 80/443，我又没有使用 DSM 自带的反向代理作为总入口，而是自己起了 NPM。结果就是：NPM 只能监听另一个 HTTPS 端口。

为了让内网访问普通 HTTPS 地址也能进 NPM，我在 NAS 本机做了 443 到 NPM 端口的重定向。

最开始规则写得太粗，只按目标端口匹配。

结果是什么？

Docker 容器访问外部 HTTPS 时，流量经过 NAS 的 PREROUTING，也被这条规则劫持到了本机 NPM。容器以为自己在访问 GitHub、Docker Hub 或其他外部服务，实际 TLS 握手打到了自家反代上。

表现出来的错误非常迷惑：TLS alert、SNI 不匹配、证书异常。

真正的修法是：重定向规则必须限制“目标地址是 NAS 自己”。

这个坑的价值在于，它让我重新理解了 host 进程、容器流量、PREROUTING、OUTPUT 之间的区别。

不是所有“本机上的流量”都走同一条路径。

### 2. 改 dnsmasq 后，Passwall 也要重启

内网域名解析由 OpenWrt dnsmasq 管，但透明代理层还有 Passwall。

我一开始以为改完 dnsmasq、重启 dnsmasq 就结束了。结果客户端看到的解析结果还是旧的。

后来才发现，Passwall 夹在客户端和 dnsmasq 之间，自己还有一层 DNS 分流和缓存。dnsmasq 重启不会通知它。

所以标准动作变成：

```text
改 dnsmasq
  ↓
重启 dnsmasq
  ↓
重启 Passwall
  ↓
再验证客户端解析结果
```

这个坑的本质不是某个软件难用，而是系统里多了一层“你以为不存在的状态”。

### 3. Gitea Actions runner 必须锁 Docker API 版本

Gitea Actions runner 需要调用 NAS 上的 Docker daemon。

问题是：runner 镜像里的 docker CLI 很新，而 DSM 自带 Docker engine 的 API 上限比较旧。CLI 默认协商失败后，所有 docker 命令都会报 client version too new。

最后解决方式很简单：显式指定 Docker API 版本，让 CLI 用 NAS daemon 支持的协议说话。

这个问题很典型：不是代码错，不是网络错，也不是权限错，而是“客户端太新，服务端太旧”。

NAS 这种环境经常会遇到这类版本错位。系统看起来像 Linux，但它不是一台你能完全控制发行版节奏的普通服务器。

### 4. DSM 上排障不能只靠 docker logs

有一次 Gitea Actions 状态错乱，Docker 命令还会 hang。普通排障路径基本失效：

- docker logs 卡住
- docker exec 卡住
- docker inspect 卡住
- docker stop 也卡住

后来才摸出 DSM 上几个特殊入口：

- 共享文件夹快照：可以对照几天前数据库长什么样
- Docker 的 log.db：DSM 用 SQLite 存容器日志，docker logs 挂了还能直接读
- cgroup.procs：判断容器是真有进程，还是 Docker daemon 以为它还活着

这类经验很难从教程里直接学到，必须在真实故障里踩出来。

NAS 不是纯 Linux 服务器，DSM 有自己的封装层。排障时如果只按通用 Docker 经验走，很容易卡住。

## 六、现在这套系统长什么样

现在运行在这台 NAS 上的东西，大致分成这些类：

| 层级 | 代表服务 |
|---|---|
| 存储与同步 | SMB、WebDAV、Synology Photos、Immich、Jellyfin、qBittorrent |
| 网络入口 | OpenWrt、dnsmasq、Passwall、Cloudflare、NPM |
| 开发基础设施 | Gitea、Actions Runner、Container Registry、PostgreSQL、Redis |
| 内容发布 | Hugo blog、nginx 静态站点 |
| AI 上下文 | nas-auth、obsidian-mcp、gitea-mcp、ezBookkeeping MCP proxy |

这些服务不是一次设计出来的，而是在两个月左右的连续折腾里逐渐长出来的。

一开始是“我想把服务从云服务器迁回家里”。

后来变成“我想让家里这台机器承担更多长期资产”。

再后来，它开始承载我的博客、代码仓库、CI/CD、AI 上下文、个人数据和一部分开发环境。

它不再只是 NAS。

它更像一个私人平台。

## 七、什么人适合这样折腾 NAS

我不觉得每个人都应该这么折腾。

如果只是想备份照片、看电影、存文件，NAS 原生功能加少量成熟套件已经够用。上来就搞公网、反代、CI/CD、自建 Git、MCP，只会把自己拖进维护泥潭。

但如果你有这些需求，这条路就很值得：

- 想掌控自己的数据
- 想有一个长期可用的个人服务平台
- 想把 Git、博客、文档、AI 工具串起来
- 想理解网络、证书、DNS、反代、容器这些东西到底怎么协作
- 能接受偶尔周末被一个 TLS 错误折磨几个小时

它不省时间。

但它会让很多抽象概念变成真实经验。

你会真的理解：

- DNS 不只是解析域名
- 反向代理不只是转发请求
- HTTPS 证书不只是浏览器小锁
- Docker 网络不只是端口映射
- CI/CD 不只是 GitHub 上一排绿色勾
- AI 接工具也不只是一个“插件”按钮

这些东西只有在你自己维护一套系统时，才会从概念变成手感。

## 八、可以继续拆开的工程复盘

这篇只是总览。里面很多坑都值得单独展开。

后面比较适合拆成几篇：

1. 内外网同域名访问：dnsmasq、NPM、证书和端口重定向
2. Gitea Actions 跑在群晖 NAS 上：从 docker-in-docker 到 host 模式
3. Claude custom connector 接入自建 MCP：DCR、PKCE、PRM、resource 和 aud
4. 为什么我给 homelab 写了一个轻量 OAuth 授权中心
5. NAS 上哪些服务最后被砍掉了，以及为什么

如果说这套 NAS 最后给我的一个结论，那应该是：

> homelab 的价值不在于把家里变成小机房，而在于给自己一个可以长期演化的工程系统。

它保存的不只是文件。

它也保存了我的工具链、部署链路、排障经验、写作流程和 AI 协作方式。

这可能才是我折腾它这么久的真正原因。
