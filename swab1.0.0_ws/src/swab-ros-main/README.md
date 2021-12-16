# swab-ros

ros package for swabbing machine

### Contents

- [System Structure](#System-Structure)
- [Installation](#Installation)
- [Usage](#Usage)
- [Usb_cam](#Usb_cam)
- [Panel](#Panel)
- [Tof](#Tof)
- [Swab](#Swab)
- [Camcam](#Camcam)

## System Structure

![](https://i.imgur.com/pgbQWgX.png)

## Installation

- Clone the package into the source directory

        cd ~/ros-workspace/src
        git clone https://github.com/tohow06/swab-ros.git

- Install libusb driver

        sudo apt install libusb-dev

- Build the packages

        cd ~/ros-workspace
        catkin_make

- Add in environment

        source ~/ros-workspace/src/devel/setup.bash
        
## Usage

- Test All function

          roslaunch swab testAll.launch

> 一次執行所有 package

## usb_cam

相機由 usb_cam 負責驅動相機，並將照片傳送至 ros topic
可以使用下面指令測試相機

        roslaunch usb_cam usb_cam-test.launch

## panel

控制器由`panel`負責

- `/script/sticks.py`會採樣並發送搖桿的訊號至 ros topic
- `/script/button.py`會採樣並發送按鈕的訊號至 ros topic

## tof

tof 由`tof`負責

- `/src/tof_talker.py`會讀取並發送 tof 訊號至 ros topic

## swab

這個 package 負責接收處理 panel 的資訊，並傳送指令給 concerto

- `/src/panel_info.py`會計算出要下達的指令
- `/src/http_lai.py`負責與 concerto 溝通，傳送下達指令，並讀取 limit switch 的狀態

## camcam

負責產生 GUI 介面，繪製圖示，顯示採檢狀態等

- `/src/camcam.py`接收 topic 資訊，利用 opencv 製作 gui

## joystick_drivers

> 使用遊戲搖桿代替 panel 時使用，已停用

搖桿由`joy`這個 package 負責
透過`/joystick_drivers/joy/src/joy_node.cpp`將資料傳進 ros

先確定 linux 有沒有讀到搖桿

```
ls /dev/input
```

通常搖桿代號是 js0
有的話即可執行

```
rosrun joy joy_node
```

成功後會發布 rostopic: `/joy`
可以使用 ros 指令來檢查

```
rostopic echo /joy
```

然後我們使用`joy_one.py`來調整`/joy`的數值
並將調整完的數值以`/joy_information`發送出來

```
rosrun swab joy_one.py
```

> 不同搖桿有各種按鍵配置 one 代表為 xbox 搖桿適用
