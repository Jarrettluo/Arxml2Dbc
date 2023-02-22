
## <font align="center">CAN 总线ARXML文件转换为dbc工具</font>


### 演示图片
<img src="https://github.com/Jarrettluo/Arxml2Dbc/blob/master/screenshot.png" alt="imGroup" width="600"/>


### 演示视频

<video src="https://github.com/Jarrettluo/Arxml2Dbc/blob/master/Arxml2Dbc%E8%BD%AF%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B.mp4"
width="600"/>


### 依赖组件
```
cantool
```

### 程序安装

```shell
pip install -i requirements.txt
```

### 启动程序

```shell
python main.py
```

### pyinstaller 打包方法
```
pyinstaller -F -w gui-2.py -i ./resources/switch_128.ico
```