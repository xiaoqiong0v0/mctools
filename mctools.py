#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-03-12
# @Author  : ${afubek} (${email})
# @Link    : ${link}
# @Version : $1.0.0$
import os
import re
import sys
import json
import time
import readline
# ----------------------------------------------------------------------------
_setting = ''
"""{'minecraft_path':'../minecraft',
    'log_path':"logs",
    'restart':False,
    'restart_time':"0h",
    'script':[{'name':name,'enable':true}]}"""
_logfile = ''
_rfcount = 0
_rchar = ["-","\\","|","/"]
_dirname, _filename = os.path.split(os.path.abspath(sys.argv[0]))
_python3path = sys.executable
#print(sys.executable)
#print("[ ! ] now path： %s now file: %s" % (_dirname,_filename))
# ----------------------------------------------------------------------------
def checkp(p):
    if not os.path.exists(p):
        print("[ - ] 文件夹(", p, ")不存在，请检查路径，或程序完整性")
        return False
    return True
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def checkf(f):
    if not os.path.isfile(f):
        print("[ - ] 文件(", f, ")不存在，请检查路径，或程序完整性")
        return False
    return True
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def mexit():
    input('按回车键结束...')
    exit()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
# @return '' or {'startf':startf(读取到最后一条的文件指针位置),'time':stime(时间),'message':message(信息)}
def flast():  # 读取日志文件最后一条信息
    global _rfcount
    try:
        with open(_logfile, 'rb') as f:
            al = str(f.readlines())
            if "[Server " not in al:
                return ''
            off = -1
            fsize = os.path.getsize(_logfile)
            while True:
                f.seek(off, 2)
                lines = f.readlines()[0].decode("utf-8")
                if "[Server " in lines:
                    f.seek(off-11, 2)
                    linesarr = f.readlines()
                    lines = ''
                    for i in linesarr:
                        lines += i.decode("utf-8")
                    stime = lines[1:9]
                    message = lines[11:]
                    startf = fsize + off
                    retdata = {'startf':startf,'time':stime,'message':message}
                    return retdata
                if off == -fsize:
                    return ''
                off -= 1
        _rfcount = 0
    except Exception as e:
        _rfcount += 1
        if _rfcount == 3:
            print("[ - ] 错误，读取文件信息失败!")
            mexit()
        time.sleep(1)
        return flast()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def sh(c):  # 执行shell命令
    return str(os.popen(c).readlines())
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def shmc(c):  # 向服务器端所在screen发送指令
    return str(os.popen("screen -S mcserver -X stuff \"%s\n\"" % (c)).readlines())
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def shmn(c):  # 向监控程序所在screen发送指令
    return str(os.popen("screen -S mcmonitor -X stuff \"%s\n\"" % (c)).readlines())
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def chekrunning():  # 检查服务器端是否正常运行，如果配置没错而没有运行，则启动它
    if "command not found" in sh("screen -v"):
        print('请先安装screen组件(apt-get/yum install screen)')
        mexit()
    if "mcserver" in sh("screen -ls"):
        if not checkp(_logfile):
            mexit()
        else:
            lst = flast()
            if '' == lst or "Shutdown" in lst['message']:
                print("[ - ] 服务器端出错关闭,正在重启...")
                shmc("java -Xms1024M -Xmx1536M -jar server.jar")
                time.sleep(1)
                tw = 0
                while True:
                    lst = flast()
                    if "[Server thread/INFO]: Done" in lst['message']:
                        print("[ + ] 启动完成!")
                        break
                    time.sleep(1)
                    tw += 1
                    if tw > 120:
                        print("[ - ] 启动超时!")
                        mexit()
                    print("\b\r[ ",_rchar[tw%4]," ] 正在启动...")
            return True
    return False
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def checkmonitor():#检查监控程序是否运行
    if "command not found" in sh("screen -v"):
        print('请先安装screen组件(apt-get/yum install screen)')
        mexit()
    return ("mcmonitor" in sh("screen -ls"))
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def startmonitor():#开启监控程序
    sh("screen -dmS mcmonitor")
    time.sleep(1)
    shmn("cd %s" % (_dirname))
    shmn("%s monitor.py" % (_python3path))
    print("[ + ] 已执行.")
    mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def stopmonitor():#停止监控程序
    shmn("quit")
    time.sleep(2)
    shmn("exit")
    print("[ + ] 已执行.")
    mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def start():  # 启动mc服务器
    sh("screen -dmS mcserver")
    time.sleep(1)
    shmc("cd %s/%s" % (_dirname,_setting['minecraft_path']))
    shmc("java -Xms1024M -Xmx1536M -jar server.jar")
    tw = 0
    while True:
        lst = flast()
        if "[Server thread/INFO]: Done" in lst['message']:
            print("[ + ] 启动完成!")
            break
        time.sleep(1)
        tw += 1
        if tw > 120:
            print("[ - ] 启动超时!")
            mexit()
        print("\b\r[ ",_rchar[tw%4]," ] 正在启动服务器端...")
    mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def shutdown():  # 关闭mc服务器
    shmc("stop")
    tw = 0
    while True:
        lst = flast()
        if lst == '' or "Shutdown" in lst['message'] or "Saving chunks for level 'world'/minecraft:" in lst['message']:
            break
        time.sleep(1)
        tw += 1
        if tw > 30:
            print("[ - ] 关闭超时!")
            mexit()
        print("\b\r[ ",_rchar[tw%4]," ] 正在关闭服务器端...")
    time.sleep(3)
    tw = 0
    print("...")
    while True:
        if "mcserver" not in sh("screen -ls"):
            print("[ + ] 服务器端已关闭!")
            break
        shmc("exit")
        time.sleep(1)
        tw += 1
        if tw > 15:
            print("[ - ] 关闭超时!")
            mexit()
        print("\b\r[ ",_rchar[tw%4]," ] 正在关闭后台会话...")
    mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def restart(auto=False):  # 重启mc服务器
    shmc("stop")
    tw = 0
    auto and print("[ ! ] 正在关闭服务器端...")
    while True:
        lst = flast()
        if lst == '' or "Shutdown" in lst['message'] or "Saving chunks for level 'world'/minecraft:" in lst['message']:
            break
        time.sleep(1)
        tw += 1
        if tw > 30:
            print("[ - ] 关闭超时!")
            mexit()
        not auto and print("\b\r[ ",_rchar[tw%4]," ] 正在关闭服务器端...")
    time.sleep(3)
    shmc("java -Xms1024M -Xmx1536M -jar server.jar")
    tw = 0
    print("...")
    auto and print("[ ! ] 正在启动服务器端...")
    while True:
        lst = flast()
        if "[Server thread/INFO]: Done" in lst['message']:
            print("[ + ] 启动完成!")
            break
        time.sleep(1)
        tw += 1
        if tw > 120:
            print("[ - ] 启动超时!")
            mexit()
        not auto and print("\b\r[ ",_rchar[tw%4]," ] 正在启动服务器端...")
    not auto and mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def resetcron(action,onlydel=False):#重置系统任务
    state = str(sh("service crond status"))
    if "running" not in state:
        sh("chkconfig crond start")
    sh("sed -i '/mctools.py %s/d' /var/spool/cron/root" % (action))
    if onlydel:
        return
    if not os.path.exists("%s/log" % (_dirname)):
        os.mkdir("%s/log" % (_dirname))
    try:
        with open("/var/spool/cron/root","a") as f:
            if 'H' in _setting['restart_time'] or 'h' in _setting['restart_time']:
                f.write("0 */%s * * * %s %s/mctools.py %s 2>&1 >>%s/log/%s.log\n" % (_setting['restart_time'][0:-1],_python3path,_dirname,action,_dirname,action))
            else:
                rt_time = _setting['restart_time'][0:-1]
                rt_time = int(rt_time)
                rt_time = rt_time if rt_time >10 else 10
                f.write("*/%s * * * * %s %s/mctools.py %s 2>&1 >>%s/log/%s.log\n" % (rt_time,_python3path,_dirname,action,_dirname,action))
        return True
    except Exception as e:
        return False
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def loadsetting():#加载配置
    global _setting,_logfile
    try:
        with open("%s/setting.json" % (_dirname), "r") as f:
            _setting = json.load(f)
            _logfile = "%s/%s/%s/latest.log" % (_dirname,_setting['minecraft_path'],_setting['log_path'])
            return True
    except Exception as e:
        print(e)
        return False
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def savesetting():#保存配置
    try:
        with open("%s/setting.json" % (_dirname), "w") as f:
            json.dump(_setting, f)
    except Exception as e:
        print("[ - ] 写入配置文件失败，请检查目录权限.")
        mexit()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>       
def settingrestart():#设置自动重启
    global _setting
    while True:
        brk = False
        if _setting['restart']:
            print("=========自动重启已经打开=========")
            print("=========1、-关闭自动重启=========")
        else:
            print("=========自动重启已经关闭=========")
            print("=========1、-开启自动重启=========")
        print("=========2、-设置重启时间=========")
        print("=========0、---返回主菜单=========")
        while True:
            sel = input("[ + ] 请输入选择\n:")
            try:
                sel = int(sel)
            except Exception as e:
                print("[ - ] 请输入数字!")
                continue
            if sel == 1:
                if _setting['restart']:
                    _setting['restart'] = False
                    resetcron('restart',True)
                else:
                    _setting['restart'] = True
                    if not resetcron('restart'):
                        print("[ - ] 设置失败,请稍后再试或提升权限.")
                savesetting()
                break
            elif sel == 2:
                while True:
                    retime = input("[ + ] 请输入时间(nh/H/m/M)(最小为10m/M)\n:")
                    rex = '[1-9]{1}[0-9]{0,8}(h|m|H|M)'
                    if None != re.match(rex,retime):
                        _setting['restart_time'] = retime
                        break
                    else:
                        print("[ - ] 格式不正确!")
                retip = input("[ + ] 请输入提示语(不修改直接回车)\n:")
                if retip.strip() != '':
                    _setting['restart_tip'] = retip
                savesetting()
                _setting['restart'] and resetcron("restart")
                break
            elif sel == 0:
                brk = True
                break
            else:
                print("[ - ] 输入错误!")
        if brk:
            break
    mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def serverswitch(li):
    i = 1
    for d in li:
        print('-- ',i,":",d['title'])
        i+=1
    print('--  0 : 返回')
    while True:
        sel = input("[ + ] 请输入选择\n:")
        try:
            sel = int(sel)
        except Exception as e:
            print("[ - ] 请输入数字!")
            continue
        if sel == 0:
            break
        elif sel > 0 and sel <= len(li):
            shmc(li[sel-1]['cmd'])
            print("[ + ] 已执行.")
            break
        else:
            print("[ - ] 输入错误!")
    serversetting()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def serversetting():  # 服务器端设置
    print("=========服务器端-设置=========")
    print("=======1、---默认游戏模式======")
    print("=======2、------游戏难度=======")
    print("=======3、------游戏时间=======")
    print("=======4、------游戏天气=======")
    print("=======0、----返回主菜单=======")
    while True:
            sel = input("[ + ] 请输入选择\n:")
            try:
                sel = int(sel)
            except Exception as e:
                print("[ - ] 请输入数字!")
                continue
            if sel == 1:
                serverswitch([
                    #adventure|creative|spectator|survival
                    {'title':'生存','cmd':'defaultgamemode survival'},
                    {'title':'创造','cmd':'defaultgamemode creative'},
                    {'title':'冒险','cmd':'defaultgamemode adventure'},
                    {'title':'旁观','cmd':'defaultgamemode spectator'}
                    ])
            elif sel == 2:
                serverswitch([
                    #easy|hard|normal|peaceful
                    {'title':'简单','cmd':'difficulty easy'},
                    {'title':'正常','cmd':'difficulty normal'},
                    {'title':'困难','cmd':'difficulty hard'},
                    {'title':'超和平','cmd':'difficulty peaceful'}
                    ])
            elif sel == 3:
                serverswitch([
                    #day|midnight|night|noon
                    {'title':'白天','cmd':'time set day'},
                    {'title':'午夜','cmd':'time set midnight'},
                    {'title':'夜晚','cmd':'time set night'},
                    {'title':'早晨','cmd':'time set noon'}
                    ])
            elif sel == 4:
                serverswitch([
                    #clear|rain|thunder
                    {'title':'无','cmd':'weather clear'},
                    {'title':'下雨','cmd':'weather rain'},
                    {'title':'打雷','cmd':'weather thunder'}
                    ])
            elif sel == 0:
                break
            else:
                print("[ - ] 输入错误!")
    mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def commandtip():
    print("ls 显示当前脚本\nadd filepath 添加脚本\ndel/enable/disable filename/number 移除/启用/禁用包含名称或数字标志的脚本\nquit 返回主菜单")
def checkhad(name):
    for d in _setting['script']:
        if d['name'] == name:
            return True
    return False
def addscript():  # 添加反馈脚本
    global _setting
    if not os.path.exists("%s/scripts" % (_dirname)):
        os.mkdir("%s/scripts" % (_dirname))
    while True:
        code = input("[ + ] 请输入指令\n:")
        if "ls" in code:
            if len(_setting['script']) == 0:
                print("[ - ] 当前没有添加脚本!")
            else:
                i = 1
                for d in _setting['script']:
                    print(i,"、",d['name'],"    ","enable" if d['enable'] else "disable")
                    i += 1
        elif "add " in code:
            fpath = code[4:].strip()
            if fpath == '':
                print("[ - ] 文件路径不能为空!")
            elif checkhad(fpath):
                print("[ - ] 该脚本已添加!")
            elif '/' not in fpath:
                if os.path.isfile("%s/scripts/%s" % (_dirname,fpath)):
                    _setting['script'].append({'name':fpath,'enable':False})
                    savesetting()
                    print("[ + ] 添加成功!")
                else:
                    print("[ - ] 文件不存在!")
            else:
                if os.path.isfile(fpath):
                    _setting['script'].append({'name':fpath,'enable':False})
                    savesetting()
                    print("[ + ] 添加成功!")
                else:
                    print("[ - ] 文件不存在!")
        elif "del " in code:
            fpath = code[4:].strip()
            if fpath.isdigit():
                fpath = int(fpath)
                if fpath>0 and fpath <= len(_setting['script']):
                    _setting['script'].pop(fpath-1)
                    savesetting()
                    print("[ + ] 移除成功!")
                else:
                    print("[ - ] 数字不在范围内!")
            elif fpath =='*':
                _setting['script'] = []
                savesetting()
                print("[ + ] 已移除所有项!")
            elif fpath == '':
                print("[ - ] 文件路径不能为空!")
            else:
                ded = 0
                for d in _setting['script']:
                    if fpath in d['name']:
                        ded += 1
                        _setting['script'].remove(d)
                if ded == 0:
                    print("[ + ] 没有脚本被移除!")
                else:
                    savesetting()
                    print("[ + ] 移除成功!")
        elif "enable" in code:
            fpath = code[7:].strip()
            if fpath.isdigit():
                fpath = int(fpath)
                if fpath>0 and fpath <= len(_setting['script']):
                    _setting['script'][fpath-1]['enable'] = True
                    savesetting()
                    print("[ + ] 启用成功!")
                else:
                    print("[ - ] 数字不在范围内!")
            elif fpath == '':
                print("[ - ] 文件路径不能为空!")
            else:
                ded = 0
                for d in _setting['script']:
                    if fpath in d['name']:
                        ded += 1
                        d['enable'] = True
                if ded == 0:
                    print("[ + ] 没有脚本被启用!")
                else:
                    savesetting()
                    print("[ + ] 启用成功!")
        elif "disable" in code:
            fpath = code[8:].strip()
            if fpath.isdigit():
                fpath = int(fpath)
                if fpath>0 and fpath <= len(_setting['script']):
                    _setting['script'][fpath-1]['enable'] = False
                    savesetting()
                    print("[ + ] 禁用成功!")
                else:
                    print("[ - ] 数字不在范围内!")
            elif fpath == '':
                print("[ - ] 文件路径不能为空!")
            else:
                ded = 0
                for d in _setting['script']:
                    if fpath in d['name']:
                        ded += 1
                        d['enable'] = False
                if ded == 0:
                    print("[ + ] 没有脚本被禁用!")
                else:
                    savesetting()
                    print("[ + ] 禁用成功!")
        elif "quit" in code:
            break
        else:
            print("[ - ] 错误指令!")
            commandtip()
    mainmenu()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def mainmenu():  # 主菜单
    if chekrunning():
        print("=========服务器端正常运行中=========")
        print("=========1、---重启服务器端=========")
        print("=========2、---关闭服务器端=========")
        print("=========3、---设置自动重启=========")
        print("=========4、-----服务端设置=========")
        print("=========5、---管理反馈脚本=========")
        mr = checkmonitor()
        if mr:
            print("=========6、---关闭监控程序=========")
        else:
            print("=========6、---开启监控程序=========")
        print("=========0、-------退出程序=========")
        while True:
            sel = input("[ + ] 请输入选择\n:")
            try:
                sel = int(sel)
            except Exception as e:
                print("[ - ] 请输入数字!")
                continue
            if sel == 1:
                restart()
                break
            elif sel == 2:
                shutdown()
                break
            elif sel == 3:
                settingrestart()
                break
            elif sel == 4:
                serversetting()
                break
            elif sel == 5:
                addscript()
                break
            elif sel == 6:
                stopmonitor() if mr else startmonitor()
                break
            elif sel == 0:
                mexit()
            else:
                print("[ - ] 输入错误!")
    else:
        print("=========服务器端当前未运行=========")
        print("=========1、---开启服务器端=========")
        print("=========2、---设置自动重启=========")
        print("=========3、---添加反馈脚本=========")
        print("=========0、-------退出程序=========")
        while True:
            sel = input("[ + ] 请输入选择\n:")
            try:
                sel = int(sel)
            except Exception as e:
                print("[ - ] 请输入数字!")
                continue
            if sel == 1:
                start()
                break
            elif sel == 2:
                serversetting()
                break
            elif sel == 3:
                addscript()
                break
            elif sel == 0:
                mexit()
            else:
                print("[ - ] 输入错误!")
            
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def init():
    global _setting
    isf = os.path.isfile("%s/setting.json" % (_dirname))
    if not isf:
        print('[ - ] 未找到配置文件,准备初始化...')
    if isf and not loadsetting():
        print("[ - ] 读取配置文件失败！请检查目录权限.")
        mexit()
    if _setting == '':
        _setting = {'minecraft_path': '../minecraft',
                    'log_path': "logs",
                    'restart': False,
                    'restart_time': "0h",
                    'restart_tip':'',
                    'script': []}
        while True:
            path = input("[ + ] 请输入minecraft目录路径，默认为\"../minecraft\"\n:")
            if path.strip() == '' and checkp("%s/%s" % (_dirname,_setting['minecraft_path'])) or path.strip() != '' and checkp(path):
                break
        if path.strip() != '':
            _setting['minecraft_path'] = path
        if not checkp("%s/%s/%s" % (_dirname,_setting['minecraft_path'], _setting['log_path'])):
            while True:
                logs_path = input("[ - ] 如果已经修改logs文件夹目录请输入(默认minecraft目录下)\n:")
                if checkp("%s/%s/%s" % (_dirname,_setting['minecraft_path'], logs_path)):
                    break
            _setting['log_path'] = logs_path
        try:
            with open("%s/setting.json" % (_dirname), "w") as f:
                json.dump(_setting, f)
        except Exception as e:
            print("[ - ] 写入配置文件失败，请检查目录权限.")
            mexit()
    if not checkp("%s/%s" % (_dirname,_setting['minecraft_path'])) or not checkp("%s/%s/%s" % (_dirname,_setting['minecraft_path'], _setting['log_path'])):
        print("或配置配置文件setting.json")
        mexit()
    mainmenu()
# ----------------------------------------------------------------------------
def main():
    if len(sys.argv)>1 and sys.argv[1] != None and sys.argv[1].strip() != '':
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),":AUTO-",sys.argv[1])
        print(":")
        isf = os.path.isfile("%s/setting.json" % (_dirname))
        if not isf:
            print('[ - ] 未找到配置文件')
            print('[ - ] 停止自动任务')
            resetcron(sys.argv[1],True)
            exit()
        if isf and not loadsetting():
            print("[ - ] 读取配置文件失败！请检查目录权限.")
            resetcron(sys.argv[1],True)
            exit()
        if sys.argv[1] == 'restart':
            _setting['restart_tip'].strip() != '' and shmc("say %s"%(_setting['restart_tip']))
            shmc("say 服务器即将在5分钟后重启")
            time.sleep(300)
            for i in range(5,15):
                shmc("say 服务器即将在%s秒后重启" % (15-i+6))
                time.sleep(1)
            for b in range(0,5):
                shmc("say %s" % (5-b))
                time.sleep(1)
            restart(True)
        if sys.argv[1] == "changecall":
            #未完成
            print("call")
    else:
        init()
if __name__ == '__main__':
    main()
