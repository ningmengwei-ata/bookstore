---
title: 设计思维 Git协作
date: 2020-07-15 08:46:11
tags:
- 笔记
- 设计思维
- 暑期
---

# 小项目2

1. 实验室网站
2. github上搭建个人网站(参照x-lab)实验室相关即可。
3. https://github.com/X-lab2017/xlab-website
4. 通过小项目体会代码协作方式
5. CMS系统。

Github与网盘的区别是github具有协作。

## Github开放式协作流程

<!--more-->

### 开源协作模式

fork(fork)函数。

![](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggrcou30b3j31340igarl.jpg)

老师把改好的卷子叫pull request，修改错误，merge request

PR包含了两个分支间的状态差异信息。

PR看作一个分支？向自己的仓库提交新的commit。

仓库与分支

![](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggrcqnnzggj31340naaou.jpg)

需要在PR的标题和正文中描述对其进行了哪些感动。

协作模式

远程仓库的master分支都是受到保护的。

![](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggrcsr8pdij30ii094wh4.jpg)

从远程的dev向远程的master分支做PR。

1. 将上游fork到自己的namespace下，origin clone到本地。
2. 在本地更改后，origin/dev->upstream/master提交PR。
3. 当PR被合并后，即被持久化保留到了上游
4. 此时在本地master同步变更
5. 再删除掉工具人/dev分支

为什么要在master上切新的分支，而不是在master分支上直接做改动呢？

切分支可以支持多feature开发。

渲染框架：Hugo

样式框架：Academic



GitHub Pages ：xxx.github.io

直接将静态文件放置。

域名反向代理；

[ x-lab官方](https://github.com/X-lab2017/xlab-website)

![](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggrd5jfs77j312w0lekdr.jpg)

githubID与github昵称。

![](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggrd7duvq3j30pc0p4aof.jpg)

![](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggrd9s6gupj30gu0omn2r.jpg)

## 注意的问题

1. commit 信息的规范
2. 正文关联issue：Related #6(?)
3. ![](https://tva1.sinaimg.cn/large/007S8ZIlgy1ggrdjdu29oj313y0omtk5.jpg)
4. 代码仓库与部署仓库

