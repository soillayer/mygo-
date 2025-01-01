# MygoMemeHelper - 表情包助手

MygoHelper 是一个便捷的表情包管理和快速选择工具，帮助用户更高效地管理和使用表情包。

## 功能特点

-  表情包快速选择和预览
-  本地表情包管理
-  快速搜索功能
-  便捷的状态窗口
-  支持快捷键操作

## 项目结构

```
/MygoHelper/
├── src/                    # 源代码目录
│   ├── meme_selector.py    # 表情包选择器
│   ├── status_window.py    # 状态窗口
│   └── utils/             # 工具函数
├── scripts/                # 脚本文件
│   ├── download_images.py  # 图片下载脚本
│   └── create_icon.py     # 图标创建脚本
├── data/                   # 数据文件
│   └── image_map.json     # 图片映射配置
├── config/                 # 配置文件
│   └── config.json        # 主配置文件
├── resources/             # 资源文件
│   └── icon.ico          # 应用图标
└── run.py                 # 主程序入口
```

## 安装说明

1. 下载最新版本的 MygoHelper.zip
2. 解压到任意目录
3. 运行 MygoHelper.exe

## 使用方法

1. 启动程序后，系统托盘会出现 MygoHelper 图标
2. 使用默认快捷键（可在配置文件中自定义）打开表情选择器
3. 输入关键词搜索表情包
4. 选择需要的表情包即可使用

## 配置说明

配置文件位于 `config/config.json`，可以自定义：
- 快捷键设置
- 图片保存路径
- 界面显示设置
- 其他个性化选项

## 系统要求

- Windows 10 及以上系统
- Python 3.6+（如果从源码运行）

## 开发说明

如果要从源码运行：

1. 克隆仓库
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
3. 运行主程序：
   ```
   python run.py
   ```

## 许可证

MIT License