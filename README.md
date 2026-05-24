# 今日能量小卡片

这是一个放在 GitHub Pages 上的每日网页小卡片。它不需要你电脑开机，GitHub Actions 会每天自动生成 `data.json`，部署网页，并通过 PushPlus 推送打开链接。

## 现在包含

- 手机友好的漂亮网页
- 每天变化的主题配色、贴纸和动态背景
- 点击开启的每日 BGM
- 天气和穿衣建议
- 在一起多少天、纪念日倒计时
- 两个人生日倒计时
- 情人节、520、521、六一、七夕、圣诞、跨年等节日倒计时
- 两个人各自星座运势
- 更详细的星座内容：能量、幸运物、感情建议、事务建议
- 今天适合干嘛、不适合干嘛
- 今日小安排：约会灵感、照片任务、今日小食、提前准备
- 男朋友想提醒她的话
- 每日一句话

手机浏览器通常不允许自动播放音乐，所以 BGM 需要点一下按钮开启。

## 先改你的信息

打开 `G:\xiaoyi-card\config.json`，重点改这些：

```json
"people": {
  "girlfriend": {
    "nickname": "小仪",
    "birthday": "2001-10-22",
    "sign": "天秤座"
  },
  "boyfriend": {
    "nickname": "小尹",
    "birthday": "2000-02-13",
    "sign": "水瓶座"
  }
},
"profile": {
  "relationship_start": "2026-05-21"
}
```

如果以后想加额外节日，可以在 `custom_festivals` 里添加：

```json
"custom_festivals": [
  {
    "name": "第一次见面",
    "date": "08-20",
    "kind": "纪念",
    "tone": "适合翻一翻以前的照片，再说一句当时没说出口的话。"
  }
]
```

固定节日会每年自动循环。七夕是农历节日，脚本里先内置了 2026-2030 年的公历日期，后面年份可以继续补。

## 音乐说明

默认是“生成式轻音乐”：网页每天按日期生成一段不同的轻音乐，不调用 AI，也不涉及版权。

不能直接从网易云、QQ 音乐、酷狗等音乐 App 随机抓歌，因为这通常需要授权、登录、接口权限，也会涉及版权和反爬。

如果你以后有合法可用的 mp3 链接或自己上传的音乐文件，可以在 `config.json` 里这样配置：

```json
"music": {
  "mode": "track",
  "tracks": [
    {
      "title": "今日轻音乐",
      "artist": "自定义",
      "src": "https://example.com/music-1.mp3"
    }
  ]
}
```

放多个 `tracks` 后，脚本会每天按日期随机选一首。

## 本地预览

```powershell
cd /d G:\xiaoyi-card
python -s .\scripts\generate_daily.py
python -s -m http.server 8765 --bind 127.0.0.1
```

然后打开：

```text
http://127.0.0.1:8765/
```

## 上传 GitHub

1. 在 GitHub 新建仓库，比如 `xiaoyi-card`。
2. 上传 `G:\xiaoyi-card` 里的所有文件。
3. 进入仓库 `Settings` -> `Pages`。
4. `Build and deployment` 选择 `GitHub Actions`。

## 配置 Secrets

进入仓库：

```text
Settings -> Secrets and variables -> Actions -> New repository secret
```

添加：

- `PUSHPLUS_TOKEN`：你的 PushPlus token。
- `PUSHPLUS_TO`：她的 PushPlus 好友令牌；不填就是默认发给 token 所属账号。

可选：

- `PAGES_URL`：网页地址，比如 `https://你的用户名.github.io/xiaoyi-card/`。

## 自动推送时间

当前是北京时间每天 21:10。GitHub Actions 使用 UTC，所以工作流里写的是：

```yaml
cron: "10 13 * * *"
```

## 手动运行

上传后进入：

```text
Actions -> Daily Xiaoyi Card -> Run workflow
```

成功后，页面一般是：

```text
https://你的用户名.github.io/仓库名/
```

## 安全提醒

不要把 PushPlus token 写进仓库。正式推送用 GitHub Secrets。
