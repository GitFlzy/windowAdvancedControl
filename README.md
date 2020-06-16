# windowAdvancedControl

windows 下更方便控制窗口的自用小工具

![image](https://github.com/GitFlzy/windowAdvancedControl/blob/master/demo.gif)

## 功能

触发热键：<kbd>ctrl</kbd>+<kbd>alt</kbd>

窗口任意位置按住热键后
  - 窗口随光标移动
  - 上滑缩小窗口
  - 下滑扩大窗口

## 存在问题

- 部分窗口有自己的滑动逻辑，这个工具的放缩功能会被屏蔽掉或者同时触发
- 小概率在刚运行工具时会“假死”，鼠标移动缓慢，重新启动工具可解决

## 环境

- win10, 界面缩放 150%
- python3.8
- pynput, pywin32

## 以后可能会做的事情

- 修复滑动屏蔽的问题
- 更方便的关闭窗口
- 其他现在还没有想到的
