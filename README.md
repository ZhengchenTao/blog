# 陶政辰的博客

简体中文 | [English](README.en.md)

个人博客源码，基于 [Hugo](https://gohugo.io/) 和 [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack)。

线上地址：<https://blog.zhengchentao.win/>

## 内容

- `content/posts/`：文章
- `content/about/`：关于页
- `assets/`：自定义样式和图片
- `themes/stack/`：主题 submodule

## 本地开发

```bash
git clone --recurse-submodules <repo>
cd blog

hugo server -D
```

需要 Hugo Extended ≥ 0.161.1。

生产构建：

```bash
hugo --gc --minify
```

## License

* 文章内容：[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh)
* 主题：见 `themes/stack/` 自身 license
