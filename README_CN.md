# 手势控制贪吃蛇游戏

[English](README.md)

![游戏演示](https://github.com/wangqiqi/interesting_assets/raw/main/images/gensture_snake2.png)

## 简介

手势贪吃蛇是一款结合计算机视觉与经典贪吃蛇游戏的互动游戏。玩家通过摄像头捕捉的手势来控制蛇的移动方向。游戏屏幕分为两部分：左侧显示实时视频流和手部跟踪，右侧显示贪吃蛇游戏。

## 特点

- 使用手势控制蛇的移动
- 实时手部跟踪和手势识别
- 分屏界面同时显示视频流和游戏画面
- 经典贪吃蛇游戏机制，带有食物邻近检测功能
- 基于得分的游戏速度调整
- 墙壁碰撞切换（可穿墙或碰墙结束游戏）
- 背景音乐和音效
- 暂停/继续功能
- 网格显示切换
- 帮助信息显示

## 游戏玩法

1. 将手放在摄像头前
2. 使用拇指和食指形成方向
3. 拇指和食指之间的角度决定蛇的移动方向：
   - 向上指：蛇向上移动
   - 向右指：蛇向右移动
   - 向下指：蛇向下移动
   - 向左指：蛇向左移动
4. 收集食物（红色方块）使蛇变长并增加分数
5. 避免蛇撞到自己的身体或墙壁（如果启用了墙壁碰撞）

## 控制方式

- **手势**：控制蛇的方向
- **P键**：暂停/继续游戏
- **R键**：游戏结束时重新开始
- **G键**：显示/隐藏网格
- **W键**：启用/禁用墙壁碰撞
- **H键**：显示/隐藏帮助信息
- **M键**：开启/关闭音乐
- **+/-键**：增加/减少游戏速度
- **ESC键**：退出游戏

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/gesture-snake.git
   cd gesture-snake
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

3. 运行游戏：
   ```
   python run.py
   ```

## 音效

游戏支持以下音效：
- 背景音乐
- 吃食物音效
- 方向变化音效
- 游戏结束音效

将您的音效文件放在`sounds`目录中，使用以下文件名：
- `background.mp3`：背景音乐
- `eat.mp3`：吃食物时的音效
- `turn.mp3`：改变方向时的音效
- `game_over.mp3`：游戏结束时的音效

## 系统要求

- Python 3.7+
- 摄像头
- 查看 `requirements.txt` 获取Python包依赖

## 项目结构

```
gesture-snake/
├── assets/              # 图像和资源
├── sounds/              # 音效和音乐
├── src/                 # 源代码
│   ├── game/            # 贪吃蛇游戏逻辑
│   ├── gesture/         # 手势检测
│   └── __init__.py
├── tests/               # 单元测试
├── .gitignore           # Git忽略文件
├── LICENSE              # MIT许可证
├── README.md            # 主README文件
├── README_CN.md         # 本文件
├── requirements.txt     # Python依赖
└── run.py               # 主入口点
```

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 微信：znzatop

![微信](https://github.com/wangqiqi/interesting_assets/raw/main/images/wechat.jpg)

## 更多项目

更多有趣的项目请见：https://github.com/wangqiqi/interesting_assets.git

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。 