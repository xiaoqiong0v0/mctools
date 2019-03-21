# mctools
<b>我的世界服务器管理工具<b /><br />
<pre>主要功能:
服务器端开关
定时重启
服务器端设置
新消息脚本调用

运行环境:
linux + python3 + screen

screen安装:
apt-get install screen
readline-devel安装:
apt-get install readline-devel

下载 mctools.py 和 monitor.py
在服务的minecraft同级目录下创建mctools文件夹
把上诉两个文件放入文件夹
控制台输入 python3 mctools.py运行程序

开启监控程序时如果服务器产生新的信息将
变量脚本列表并执行
将以以下方式调用脚本:
'''script.py {'startf':startf(读取到最后一条的文件指针位置),'time':stime(时间),'message':message(信息)}'''</pre>
