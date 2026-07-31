---
title: Cloudflare 一直没缓存我的站，三个月后我才发现为什么
slug: cloudflare-8443-no-cache-tunnel
date: 2026-07-31
tags: [Cloudflare, CDN, 缓存, Cloudflare-Tunnel, NAS, Homelab, 网络排查]
categories: [工程实践]
description: "外网访问慢了三个月，cf-cache-status 全站恒 DYNAMIC。根因是一条看起来无害的 Origin Rule：Cloudflare 对非标端口回源默认禁用缓存，且 Free 计划无解。这篇复盘从症状、排除过程写到最反直觉的发现——规则匹配即触发缓存禁用，与实际回源路径无关——以及迁到 CF Tunnel 后的实测数字。"
draft: false
---

# Cloudflare 一直没缓存我的站，三个月后我才发现为什么

我的家用 NAS 上跑着十几个对外服务：博客、相册、记账、Git、WebDAV，全部挂在 Cloudflare 橙云后面（背景见上一篇[《我把家用 NAS 搭成了一套个人基础设施》](/posts/homelab-nas-infrastructure/)）。从今年 4 月架构定型开始，外网访问就一直慢——首包普遍在一秒半以上，波动时能到两三秒。

我一度以为这就是"家宽 + 免费 CDN"的正常水平，默默接受了三个月。直到有一天认真看了一眼响应头：

```
cf-cache-status: DYNAMIC
```

不是某个服务，是**全站**。博客的 CSS、1MB 的 echarts.min.js、带 hash 文件名的静态资源，全部是 DYNAMIC。Cloudflare 把所有请求都当作动态内容处理，每一次访问都要回源到家里的 NAS——名义上是 CDN，实际只承担了反向代理的角色。

这篇复盘讲清楚三件事：根因是什么、为什么这么难查、以及迁到 Cloudflare Tunnel 之后的实测收益。

## 一、背景：为什么我的回源端口是 8443

要理解这个坑，得先说清楚当初为什么不走标准的 443。

答案带点国内特色：**由于众所周知的原因，家宽的入站 443 是不通的**。这不是猜测，是实测结论：在 OpenWrt 上加一条 `WAN:443 → NAS` 的 DNAT，然后从办公室和境外 VPS 两个方向对着公网 IP 打 443，路由器上的 nft counter 恒为 0——SYN 包根本没到我家。我的 OpenWrt 是 PPPoE 直拨持公网 IP，前面没有光猫路由层，所以结论很干净：包在上游链路就已经被丢弃。

于是 4 月的架构是这样绕的：

```
外网用户 → Cloudflare 橙云（wildcard A 记录指向家宽公网 IP）
        → Origin Rule 把回源端口改写成 8443
        → OpenWrt DNAT WAN:8443 → NAS 反向代理
        → 各 Docker 服务
```

关键角色是那条 **Origin Rule**：`*.mydomain.com` 的请求，回源端口统一改写为 8443。用户侧照常访问 443（那是 CF 边缘的 443，没被封），CF 回源时走 8443 绕开封锁。配合一个 DDNS 脚本跟踪公网 IP 漂移，整套链路看起来一切正常——每个服务都能打开，证书正常，日志正常。

唯一的例外是慢，以及那个当时没有引起注意的 DYNAMIC。

## 二、排查：常规原因逐一排除

静态资源不被缓存，常规嫌疑无非几类。我挨个排：

- **Cache Rule 没生效？** 建了显式规则强制缓存静态扩展名——没用，依旧 DYNAMIC。
- **源站响应头有毒？** 查了 `Cache-Control`、`Vary`、弱 ETag、chunked 编码——都试过修正，无差别。
- **wildcard DNS 的锅？** 给测试子域建了显式 A 记录对照——无差别。
- **有 Worker / Snippet / Page Rule 在半路拦截？** 全查了，账号里一个都没有。

到这一步，情况已经相当反常：一个干净的 zone，没有任何拦截逻辑，源站响应头正确，Cache Rule 明确命中，CF 就是不缓存，而且**没有任何报错和提示**。

最后是在 Cloudflare 官方文档一个很不起眼的页面（[Network ports](https://developers.cloudflare.com/fundamentals/reference/network-ports/)）找到的答案。

## 三、根因：非标端口回源，缓存默认禁用，Free 计划无解

Cloudflare 支持代理一批非标端口（HTTPS 侧有 2053、2083、2087、2096、8443 等），但文档里明确写着：这些端口上的流量**只代理、不缓存**，性能类功能也一律不生效。想解禁？可以，建一条 Cache Rule 就行——但这个能力是 **Enterprise 专属**。

也就是说：

- 缓存可用的回源端口只有 80 / 8080 / 443；
- 8443 属于"能用，但缓存禁用"的灰色名单；
- Free / Pro / Business 没有任何开关能解禁，任何 Cache Rule、cache level、源站 Cache-Control 都无效。

我那条 Origin Rule 把全站回源改写到 8443 的瞬间，整个 zone 的缓存就被静默关掉了。没有告警，没有 dashboard 提示，Cache Rule 界面照样让你建规则、照样显示"已启用"——只是永远不生效。

事后在 Cloudflare Community 搜到一个遇到相同问题的帖子，标题就叫 "Mysterious lack of caching due to origin 8443"。Mysterious 这个词用得相当准确。这个限制真正的问题不在于分层收费本身（商业上可以理解），而在于**它完全静默**：你可以配出一套处处显示正常、实际全部失效的缓存配置。

## 四、意外的转折：切到 Tunnel 之后，依然 DYNAMIC

根因清楚了，方案也顺理成章：既然入站 443 不可用、8443 不给缓存，那就干脆不要入站——上 **Cloudflare Tunnel**。cloudflared 从 NAS 向 CF 边缘发起纯出站连接，边缘把请求顺着这条隧道送回来，回源端口的概念直接消失。

顺带一提，Tunnel 我 4 月评估过并且否掉了，理由有两条："已有固定公网 IP"，以及"CF 有 100MB 上传限制"。三个月后回头看：IP 已经漂了三次，"固定"的前提早已不存在；100MB 是橙云代理的通用限制，跟 Tunnel 无关，早就在生效。当年否决的理由，一条都不再成立。

部署本身不难：一个 cloudflared 容器，dashboard 建 tunnel，把测试子域的 DNS 从 A 记录换成指向 `<tunnel-id>.cfargotunnel.com` 的 CNAME。灰度第一个站，流量确认已经走 tunnel（反代日志里 client IP 变成了 docker 网桥地址），连续两次 GET 同一个静态资源——

还是 DYNAMIC。

这是整个排查里最反直觉的一幕。Origin Rule 的端口改写发生在 CF 的请求处理层：**只要规则匹配，请求就被打上"非标端口回源"的标记，缓存随之禁用**。至于流量实际走不走 8443、走不走 tunnel——并不在判定范围内。我的规则匹配 `*.mydomain.com`，所以哪怕 8443 已经彻底退出链路，缓存依然被禁用。

给 Origin Rule 加上排除条件（`http.host ne "test.mydomain.com"`）之后，立竿见影：DYNAMIC → MISS → HIT。全站迁移完成后，这条规则被整条删除。

如果你也在排查类似的缓存问题：**除了确认流量的实际路径，还应把 Origin Rules 里所有匹配相关域名的规则逐条检查一遍**——它们的副作用在匹配时就已经发生。

## 五、实测数字

迁移前后，从同一台境外机器对同链路做 TTFB 采样（各 5 次，均经 CF 新加坡边缘）：

| 链路 | TTFB | 备注 |
|---|---|---|
| 旧路（8443 DNAT 回源，无缓存） | 0.69–2.50s，中位 ~1.5s | 抖动大 |
| Tunnel 回源，未命中缓存 | 0.39–0.46s | **未命中缓存已有 3 倍以上提升** |
| Tunnel + 边缘缓存 HIT | ~0.31s | 1MB 静态资源从边缘直出 |

两个值得展开的点：

1. **未命中缓存时就已经有 3 倍提升**。这部分收益来自 tunnel 的持久连接：cloudflared 与边缘维持几条常驻连接，省掉了旧链路上每个请求的回源 TCP + TLS 握手。动态应用（.NET 后台、相册）同样获得约 4 倍的 TTFB 改善——这个收益和缓存无关，纯粹是连接模型的差异。
2. **缓存解禁后甚至不需要配置 Cache Rule**。端口限制移除后，CF 对静态扩展名的默认缓存行为自动生效，带 hash 的前端资源直接 MISS → HIT。之前建的那些"强制缓存"规则，从头到尾都不是问题所在。

附带收益同样可观：

- 家里**不再暴露任何入站端口**（8443 的 DNAT 已撤除，从公网探测返回 Connection refused）；
- 外网链路不再依赖家宽公网 IP，跟踪 IP 漂移的 DDNS 脚本随之退役；
- 入站 443 通不通，也不再影响这条链路。

## 六、迁移路上的另外两个坑

**QUIC 在国内环境不可靠，且 cloudflared 不会自动降级。** cloudflared 默认用 QUIC（UDP 7844）连边缘。部署当天测试一切正常，两天后 UDP 通道被切断，外网整站 503——cloudflared 检测到 QUIC 不通后不会自动回退到 TCP，而是停留在断连状态。解法是显式固定协议：环境变量 `TUNNEL_TRANSPORT_PROTOCOL=http2`。国内环境建议部署时就固定 http2，不要把可用性押在 UDP 上。

**在家里测不了外网链路。** 我的内网 DNS 把自家域名劫持到 NAS 直连，不经 CF——这意味着在家做的所有"外网验证"其实都在测内网路径。判别方法很简单：响应头里没有 `cf-ray` 就说明根本没过 Cloudflare。外网链路的验证一律从境外机器发起，这是这次排查里长出来的采样纪律。

（还有一个 NPM strict SNI 与 cloudflared wildcard ingress 的握手坑，比较场景特定，一句话带过：wildcard ingress 指向 IP 时 cloudflared 不发 SNI，开了 strict SNI 的反代会直接拒绝握手，需要在 ingress 里固定 `originServerName` 当锚点。）

## 七、教训

1. **非标端口在 Cloudflare 上有隐性代价，而且是静默的。** 8443 能代理、能过证书、能跑业务，唯独不缓存，且没有任何界面会告诉你这一点。如果你因为各种原因用了非标端口回源，先去查 `cf-cache-status`。
2. **Origin Rule 的副作用在匹配时发生，与实际链路无关。** 排查时把"配置了什么规则"和"流量实际怎么走"当成两个独立变量，分别验证。
3. **"慢"要尽早量化。** 我把 1.5s 的 TTFB 当作"免费 CDN 的正常水平"接受了三个月，实际上 0.3–0.4s 才是这条链路应有的表现。没有基线数字，就没有"不对劲"的触发器。
4. **定期回看被否决的方案。** CF Tunnel 4 月被我否掉，7 月成了最优解——不是方案变了，是前提变了。

---

这套架构迁移完成后，家里的 NAS 对公网是零入站端口的：所有外网流量走 cloudflared 出站隧道，所有内网流量走本地 DNS 直连。回头看，这个"众所周知"的限制反而把这套架构推向了一个更干净的形态——也算是意外的收获。
