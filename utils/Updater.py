import hashlib
import os
import subprocess
import traceback

import requests
import tkinter as tk
from tkinter import messagebox

githubURL = ''
target_size = 0
mainWindow = None

#错误时的处理
def error(e):
    '''
    错误时的信息处理
    :param e: 错误信息
    :return: void
    '''
    changeState([0,0,1,0,0,0],e)

def md5sum(fname):
    '''
    计算文件MD5值
    :param fname: 文件路径
    :return: String：该文件的MD5值
    '''
    if not os.path.isfile(fname):
        return False
    try:
        f = open(fname, 'rb')
    except:
        return False
    m = hashlib.md5()
    # 大文件处理
    while True:
        d = f.read(8096)
        if not d:
            break
        m.update(d)
    ret = m.hexdigest()
    f.close()
    return ret

def getGithubURL():
    '''
    获取Github镜像链接
    :return: status
    '''
    global githubURL
    ips = None
    try:
        ips = eval(requests.get('https://raw.hellogithub.com/hosts.json',verify=False).text)
        for i in ips:
            if i[1] == 'github.com':
                githubURL = i[0]
        return 0
    except Exception:
        error(f'{traceback.format_exc()}\n{ips}')
        return 1

def download(url,path):
    '''下载文件'''
    global mainWindow
    # 请求下载地址，以流式的。打开要下载的文件位置。
    with requests.get(url, stream=True, verify=False) as r, open(path, 'wb') as file:
        total_size = int(r.headers['content-length'])
        mainWindow.logger.info('下载大小：'+str(total_size))
        content_size = 0
        for content in r.iter_content(chunk_size=1024):
            file.write(content)
            # 统计已下载大小
            content_size += len(content)
            # 计算下载进度
            percent = round((content_size / total_size) * 100,1)
            mainWindow.updating_progress['text'] = mainWindow.updating_text.format(percent)
        return 0

def changeState(mode,msg):
    '''
    更换窗口状态
    :param mode: 模式[正在检测更新,最新版本,更新错误,检测到更新,正在更新,更新完毕]
    :param msg: 在更新错误和检测到更新时的文字信息
    :return:
    '''
    if mode[0]:
        mainWindow.getting_update.pack(side=tk.TOP, fill=tk.X)
    else:
        mainWindow.getting_update.pack_forget()
    if mode[1]:
        mainWindow.up_to_date.pack(side=tk.TOP, fill=tk.X)
    else:
        mainWindow.up_to_date.pack_forget()
    if mode[2]:
        mainWindow.error_text.configure(state=tk.NORMAL)
        mainWindow.error_text.delete(1.0,tk.END)
        mainWindow.error_text.insert(tk.END,msg)
        mainWindow.error_text.configure(state=tk.DISABLED)
        mainWindow.update_error.pack(side=tk.TOP, fill=tk.X)
    else:
        mainWindow.update_error.pack_forget()
    if mode[3]:
        mainWindow.update_text['text'] = mainWindow.update_msg.format(msg[0],msg[1])
        mainWindow.need_update.pack(side=tk.TOP, fill=tk.X)
    else:
        mainWindow.need_update.pack_forget()
    if mode[4]:
        mainWindow.updating.pack(side=tk.TOP, fill=tk.X)
        mainWindow.updating_progress['text'] = mainWindow.updating_text.format(msg[2])
    else:
        mainWindow.updating.pack_forget()
    if mode[5]:
        mainWindow.update_complete.pack(side=tk.TOP, fill=tk.X)
    else:
        mainWindow.update_complete.pack_forget()

def update():
    global mainWindow
    # 更新脚本
    toastScript = '{}\\toast.ps1'.format(mainWindow.work_dir)
    toastContent = 'Add-Type -AssemblyName System.Windows.Forms\n$global:balloon = New-Object System.Windows.Forms.NotifyIcon\n$balloon.Icon = "{}"\n$balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info\n$balloon.BalloonTipText = "这可能需要一些时间，请稍候..."\n$balloon.BalloonTipTitle = "CountBoard 正在进行更新"\n$balloon.Visible = $true\n$balloon.ShowBalloonTip(10)'.format(mainWindow.icon)
    with open(toastScript,'w+',encoding='gbk') as f:
        f.write(toastContent)
    indexA = toastScript.find('\\')+1
    indexB = len(toastScript)-''.join(reversed(toastScript)).find('\\')
    toastScriptPath = list(toastScript)
    toastScriptPath.insert(indexA,"'")
    toastScriptPath.insert(indexB,"'")
    toastScriptPath = ''.join(toastScriptPath)
    updateScript = '{}\\Update.vbs'.format(mainWindow.work_dir)
    updateContent = 'Set ws = createobject("wscript.shell")\n{0}\nws.run "powershell.exe Set-ExecutionPolicy RemoteSigned",0,True\nws.run "powershell.exe {1}",0,True\nws.run "taskkill /t /f /im CountBoard.exe",0,True\nSet file = CreateObject("Scripting.FileSystemObject")\nfile.DeleteFile("{2}")\nfile.CopyFile "{3}","{2}",True\nws.run "{2}",0\nfile.DeleteFile("{3}")\nfile.DeleteFile("{4}")\nfile.DeleteFile("{6}")\nfile.DeleteFile("{5}")'.format(mainWindow.elevate_script,toastScriptPath,mainWindow.exe_dir_path + '\\CountBoard.exe',mainWindow.work_dir + '\\Update.exe',mainWindow.work_dir + '\\.UpdateDownloaded',updateScript,toastScript)
    with open(updateScript,'w+',encoding='utf-8') as f:
        f.write(updateContent)
    messagebox.showinfo('CountBoard 更新','CountBoard 即将进行更新，将会自动退出程序并请求管理员权限')
    subprocess.Popen('wscript.exe "{}"'.format(updateScript))

def checkUpdate(window):
    '''
    更新主程序
    :param window:主窗口
    :return:void
    '''
    global mainWindow
    mainWindow = window
    changeState([1,0,0,0,0,0],None)
    # 获取Github镜像银接
    if getGithubURL() == 1:
        return
    # 检测新版本
    info = None
    try:
        info = eval(requests.get("https://{}/alexliu07/CountBoard/raw/main/version.json".format(githubURL),verify=False).text)
    except Exception:
        error(f'{traceback.format_exc()}\n{info}')
        return
    # 获取最新版本号
    latest_version = info['version']
    if latest_version == mainWindow.version:
        # 最新版
        mainWindow.logger.info('当前已是最新版本')
        changeState([0,1,0,0,0,0],None)
        return
    else:
        changeState([0,0,0,1,1,0],[latest_version,info['content'],'0'])
        # 下载最新版本
        downloadURL = info['link']
        target_md5 = info['md5']
        file_path = mainWindow.work_dir + '\\Update.exe'
        mark_path = mainWindow.work_dir + '\\.UpdateDownloaded'
        mainWindow.logger.info('目标MD5：'+str(target_md5))
        # 验证本地是否存在文件以及是否匹配
        if os.path.exists(file_path) and os.path.exists(mark_path) and md5sum(file_path) == target_md5:
            with open(mark_path,'r',encoding='utf-8') as f:
                if f.read() == latest_version:
                    mainWindow.logger.info('执行更新')
                    # 执行更新
                    update()
                    mainWindow.exit_()
                    return
        if download(downloadURL,file_path):
            return
        # 验证文件
        file_md5 = md5sum(file_path)
        mainWindow.logger.info('文件MD5：'+str(file_md5))
        if file_md5 != target_md5:
            error('文件MD5不匹配')
            return
        with open(mainWindow.work_dir + '\\.UpdateDownloaded','w+',encoding='utf-8') as f:
            f.write(latest_version)
        changeState([0,0,0,1,0,1],[latest_version,info['content']])