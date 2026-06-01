# Zhengchen's Blog

[简体中文](README.md) | English

Personal blog source, built with [Hugo](https://gohugo.io/) and [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack).

Live at <https://blog.zhengchentao.win/>.

## Content

- `content/posts/`: posts
- `content/about/`: about page
- `assets/`: custom styles and images
- `themes/stack/`: theme submodule

## Local development

```bash
git clone --recurse-submodules <repo>
cd blog

hugo server -D
```

Requires Hugo Extended ≥ 0.161.1.

Production build:

```bash
hugo --gc --minify
```

## License

* Post content: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
* Theme: see `themes/stack/` for its own license
