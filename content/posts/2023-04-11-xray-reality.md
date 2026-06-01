---
title: "Xray Reality 协议：隐藏服务端 TLS 指纹的现代代理方案"
date: 2023-04-11
lastmod: 2026-06-01
slug: xray-reality
tags: ["TLS", "Xray", "VLESS", "Reality", "X25519", "代理协议"]
categories: ["网络协议"]
description: "REALITY 通过修改 TLS 握手并在主动探测时回落到真实目标站点，降低传统代理常见的证书和服务端指纹特征。本文从协议设计到服务端 / 客户端配置做一份可复查的技术笔记。"
draft: false
---

> 整理自 [bandwh.com](https://www.bandwh.com/net/994.html)（原文 2023-04-11），本文于 2026-06 按 Xray-core v26.x 文档重新核对。
>
> 适用系统：Debian 11 / Ubuntu 22.04+ | Xray 版本：>= 1.8.0；具体最新版请看 [Xray-core releases](https://github.com/XTLS/Xray-core/releases)。2024 起 Xray-core 改用 CalVer，例如 v26.5.9 表示 2026 年 5 月 9 日附近的版本。
>
> 文中所有 UUID / X25519 密钥均为示例值，实际部署务必使用 `xray uuid` / `xray x25519` 重新生成。
>
> 本文是协议学习和自建加密代理的技术笔记。实际使用时请遵守所在地法律法规、云服务商条款和网络使用规范。

---

## 一、背景与原理

### 1.1 为什么需要 Reality？

传统 v2ray 方案需要购买域名并生成 TLS 证书，通过各种流量伪装来规避检测。然而随着 DPI 检测能力的升级，**部分 v2ray / XTLS 组合的协议特征已经更容易被识别**，导致 VPS 的 443 端口频繁被封锁或阻断。

Xray 1.8.0 版本推出 **REALITY 协议**，配合此前的 **Vision 流控**，形成了后来很常见的一套组合：
```
VLESS + Vision + uTLS + REALITY
```

### 1.2 REALITY 的核心优势

| 特性 | 说明 |
|------|------|
| 隐藏服务端 TLS 指纹 | 降低服务端可识别特征，让握手行为尽量接近真实 TLS 访问 |
| 前向保密 | 仍保有 TLS 前向保密性，历史流量无法被解密 |
| 抗证书链攻击 | 主动探测时回放真站证书，避免暴露自签或异常证书链 |
| 无需域名 | 指向他人网站的 SNI，无需自己购买域名或配置 TLS |
| 中间人防御 | 即使客户端配置泄露，攻击者仍难以伪造服务端身份 |
| 缓解 SNI 阻断 | 在部分网络环境中可降低单纯基于 SNI 的阻断概率 |

### 1.3 使用前提

- 一台可访问的 VPS（无需域名）
- 服务端与客户端 **Xray 均需 >= 1.8.0 版本**
- 443 端口不被 Nginx、Caddy 等其他程序占用
- **不支持 CDN 代理**（如 Cloudflare 橙云，会终止 TLS 让 Reality 的端到端伪装失效）。CF **灰云（DNS only）** 只做 DNS 解析、不接管流量，等价于直连 VPS，可正常使用

官方 GitHub：https://github.com/XTLS/REALITY

---

### 1.4 被动监听 vs 主动探测：Reality 的抗检测机制

Reality 的抗识别效果，要分「被动监听」和「主动探测」两种检测场景看才能讲清楚。它不是让流量在所有维度上不可识别，而是尽量减少传统代理暴露出的协议和证书异常。

#### 1.4.1 被动监听：完整握手时序

假设客户端配置 `serverNames: ["www.microsoft.com", "microsoft.com"]`，连接 VPS（IP `203.0.113.10`）的过程：

| 步 | 客户端动作 | 检测方观察到 | VPS 动作 |
|---|---|---|---|
| ① DNS | 查询 VPS 对应的域名（若客户端直接填 IP 则跳过） | 一次明文 DNS 请求；若走 DoH/DoT 加密 DNS 则看不到 | — |
| ② TCP | 解析到 `203.0.113.10`，发起 TCP SYN 到 `203.0.113.10:443` | 客户端跟某境外 IP 建立 TCP 连接 | accept |
| ③ TLS ClientHello | 发送 ClientHello：**SNI = `www.microsoft.com`**，并在握手参数里带上基于 Reality 公钥派生的标记 | TLS 1.3 握手开始，**目标看起来是 www.microsoft.com**；uTLS 尽量模拟 Chrome / Firefox 指纹 | Xray 验证标记 ✓ → 接管连接 |
| ④ 后续 | TLS 握手完成，进入 VLESS 加密流量 | TLS 1.3 握手完成 + 加密流量，协议层特征比传统 v2ray 更少 | 解密 VLESS，按 outbound 转发到目标 |

各被动观察手段实际看到的：

| 观察手段 | 看到的内容 | 单独依靠该维度能否确认？ |
|---|---|---|
| DNS 监听（明文） | 客户端查询某域名 → `203.0.113.10` | 难以仅凭 DNS 判断 |
| TCP/IP 层 | 客户端直连 `203.0.113.10:443` | 难以仅凭端口判断 |
| TLS 握手 SNI | **SNI = `www.microsoft.com`** | 看起来像访问 microsoft，但仍可能结合 IP/ASN 等信息分析 |
| TLS 指纹（JA3 / JA4） | uTLS 模拟的 Chrome / Firefox 指纹 | 难以仅凭 TLS 指纹确认 |
| 流量大小 / 时序 | TLS 1.3 + 加密流量 | 相比传统 v2ray 少了明显规律，但仍可能被统计模型分析 |

#### 1.4.2 主动探测：透明回放真站

Reality 很重要的一点是**应对主动探测**。检测方如果怀疑某个 IP 是代理，会主动发探测请求看看回应。三方角色：**探测方** ／ **VPS (Xray Reality)** ／ **真 www.microsoft.com**：

1. **探测方 → VPS:443**：发送 TLS ClientHello，`SNI = www.microsoft.com`，但**没有 Reality 标记**（探测方没有服务端私钥，无法构造）
2. **VPS Xray**：验证 Reality 标记失败 ✗ → 不当作合法客户端，把这条 TCP 连接**透明转发**给 `target = www.microsoft.com:443`
3. **VPS → 真 www.microsoft.com:443**：原样转发 ClientHello（VPS 不解密、不修改）
4. **真 www.microsoft.com → VPS → 探测方**：microsoft 返回 ServerHello + 真证书 + 真页面，VPS 原样回放给探测方
5. **探测方最终看到的**：完整 TLS 1.3 握手 + microsoft 的真证书（CA 可校验） + microsoft 的真实页面内容 → 从 TLS 握手和证书层看，返回结果更接近真实站点访问

> **实战验证**：Reality 配好后，**用浏览器 IP 直连 `https://<VPS-IP>`** 应该看到「证书 CN 是 www.microsoft.com，但浏览器报 CN 与 IP 不匹配」的警告 —— 这是验证 Reality 回放是否工作的直观方式。能看到 microsoft 的真证书就说明回落机制 OK，反之要查 `target` 出站连通性。

**跟传统 v2ray + TLS 方案的关键差别**：

- **传统方案**（v2ray + WebSocket + TLS + Nginx 反代）：被探测时，VPS 上的 Nginx 用自己的证书回包。即便配了「伪装站」（反代 nginx 默认页或某个真站），证书也通常是你自己域名的证书，和探测请求里的 `microsoft.com` 对不上，证书链这一层就容易暴露。
- **Reality 方案**：不返回任何自己生成的内容。**直接把探测请求中继给真 microsoft**，回包就是 microsoft 自己生成的（证书 / 签名 / 内容全真），至少在 TLS 握手和证书链这一层更接近真实访问。

---

## 二、服务端搭建

### 2.1 安装 Xray

通过官方脚本安装当前发布版（需要 root 权限）：
```bash
sudo bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
```

> 不传 `--version` 会安装当前发布版；想钉版本可改为 `@ install --version <version>`。
>
> 安装完成后，Xray 可执行文件位于 `/usr/local/bin/xray`，配置文件位于 `/usr/local/etc/xray/config.json`，systemd 单元 `xray.service`（以 `nobody` 运行，已授 `CAP_NET_BIND_SERVICE`，可绑 443）。

### 2.2 生成 UUID + X25519 + ShortId

三件套一次出，建议合并执行避免漏：

```bash
echo '---uuid---';     sudo /usr/local/bin/xray uuid
echo '---x25519---';   sudo /usr/local/bin/xray x25519
echo '---shortid---';  openssl rand -hex 8
```

> - **UUID**：客户端身份认证
> - **PrivateKey（私钥）**：填入服务端配置，务必保密
> - **PublicKey（公钥）**：填入客户端配置。新版文档里客户端字段名逐步改成 `password`，但它对应的仍是服务端 X25519 公钥
> - **ML-DSA-65**（v26.x 新增能力）：可选的后量子签名增强，基础 Reality 配置不需要；要启用时请按官方文档检查 target 证书长度和客户端支持
> - **ShortId**：客户端校验位。**不要写 `"88"` `"888888"` 这种弱值**（容易被批量扫探到），用 `openssl rand -hex 8` 生成 8 字节随机数，对应 16 个十六进制字符

### 2.3 编写服务端配置文件

**关键要求：** 回落目标网站（`target` / 旧字段 `dest`）要能正常完成 TLS 握手，且要和 `serverNames` 里的 SNI 对得上。建议选访问稳定、证书链正常的知名站点，本例使用 `www.microsoft.com`。预先验证：

```bash
curl -sI --tlsv1.3 --max-time 5 https://www.microsoft.com -o /dev/null -w 'http=%{http_code}\n'   # 200 即可用
```

配置文件参数说明：

| 参数 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 客户端 UUID，由 `xray uuid` 生成 |
| `flow` | ❌ | 使用 TCP 时填 `xtls-rprx-vision`；H2 协议留空 |
| `target` / `dest` | ✅ | 回落的真实网站，格式 `域名:443`；新版文档使用 `target`，旧字段 `dest` 仍作为别名 |
| `serverNames` | ✅ | 客户端可用的 SNI 列表，通常包含 target 域名及其裸域/子域 |
| `privateKey` | ✅ | 服务端私钥（Private key） |
| `shortIds` | ✅ | 客户端 ID 列表，十六进制，长度为 2 的倍数，最多 16 个十六进制字符。**用 `openssl rand -hex 8` 生成，别用弱值** |
| `maxTimeDiff` | ❌ | 允许的最大时间差（ms），`0` 为不限。建议设置一个合理窗口，例如 `60000`（60s），既宽容时钟漂移又降低重放风险 |
| `show` | ❌ | 是否输出调试信息，默认 `false`，排查问题时改为 `true` |

完整配置示例（监听 `::` 一次绑 v4 + v6）：
```json
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "listen": "::",
      "port": 443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "94b60beb-a0fd-4aff-9c7c-9a36f74022db",
            "flow": "xtls-rprx-vision"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "show": false,
          "target": "www.microsoft.com:443",
          "xver": 0,
          "serverNames": [
            "www.microsoft.com",
            "microsoft.com"
          ],
          "privateKey": "<PRIVATE_KEY_FROM_xray_x25519>",
          "minClientVer": "",
          "maxClientVer": "",
          "maxTimeDiff": 60000,
          "shortIds": [
            "<openssl_rand_hex_8_output>"
          ]
        }
      }
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom",
      "tag": "direct"
    },
    {
      "protocol": "blackhole",
      "tag": "blocked"
    }
  ]
}
```

### 2.4 写入配置并启动

**写入配置文件**（heredoc 写法避免编辑器缩进问题）：
```bash
sudo tee /usr/local/etc/xray/config.json > /dev/null <<'EOF'
{ ... 上方 JSON ... }
EOF
sudo /usr/local/bin/xray run -test -config /usr/local/etc/xray/config.json   # 必跑：先校验 JSON
sudo systemctl enable xray --now                                              # 启用并立即启动（开机自启已内置）
```

**常用服务管理命令**：
```bash
sudo systemctl restart xray
sudo systemctl status xray
sudo journalctl -u xray -f          # 跟踪日志
sudo ss -tlnp | grep 443            # 验证监听
```

### 2.5 排错方法

**v26.x 一个常见坑：默认 `loglevel: warning` 不一定打印 `listening` 行**，启动后用 `journalctl` 可能只能看到 `Xray 26.x started` 然后就没下文，看起来「started 但没在 listen」。这时以 `ss -tlnp | grep 443` 为准。要肉眼确认，可以临时把 `loglevel` 改 `debug` 跑前台：

```bash
# 配置检查
sudo /usr/local/bin/xray run -test -config /usr/local/etc/xray/config.json

# 临时改 debug 跑前台，看到 [Info] transport/internet/tcp: listening TCP on [::]:443 才算 OK
sudo sed -i 's/"loglevel": "warning"/"loglevel": "debug"/' /usr/local/etc/xray/config.json
sudo timeout 5 /usr/local/bin/xray run -config /usr/local/etc/xray/config.json
# 排错完改回 warning，重启服务
```

常见问题排查：
- **客户端测试超时但服务端没日志** → 流量根本没到 xray。用 `sudo tcpdump -i any 'tcp port 443' -nn` 看是否收到 SYN：
  - 收不到 SYN → 链路问题（云防火墙没开、客户端代理设置错），跟 xray 无关
  - 收到 SYN 但客户端重传 SYN 看不到 ACK → 服务器 SYN-ACK 在回程被丢弃
  - 收到完整三次握手但 xray 日志显示 `REALITY: processed invalid connection: server name mismatch` → 客户端 SNI / 公钥 / shortId 不匹配
- **客户端导入 URL 后连不上但手动填字段就好**：部分 iOS 客户端（如 Shadowrocket）对 `vless://` 里的 `pbk` `sid` `flow` 字段解析有时丢字段，**优先手动填**而非 URL 导入
- 检查 443 端口占用：`sudo ss -tlnp | grep 443`
- 检查 JSON 格式：`sudo /usr/local/bin/xray run -test -config /usr/local/etc/xray/config.json`
- 确认 `target` 能正常 TLS 访问：`curl -sI --tlsv1.3 https://www.microsoft.com`（200 即可用）
- AWS Lightsail / GCP / 阿里云等带云防火墙的实例，**OS 层 ufw 通了不算**，云控制台里的实例防火墙也要单独开 443（IPv4 + IPv6 都要）

---

## 三、可选：BBR 加速

VPS 到客户端链路丢包高时，BBR 拥塞控制能显著提升 TCP 吞吐。Linux kernel ≥ 4.9 已内置 BBR（Ubuntu 22.04 / Debian 11 都满足），**不需要第三方脚本**，直接 sysctl 开启：

```bash
sudo tee /etc/sysctl.d/99-bbr.conf > /dev/null <<'EOF'
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
EOF
sudo sysctl --system

# 验证
sysctl net.ipv4.tcp_congestion_control   # 应输出 bbr
lsmod | grep bbr                          # 应看到 tcp_bbr
```

立即生效，无需重启。

---

## 四、客户端配置

### 4.1 客户端通用参数

连接服务端时需填写以下关键参数：

| 参数 | 说明 |
|------|------|
| 地址（Address） | VPS 的 IPv4 或 IPv6（v6 用 `[2600:...]:443` 这种带方括号格式） |
| 端口（Port） | `443` |
| 用户 ID | 服务端配置中的 UUID |
| 流控（Flow） | `xtls-rprx-vision` |
| 加密（Encryption） | `none` |
| 传输协议（Network/Transport） | `tcp` 或「原始/none」（不要套 ws/grpc） |
| 安全类型（Security） | `reality` |
| SNI | 与服务端 `serverNames` 一致，如 `www.microsoft.com` |
| 公钥（PublicKey / password） | 服务端生成的 X25519 公钥；新版文档里的客户端字段名叫 `password` |
| ShortId | 服务端 `shortIds` 中的任意一项 |
| uTLS 指纹（Fingerprint） | 建议填 `chrome` 或 `firefox` |
| ALPN | 默认 `h2,http/1.1` 或留空都行（不影响 Reality 握手） |
| 多路复用（Mux） | **关闭**（Vision 与 Mux 不兼容） |
| TLS「允许不安全」/ Insecure | **关闭**（Reality 自带证书校验逻辑） |

### 4.2 客户端速查

截至 2026-06，大多数主流客户端已经内置支持 Reality 的 Xray-core，下载最新版通常即可，无需手动切 Pre-Release：

| 平台 | 客户端 | 下载 |
|---|---|---|
| Windows | V2rayN | https://github.com/2dust/v2rayN/releases |
| macOS | V2rayU / FoXray | https://github.com/yanue/V2rayU/releases |
| Android | V2rayNG | https://github.com/2dust/v2rayNG/releases |
| iOS | Shadowrocket（付费）/ Streisand | App Store |
| OpenWrt | PassWall2 / SSR Plus+ | 建议使用近期维护版，老编译版本可能缺 Reality / Vision 支持 |
| 通用核心 | sing-box / Clash.Meta（mihomo） | 各发行版仓库或 GitHub |

**iOS Shadowrocket 注意**：URL 导入有时会丢字段（特别是 `pbk` `sid` `fp`），导致测试延迟超时但客户端不报错。**遇到测速失败优先手动按 4.1 字段表填**，不要依赖 URL 导入。

---

## 五、安全性深度解析

### 5.1 为什么使用公私钥而非仅 UUID？

传统方案若使用对称密钥（UUID），攻击者一旦获取客户端配置，即可实施中间人攻击。

REALITY 使用 **X25519 非对称密钥 + 修改后的 TLS 握手** 机制：
- 即使攻击者获取到客户端公钥，也**难以验证某条连接是否属于 REALITY**
- 难以进行有效的中间人攻击

> REALITY 的设计原则是：**默认假设客户端配置已泄露**，将安全边界收敛至服务端私钥。只要服务端私钥不泄露，攻击者就难以伪装服务端。即使私钥泄露，攻击者也无法直接解密历史流量（前向保密），但可以尝试中间人攻击，因此私钥仍然要按高敏感凭据管理。

建议：**定期更换公私钥对**，公钥可在多个客户端间安全共享。

### 5.2 如何解决 TLS in TLS 问题？

「TLS in TLS」指内层 TLS 握手特征暴露的问题（即加密套娃特征）。  

REALITY 本身就是 TLS，可直接复用 **XTLS Vision** 的成熟解决方案：Vision 会对内层 TLS 握手包进行**填充处理（不加密，直接发送）**，从而降低 TLS 套 TLS 的可识别特征。

此外，HTTP/2 与 gRPC 自带多路复用，也可配合 REALITY 使用，进一步优化网络性能。

---

## 六、注意事项

- Reality **不支持 CDN 代理**（如 Cloudflare 橙云），请勿将域名套 CDN 代理使用；CF **灰云（DNS only）** 仅做 DNS 解析不接管流量，等同直连 VPS，可以用（CF 在链路里只起 DNS 提供商作用）
- `target` / `dest` 目标网站需要能正常 TLS 访问，建议选用 `www.microsoft.com`、`www.icloud.com`、`www.apple.com` 等访问稳定、证书链正常的知名站点。Cloudflare 系站点未必不能用，但由于边缘节点、证书和握手行为变化较多，排错成本更高
- 服务端 443 端口在使用期间不能被其他程序（Nginx、Caddy 等）占用，80 端口无特殊要求
- ShortId **不要用弱值**（`88` `888888` 这种），用 `openssl rand -hex 8` 生成 16 个十六进制字符；`maxTimeDiff` 建议设一个合理窗口，例如 `60000`（60s），防重放又宽容时钟漂移
- 技术持续更新，请关注 Xray 官方仓库（<https://github.com/XTLS/Xray-core/releases>）与官方 wiki（<https://xtls.github.io/>）获取最新版本信息

---

*本文最初整理自 [bandwh.com](https://www.bandwh.com/net/994.html)（2023-04，对应 Xray 1.8.0），2026-06 根据 Xray-core v26.x 文档重新核对。*
