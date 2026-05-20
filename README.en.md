# Zhengchen's Notebook

[简体中文](README.md) | English

Personal blog source, built on [Hugo](https://gohugo.io/) + [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack).

Live at <https://blog.zhengchentao.win/>.

## Local development

```bash
# First-time clone: pull submodules
git clone --recurse-submodules <repo>
# Or, if already cloned:
git submodule update --init --recursive

# Local preview (includes drafts)
hugo server -D

# Production build
hugo --gc --minify
```

Requires Hugo Extended ≥ 0.161.1.

## New post

```bash
hugo new posts/2026-05-06-my-post.md
```

The date in the filename is only for local sorting — the actual publish time
comes from the `date` field in front matter.

## Deployment

Push-to-deploy via Gitea Actions: every push to `main` triggers a build, then
`rsync` ships `public/` to a directory bind-mounted into a long-running nginx
container on the NAS. Filesystem-level sync, no restart needed. Compose file
for the nginx container lives at [deploy/docker-compose.yml](deploy/docker-compose.yml).

## License

* Post content: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
* Theme: see `themes/stack/` for its own license
