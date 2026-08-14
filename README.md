# mengde

 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Build Status](https://travis-ci.org/wateret/mengde.svg?branch=master)](https://travis-ci.org/wateret/mengde) 

Project mengde is named after the courtesy name(Mèngdé 孟德) of Cáo Cāo 曹操 from Chinese Three Kingdoms period.
This game is inspired by "三國志曹操傳" by 1998, KOEI.

There are features in common between mengde and 三國志曹操傳.

- Similar game system
    - Battle system : Turn-based with square tiles
    - Stat system : 5 stats along with HP and MP which are the same
	- Hero system : All heroes have different class and stat which makes each hero special
- Same graphical resources

## For gamers

This game is not complete for playing yet.

### 东周列国志 MOD（Windows）

给其他玩家使用时，发布 `release\Ekgd-portable-win64.zip`。玩家完整解压后双击 `Ekgd\Ekgd.exe`，无需安装 Python，也不需要项目源码或命令行。不要只复制单个 EXE，必须保留旁边的 `_internal` 文件夹。

便携版存档保存在 `%LOCALAPPDATA%\Ekgd\saves`，启动错误日志保存在 `%LOCALAPPDATA%\Ekgd\logs\startup-error.log`。

开发机重新打包：

```powershell
.\.venv-rl\Scripts\python.exe -m pip install -r packaging\requirements-portable.txt
.\tools\build_portable.ps1
```

第一回使用 `game/sce/dongzhou` 下的 Lua 剧本。进入项目目录后运行：

```powershell
cd C:\mengde
.\.venv-rl\Scripts\python.exe -m rl.play_gui --scenario dongzhou --assets-root "D:\Downloads\LZC传（Li自成）\LZC传（Li自成）"
```

开场、胜利和失败过场均由关卡 Lua 文件中的 `gstory` 表驱动；战场、人物和胜负条件由同一关卡文件中的 `gstage` 及回调函数驱动。

当前 GUI 入口 `rl/play_gui.py` 会加载同目录的固定 Python 3.10 运行载荷 `rl/_play_gui_runtime.cpython-310.pyc`。发布或迁移时两者必须一同保留；不要把该载荷当作普通 `__pycache__` 删除。

## For scenario(MOD) developers

TBD

## For game engine developers

For now we only have instructions for build.

### Reinforcement learning / Mirror Mode

The Fire Emblem Mirror Mode method has been ported as a headless Gymnasium environment using the real mengde rule engine. It includes legal-action masking, demonstration recording, behavioral cloning, GAIL, and masked PPO. See [the Chinese RL guide](docs/reinforcement_learning_zh.md) for architecture, build, data collection, training, and evaluation commands.

### How to Build

#### Required Tools and Packages

* CMake
* SDL2
* SDL2 TTF
* Lua 5.2
* boost >= 1.52

#### macOS

```
$ brew install cmake sdl2 sdl2_ttf lua boost
$ ./build.py
$ build/Darwin.x86_64.Debug/game/game
```

#### Ubuntu

```
$ apt-get install cmake libsdl2-dev libsdl2-ttf-dev liblua5.2-dev libboost-system-dev libboost-filesystem-dev
$ ./build.py
$ build/Linux.x86_64.Debug/game/game
```

##### Building with Docker

Take the following steps to build mengde through Docker:

1. Install Docker on your machine as described in the [Docker documentation](https://docs.docker.com/install/).
2. Optionally, create a Linux group called docker to allow launching containers without sudo as described in the [Docker documentation](https://docs.docker.com/install/linux/linux-postinstall/). (If you don't do this step, you'll have to use sudo each time you invoke Docker.)
3. Create a Docker image for building the mengde.
```
$ docker build -t {image_tag_name} docker
```

4. Launch a Docker container that contains one of created binary images for building.
```
$ docker run --rm -v `pwd`:{mount_path_on_container} -w={mount_path_on_container} {image_tag_name} ./build.py
```

##### Cross build for ARM(Raspberry Pi 2/3)

You need to install required packages
```
sudo apt-get install qemu qemu-user-static binfmt-support debootstrap
sudo apt-get install binutils-arm-linux-gnueabihf
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
```

You then need to prepare a root filesystem. Only ARMv7l is supported for now.
```
$ sudo ./cross/build-rootfs.sh
```
Root file system will be prepared in `./cross/rootfs/armv7l`

After it's prepared, you can build with `--cross` option.
```
$ ./build.py --cross armv7l
```

#### Windows

TBD

