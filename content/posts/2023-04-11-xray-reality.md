---
title: "Xray Reality 协议：消除 TLS 指纹的现代代理方案"
date: 2023-04-11
lastmod: 2026-05-03
slug: xray-reality
tags: ["TLS", "Xray", "VLESS", "Reality", "X25519", "代理协议"]
categories: ["网络协议"]
description: "REALITY 协议通过 TLS 1.3 key_share 字段嵌入身份标记 + 主动探测时透明回放真站，从协议层消除 TLS 指纹特征。本文从协议设计到服务端 / 客户端完整搭建。"
draft: false
---

> 整理自 [bandwh.com](https://www.bandwh.com/net/994.html)（原文 2023-04-11），本文于 2026-05 重新整理发布。  
> 适用系统：Debian 11 | Xray 版本：>= 1.8.0  
> 文中所有 UUID / X25519 密钥均为示例值，实际部署务必使用 `xray uuid` / `xray x25519` 重新生成。

---

## 一、背景与原理

### 1.1 为什么需要 Reality？

传统 v2ray 方案需要购买域名并生成 TLS 证书，通过各种流量伪装来规避检测。然而随着 DPI 检测能力的升级，**v2ray 的 TLS/XTLS 协议特征已可被精准识别**，导致 VPS 的 443 端口频繁被封锁或阻断。

Xray 1.8.0 版本推出了全新的 **REALITY 协议**，配合此前的 **Vision 流控**，组成了当前最新的协议组合：
```
VLESS + Vision + uTLS + REALITY
```

### 1.2 REALITY 的核心优势

| 特性 | 说明 |
|------|------|
| 消除 TLS 指纹 | 消除服务端 TLS 指纹特征，令流量与真实网站无异 |
| 前向保密 | 仍保有 TLS 前向保密性，历史流量无法被解密 |
| 抗证书链攻击 | 证书链攻击无效，安全性超越常规 TLS |
| 无需域名 | 指向他人网站的 SNI，无需自己购买域名或配置 TLS |
| 中间人防御 | 即使客户端配置泄露，审查方也无法进行有效中间人攻击 |
| SNI 阻断消失 | 据实测，使用 Reality 后 SNI 阻断现象消失 |

### 1.3 使用前提

- 一台可访问的 VPS（无需域名）
- 服务端与客户端 **Xray 均需 >= 1.8.0 版本**
- 443 端口不被 Nginx、Caddy 等其他程序占用
- **不支持 CDN 代理**（如 Cloudflare 橙云，会终止 TLS 让 Reality 的端到端伪装失效）。CF **灰云（DNS only）** 只做 DNS 解析、不接管流量，等价于直连 VPS，可正常使用

官方 GitHub：https://github.com/XTLS/REALITY

---

## 二、服务端搭建

### 2.1 安装 Xray

通过官方脚本安装指定版本：
```bash
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install --version 1.8.0
```

> `--version 1.8.0` 可按需替换为更新版本号。  
> 安装完成后，Xray 可执行文件位于 `/usr/local/bin/xray`，配置文件位于 `/usr/local/etc/xray/config.json`。

### 2.2 生成 UUID

UUID 用于客户端身份认证：
```bash
cd /usr/local/bin/
./xray uuid > uuid
cat uuid   # 查看生成的 UUID
```

### 2.3 生成 X25519 公私钥对

REALITY 使用非对称密钥替代传统 UUID 认证，安全性更高：
```bash
cd /usr/local/bin/
./xray x25519 > key
cat key    # 查看生成的公钥（PublicKey）和私钥（PrivateKey）
```

> - **PrivateKey（私钥）**：填入服务端配置，务必保密
> - **PublicKey（公钥）**：填入客户端配置，可多端共享

### 2.4 编写服务端配置文件

**关键要求：** 回落目标网站（`dest`）必须支持 TLSv1.3，建议使用国外知名大站，本例使用 `www.amazon.com`。

配置文件参数说明：

| 参数 | 必填 | 说明 |
|------|------|------|
| `id` | ✅ | 客户端 UUID，由 `xray uuid` 生成 |
| `flow` | ❌ | 使用 TCP 时填 `xtls-rprx-vision`；H2 协议留空 |
| `dest` | ✅ | 回落的真实境外网站，格式 `域名:443` |
| `serverNames` | ✅ | 客户端可用的 SNI 列表，需与 dest 匹配 |
| `privateKey` | ✅ | 服务端私钥（Private key） |
| `shortIds` | ✅ | 客户端 ID 列表，十六进制，长度为 2 的倍数，上限 16 位 |
| `maxTimeDiff` | ❌ | 允许的最大时间差（ms），`0` 为不限，建议设 10000~60000 |
| `show` | ❌ | 是否输出调试信息，默认 `false`，排查问题时改为 `true` |

完整配置示例：
```json
{
  "inbounds": [
    {
      "listen": "0.0.0.0",
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
          "dest": "www.amazon.com:443",
          "xver": 0,
          "serverNames": [
            "amazon.com",
            "www.amazon.com"
          ],
          "privateKey": "UCWnsGnHIqsCgb10JzaL7TaC9pZKJSSax9vW-QbaVkM",
          "minClientVer": "",
          "maxClientVer": "",
          "maxTimeDiff": 0,
          "shortIds": [
            "88",
            "888888"
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

### 2.5 写入配置并启动

**写入配置文件：**
```bash
nano /usr/local/etc/xray/config.json
# 粘贴上方配置，Ctrl+X 退出，按 Y 确认保存
```

**服务管理命令：**
```bash
service xray start    # 启动 Xray
service xray stop     # 停止 Xray
service xray restart  # 重启 Xray
service xray status   # 查看运行状态
```

### 2.6 排错方法

若服务启动报错，可将配置中 `"show": false` 改为 `"show": true`，然后手动运行查看详细日志：
```bash
/usr/local/bin/xray -c /usr/local/etc/xray/config.json
```

常见问题排查：
- 检查 443 端口是否被其他程序占用：`ss -tlnp | grep 443`
- 检查配置文件 JSON 格式是否有误（注释需删除）
- 确认 `dest` 目标网站支持 TLSv1.3：`curl -v --tlsv1.3 https://www.amazon.com`

---

## 三、可选：BBR 加速

VPS 到国内线路较差时，可安装 BBR 拥塞控制算法提升 TCP 吞吐量：
```bash
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh \
  && chmod +x bbr.sh \
  && ./bbr.sh
```

安装完成后按提示重启 VPS 即可生效。

---

## 四、客户端配置

### 4.1 客户端通用参数

连接服务端时需填写以下关键参数：

| 参数 | 说明 |
|------|------|
| 地址（Address） | VPS 的 IP 地址 |
| 端口（Port） | `443` |
| 用户 ID | 服务端配置中的 UUID |
| 流控（Flow） | `xtls-rprx-vision` |
| 加密（Encryption） | `none` |
| 传输协议（Network） | `tcp` |
| 安全类型（Security） | `reality` |
| SNI | 与服务端 `serverNames` 一致，如 `www.amazon.com` |
| 公钥（PublicKey） | 服务端生成的 Public key |
| ShortId | 服务端 `shortIds` 中的任意一项，如 `88` |
| uTLS 指纹（Fingerprint） | 建议填 `chrome` 或 `firefox` |

### 4.2 Windows 客户端（V2rayN）

- 下载地址：https://github.com/2dust/v2rayN/releases
- 需使用最新版本，确保内置 Xray-Core >= 1.8.0
- 若版本不足，进入「设置」→ 勾选「检查 Pre-Release 版本更新」后更新核心
- 操作路径：「服务器」→「添加 [VLESS] 服务器」→ 按上表填写各参数

### 4.3 Android 客户端（V2rayNG）

- 下载地址：https://github.com/2dust/v2rayNG/releases
- 同样需使用支持 Reality 的最新版本

### 4.4 路由器端（OpenWrt）

- 适用于 2023 年 4 月后编译的含 ShadowSocksR Plus+ 的固件
- 在插件设置界面中选择 VLESS 协议，填写对应的 Reality 参数

---

## 五、安全性深度解析

### 5.1 为什么使用公私钥而非仅 UUID？

传统方案若使用对称密钥（UUID），攻击者一旦获取客户端配置，即可实施中间人攻击。

REALITY 使用 **X25519 非对称密钥 + TLSv1.3 key_share** 机制：
- 即使攻击者获取到客户端公钥，也**无法验证某条连接是否属于 REALITY**
- 更无法进行有效的中间人攻击

> REALITY 的设计原则是：**默认假设客户端配置已泄露**，将安全边界收敛至服务端私钥。只要服务端私钥不泄露，流量就是安全的。即使私钥泄露，攻击者也无法直接解密历史流量（前向保密），只能尝试中间人攻击，但中间人需要持有 Reality 私钥才能伪装服务端，这做不到。

建议：**定期更换公私钥对**，公钥可在多个客户端间安全共享。

### 5.2 如何解决 TLS in TLS 问题？

"TLS in TLS" 指内层 TLS 握手特征暴露的问题（即加密套娃特征）。  

REALITY 本身就是 TLS，可直接复用 **XTLS Vision** 的成熟解决方案：Vision 会对内层 TLS 握手包进行**填充处理（不加密，直接发送）**，从而消除 TLS 套 TLS 的可识别特征。

此外，HTTP/2 与 gRPC 自带多路复用，也可配合 REALITY 使用，进一步优化网络性能。

---

## 六、注意事项

- Reality **不支持 CDN 代理**（如 Cloudflare 橙云），请勿将域名套 CDN 代理使用；CF **灰云（DNS only）**仅做 DNS 解析不接管流量，等同直连 VPS，可以用（CF 在链路里只起 DNS 提供商作用）
- `dest` 目标网站必须支持 TLSv1.3，建议选用 `www.amazon.com`、`www.microsoft.com` 等国际知名站点
- 服务端 443 端口在使用期间不能被其他程序（Nginx、Caddy 等）占用
- 80 端口无特殊要求
- 技术持续更新，请关注 Xray 官方仓库获取最新版本信息

---

*本文整理自 [bandwh.com](https://www.bandwh.com/net/994.html)，如有更新请以原文为准。*