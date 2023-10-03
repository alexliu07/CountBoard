import os
import subprocess
import traceback

import requests
import tkinter as tk

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
def getGithubURL():
    '''
    获取Github镜像链接
    :return: status
    '''
    global githubURL
    ips = None
    try:
        ips = eval(requests.get('https://raw.hellogithub.com/hosts.json').text)
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
        if total_size != target_size:
            error('文件大小不匹配')
            return 1
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
        mainWindow.error_text['text'] = mainWindow.error_msg.format(msg)
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
    updateScript = '{}\\Update.vbs'.format(mainWindow.work_dir)
    updateContent = 'Set ws = createobject("wscript.shell")\n{0}\nws.run "powershell.exe Set-ExecutionPolicy RemoteSigned",0,True\nws.run "powershell.exe {1}",0,True\nws.run "taskkill /t /f /im CountBoard.exe",0,True\nSet file = CreateObject("Scripting.FileSystemObject")\nfile.DeleteFile("{2}")\nfile.CopyFile "{3}","{2}",True\nws.run "{2}",0\nfile.DeleteFile("{3}")\nfile.DeleteFile("{4}")\nfile.DeleteFile("{1}")\nfile.DeleteFile("{5}")'.format(mainWindow.elevate_script,toastScript,mainWindow.exe_dir_path + '\\CountBoard.exe',mainWindow.work_dir + '\\Update.exe',mainWindow.work_dir + '\\.UpdateDownloaded',updateScript)
    with open(updateScript,'w+',encoding='utf-8') as f:
        f.write(updateContent)
    subprocess.Popen('wscript.exe "{}"'.format(updateScript))

def checkUpdate(window):
    '''
    更新主程序
    :param window:主窗口
    :return:void
    '''
    global mainWindow,target_size
    mainWindow = window
    changeState([1,0,0,0,0,0],None)
    # 获取Github镜像银接
    if getGithubURL() == 1:
        return
    # 检测新版本
    info = None
    try:
        info = requests.get('https://api.github.com/repos/alexliu07/CountBoard/releases').text
        info = info.replace('false','False').replace('true','True').replace('null','None')
        info = eval(info)
        latest_version_detail = info[0]
    except Exception:
        error(f'{traceback.format_exc()}\n{info}')
        return
    # 获取最新版本号
    latest_version = latest_version_detail['tag_name']
    if latest_version == mainWindow.version:
        # 最新版
        mainWindow.logger.info('当前已是最新版本')
        changeState([0,1,0,0,0,0],None)
        return
    else:
        changeState([0,0,0,1,1,0],[latest_version,latest_version_detail['body'],'0'])
        # 下载最新版本
        downloadURL = latest_version_detail['assets'][0]['browser_download_url'].replace('www.github.com',githubURL).replace('github.com',githubURL)
        target_size = latest_version_detail['assets'][0]['size']
        file_path = mainWindow.work_dir + '\\Update.exe'
        mark_path = mainWindow.work_dir + '\\.UpdateDownloaded'
        mainWindow.logger.info('目标大小：'+str(target_size))
        # 验证本地是否存在文件
        if os.path.exists(file_path) and os.path.exists(mark_path) and os.path.getsize(file_path) == target_size:
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
        file_size = os.path.getsize(file_path)
        mainWindow.logger.info('文件大小：'+str(file_size))
        if file_size != target_size:
            error('文件大小不匹配')
            return
        with open(mainWindow.work_dir + '\\.UpdateDownloaded','w+',encoding='utf-8') as f:
            f.write(latest_version)
        changeState([0,0,0,1,0,1],[latest_version,latest_version_detail['body']])