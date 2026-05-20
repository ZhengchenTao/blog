# 陶政辰的笔记本

简体中文 | [English](README.en.md)

个人博客源码，基于 [Hugo](https://gohugo.io/) + [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack)。

线上地址：<https://blog.zhengchentao.win/>

## 目录结构

```
.
├── .gitea/workflows/   # Gitea Actions：push 后自动 build + rsync 到 NAS
├── archetypes/         # 新文章模板
├── assets/             # 自定义 SCSS / 图片
├── content/            # 正文
│   ├── about/          # 关于页
│   ├── archives/       # 归档页
│   ├── posts/          # 文章
│   └── search/         # 搜索页
├── deploy/             # NAS 上 nginx 容器的 docker-compose（参考用）
├── themes/stack/       # 主题（git submodule）
└── hugo.yaml           # Hugo 配置
```

## 本地开发

```bash
# 第一次拉代码记得带上 submodule
git clone --recurse-submodules <repo>
# 或：已经 clone 了
git submodule update --init --recursive

# 本地预览（含草稿）
hugo server -D

# 生产构建
hugo --gc --minify
```

需要 Hugo Extended ≥ 0.161.1。

## 写一篇新文章

```bash
hugo new posts/2026-05-06-my-post.md
```

文件名里的日期只是给自己排序用，真正决定发布时间的是 front matter 里的 `date`。

## 部署

不用手动部署。流程：

1. `git push` 到 `main`
2. Gitea Actions（`.gitea/workflows/build.yml`）在 runner 里跑 `hugo --gc --minify`
3. `rsync` 把 `public/` 推到 NAS 上的 `/blog-public/`（host 模式 bind mount）
4. NAS 上常驻的 nginx 容器只读挂载该目录，文件系统层同步，无需重启

NAS 上 nginx 容器的 compose 文件见 [deploy/docker-compose.yml](deploy/docker-compose.yml)，只在重建时用得到。

## License

* 文章内容：[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh)
* 主题：见 `themes/stack/` 自身 license
