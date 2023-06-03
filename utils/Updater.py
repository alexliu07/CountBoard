import time

import requests
import tkinter as tk
#错误时的处理
githubURL = ''
mainWindow = None
def error(e):
    '''
    错误时的信息处理
    :param e: 错误信息
    :return: void
    '''
    changeState([0,0,1,0],e)
def getGithubURL():
    '''
    获取Github镜像链接
    :return: status
    '''
    global githubURL
    try:
        ips = eval(requests.get('https://raw.hellogithub.com/hosts.json').text)
        for i in ips:
            if i[1] == 'github.com':
                githubURL = i[0]
        return 0
    except Exception as e:
        error(e)
        return 1

def changeState(mode,msg):
    '''
    更换窗口状态
    :param mode: 模式[正在检测更新,最新版本,更新错误,检测到更新]
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
        mainWindow.update_error.pack(side=tk.TOP, fill=tk.X)
        mainWindow.error_text['text'] = mainWindow.error_msg.format(msg)
    else:
        mainWindow.update_error.pack_forget()
    if mode[3]:
        mainWindow.need_update.pack(side=tk.TOP, fill=tk.X)
        mainWindow.update_text['text'] = mainWindow.update_msg.format(msg[0],msg[1])
        mainWindow.update_process['text'] = msg[2]
    else:
        mainWindow.need_update.pack_forget()
def checkUpdate(window):
    '''
    更新主程序
    :param window:主窗口
    :return:void
    '''
    global mainWindow
    mainWindow = window
    changeState([1,0,0,0],None)
    #获取Github镜像银接
    if getGithubURL() == 1:
        return
    # changeState([0,1,0,0],None)
    # changeState([0,0,0,1],['123','aaa'])
    # 检测新版本
    try:
        info = requests.get('https://api.github.com/repos/alexliu07/CountBoard/releases').text
        info = info.replace('false','False').replace('true','True').replace('null','None')
        info = eval(info)
        latest_version_detail = info[0]
    except Exception as e:
        error(e)
        return
    #获取最新版本号
    latest_version = latest_version_detail['tag_name']
    if latest_version == mainWindow.version:
        changeState([0,1,0,0],None)
        return
    else:
        changeState([0,0,0,1],[latest_version,latest_version_detail['body'],'正在下载更新...'])


# #隐藏窗口
# win = tkinter.Tk()
# win.withdraw()
# #寻找是否有本地更新包
# if os.path.exists('updater/offline/app-update.zip'):
#     asks = messagebox.askyesnocancel('Days Count Down离线更新','检测到Days Count Down的离线更新包，是否进行更新\n建议从官方Github下载更新包，对第三方更新包引起的程序出错概不负责\n单击“是”以进行更新，单击“否”以在线搜索更新，单击“取消”以取消更新')
#     if asks == True:
#         os.system('taskkill /t /f /im dayscountdown.exe')
#         #删除源文件
#         os.system('rmdir /s /q resources\\app')
#         #解压更新文件
#         os.system('updater\\7zip\\7za.exe x -o"resources" updater/offline/app-update.zip')
#         #记录最新版本
#         filej = open('resources/app/package.json','r',encoding='utf-8')
#         latest_detail = eval(filej.read())
#         latest_version = float(latest_detail['version'][:3])
#         filen = open('version.ini','w+',encoding='utf-8')
#         filen.write(str(latest_version))
#         filen.close()
#         #启动程序
#         os.system('start dayscountdown.exe')
#         sys.exit()
#     elif asks == None:
#         sys.exit()
# #获取github ip
#
# #获取最新版本信息
# try:
#     info = requests.get('https://api.github.com/repos/alexliu07/DaysCountDown/releases').text
#     info = info.replace('false','False').replace('true','True').replace('null','None')
#     info = eval(info)
#     latest_version_detail = info[0]
# except Exception as e:
#     error(e)
# #获取最新版本号
# latest_version = float(latest_version_detail['tag_name'])
# #获取当前版本号
# file = open('version.ini','r',encoding='utf-8')
# current_version = float(file.read())
# file.close()
# #检测更新
# if current_version < latest_version:
#     #查找更新包大小
#     for i in latest_version_detail['assets']:
#         if i['name'] == 'app-update.zip':
#             update_size = i['size']
#     #询问是否更新
#     asks = messagebox.askokcancel('Days Count Down更新','检测到Days Count Down有更新，是否进行更新？\n新版本：{}    当前版本：{}\n更新内容：\n{}'.format(latest_version,current_version,latest_version_detail['body']))
#     if asks:
#         #检测文件夹是否存在
#         if not os.path.exists('updater/tmp'):
#             os.mkdir('updater/tmp')
#         #下载更新
#         if not os.path.exists('updater/tmp/tmp.zip'):
#             print('正在下载更新...')
#             try:
#                 filed = requests.get('https://'+githuburl+'/alexliu07/DaysCountDown/releases/download/'+str(latest_version)+'/app-update.zip',verify=False)
#                 filetmp = open('updater/tmp/tmp.zip','wb')
#                 filetmp.write(filed.content)
#                 filetmp.close()
#             except Exception as e:
#                 error(e)
#         print('更新下载完毕')
#         #检测文件是否匹配
#         file_size = os.path.getsize('updater/tmp/tmp.zip')
#         if file_size == update_size:
#             os.system('taskkill /t /f /im dayscountdown.exe')
#             #删除源文件
#             os.system('rmdir /s /q resources\\app')
#             #解压更新文件
#             os.system('updater\\7zip\\7za.exe x -o"resources" updater/tmp/tmp.zip')
#             #记录最新版本
#             filen = open('version.ini','w+',encoding='utf-8')
#             filen.write(str(latest_version))
#             filen.close()
#             #删除临时下载文件
#             os.remove('updater/tmp/tmp.zip')
#             #启动程序
#             os.system('start dayscountdown.exe')
#         else:
#             error('File size not match. Maybe download error.')
# else:
#     messagebox.showinfo('未检测到更新','Days Count Down为最新版本！')