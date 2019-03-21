#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2019-03-20 10:55:35
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
import os
import sys
import json
import time
import threading
# ----------------------------------------------------------------------------
_scripts = []
_setting = ''
_pos = 0
_callbackfile = ''
_python3path = sys.executable
_dirname, _filename = os.path.split(os.path.abspath(sys.argv[0]))
_wlogfile = "log/witch.log"
_logfile = ''
_run = True
# ----------------------------------------------------------------------------
def mlog(s):
    #print(s)
    with open(_wlogfile,"a") as f:
        f.write("["+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+"] "+str(s)+"\n")
def sh(c):  # 执行shell命令
    mlog("[ ! ] %s"%(c))
    return str(os.popen(c).readlines())
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def loadsetting():#加载配置
    global _setting,_logfile
    try:
        with open("%s/setting.json" % (_dirname), "r") as f:
            _setting = json.load(f)
            _logfile = "%s/%s/%s/latest.log" % (_dirname,_setting['minecraft_path'],_setting['log_path'])
            return True
    except Exception as e:
        return False
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def loadscripts():#加载配置中脚本列表
    global _scripts
    try:
        with open("%s/setting.json" % (_dirname), "r") as f:
            _scripts = json.load(f)['script']
            return True
    except Exception as e:
        return False
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
            mlog("[ - ] 错误，读取文件信息失败!")
            exit()
        time.sleep(1)
        return flast()
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def getrealpath(path):#获取真实脚本路径
    if '/' not in path:
        return _dirname + "/" +"scripts/"+path
    elif path[0:3] == '../':
        return _dirname + "/" + path
    else:
        return path
def runscripts():#执行脚本
    if loadscripts():
        lst = flast()
        if lst =='':
            mlog("[ - ] 未读取到信息.")
            return False
        for d in _scripts:
            if d['enable']:
                mlog("[ ! ] run %s " % (d['name']))
                if d['name'][-3:] == ".sh":
                    shmsg = sh("/bin/sh %s %s %" % (getrealpath(d['name']),str(lst)))
                    mlog("[ ! ] result: "+str(shmsg))
                elif d['name'][-3:] == ".py":
                    shmsg = sh("%s %s %s" % (_python3path,getrealpath(d['name']),str(lst)))
                    mlog("[ ! ] result: "+str(shmsg))
                elif d['name'][-4:] == ".php":
                    shmsg = sh("php %s?last=" % (getrealpath(d['name']),str(lst)))
                    mlog("[ ! ] result: "+str(shmsg))
                else:
                    mlog("[ - ] 不支持的脚本类型!")
    else:
        mlog("[ - ] 获取脚本列表失败!")
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
def start():
    global _pos
    while _run:
        if os.path.isfile(_logfile):
            time.sleep(1)
            try:
                if os.path.getsize(_logfile) != _pos:
                    mlog("[ ! ] 新的改变!")
                    _pos = os.path.getsize(_logfile)
                    runscripts()
            except Exception as e:
                continue
        else:
            time.sleep(1)
    mlog("[ ! ] exit")
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
# 传入参数 要监控文件路径 回调文件路径
def main():
    global _pos,_run
    if not loadsetting():
        mlog("[ - ] 配置文件加载失败!")
        exit()
    if not os.path.isfile(_logfile):
        mlog("[ - ] 要监控的文件没找到!")
        exit()
    _pos = os.path.getsize(_logfile)
    threading.Thread(target=start)
    while True:
        ret = input(":")
        if ret == "quit":
            _run = False
            break
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>
if __name__ == '__main__':
    main()
