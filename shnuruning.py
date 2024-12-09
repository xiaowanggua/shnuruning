import tkinter as tk
import subprocess
import os
from pathlib import Path
from tkinter import messagebox
from tkinter import messagebox
from mitmproxy import http
import json
from mitmproxy.tools.main import mitmdump
import threading
import time
from multiprocessing import Process
import requests

url2 = "https://cpapp.1lesson.cn/api/route/selectStudentSignIn"
url1 = 'https://cpapp.1lesson.cn/api/route/insertStartRunning'
url3 = 'https://cpapp.1lesson.cn/api/route/insertFinishRunning'
recordId = ''
userids = ''
run_distance = 0
run_times = 0

def post(url,data,headers=None):
    response = requests.post(url, data=data, headers=headers)
    print(response.json())
    return response.json()

def runs(point):
    points = {
        "userId": userids,
        "recordId": recordId,
        "posLongitude": 0,
        "posLatitude": 0,
    }
    headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    if point == 0:
        points["posLongitude"] = 121.51818147705078
        points["posLatitude"] = 30.837721567871094
    elif point == 1:
        points["posLongitude"] = 121.52092847705076
        points["posLatitude"] = 30.834883567871294
    elif point == 2:
        points["posLongitude"] = 121.51926147705322
        points["posLatitude"] = 30.835872567871354
    elif point == 3:
        points["posLongitude"] = 121.51749847705033
        points["posLatitude"] = 30.835306567871091
    print(points)
    post(url2,points,headers=headers)

def install():
    ca_cert_path = Path(os.path.expanduser("~/.mitmproxy/mitmproxy-ca.p12"))
    print(ca_cert_path)

    # Check if the certificate exists
    if not ca_cert_path.exists():
        messagebox.showerror("安装证书", "无法找到mitmproxy CA证书，开始生成证书，约等待5s。")
        
        # Generate a new certificate using mitmdump in a separate thread
        def generate_certificate():
            subprocess.run(["mitmdump"], check=True)


        thread = threading.Thread(target=generate_certificate)
        thread.start()
        time.sleep(3)
        subprocess.run(["taskkill", "/F", "/IM", "mitmdump.exe"], check=True)


        # Check again if the certificate exists
        if not ca_cert_path.exists():
            messagebox.showerror("安装证书", "证书生成失败，无法找到mitmproxy CA证书")
            return

    # Install the certificate
    try:
        subprocess.run([
            "powershell", 
            "-Command", 
            f'Import-PfxCertificate -FilePath "{ca_cert_path}" -CertStoreLocation "Cert:\\CurrentUser\\Root"'
        ], check=True)
        messagebox.showinfo("安装证书", "证书安装成功")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("安装证书", f"证书安装失败: {e}")

  
def show_user_id_screen():
    main_frame.pack_forget()
    user_id_frame.pack()

def show_main_screen():
    user_id_frame.pack_forget()
    main_frame.pack()

def install_certificate():
    install()

def start_mitmproxy():
    mitmdump(['-s', "./Addon.py"])


def run() -> Process:
    """运行多进程"""
    p = Process(target=start_mitmproxy, name='mitmproxy')
    p.start()
    return p


def stop(p: Process) -> None:
    """终止多进程"""
    p.terminate()
    p.join()


def start_getting_user_id():
    messagebox.showinfo("获取用户ID", "开始获取用户ID,请在点击确定后,20s内打开电脑微信体锻打卡小程序,如获取成功将在文件目录下自动生成userId.txt文件,获取成功后需要去系统代理选项手动取消一下代理。")
    
    # Set system proxy
    os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f')
    os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d 127.0.0.1:8080 /f')
    p = run()
    time.sleep(20)
    stop(p)




if __name__ == '__main__':

    root = tk.Tk()
    root.title("跑步应用")

    # 主界面
    main_frame = tk.Frame(root)
    main_frame.pack()


    def show_run_screen():
        main_frame.pack_forget()
        run_frame.pack()


    def start_countdown():
        
        try:
            global run_distance
            global run_times
            run_time = int(run_time_entry.get()) * 60
            run_times = run_time
            run_distance = int(run_distance_entry.get())
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数")
            return
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = post(url1, {'userId': userids},headers=headers)
        global recordId
        recordId = r["data"]["runningRecord"]
        time.sleep(1)
        runs(0)
        time.sleep(1)
        runs(1)
        time.sleep(1)
        runs(2)
        countdown_label.config(text=f"{run_time} 秒")
        countdown(run_time)

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"{time_left} 秒")
            root.after(1000, countdown, time_left - 1)
        else:
            finish()

    def finish():
        runs(3)
        data = f'{{"userId":"{userids}","runningRecordId":"{recordId}","mileage":{run_distance},"speedAllocation":0,"totalTime":{int(run_times/60)},"data":[]}}'        
        print(data)
        r = post(data=data,url=url3,headers={'Content-Type': 'application/json'})
        countdown_label.config(text=f"跑步结束,请打开小程序检查是否次数增加。")


    def check_user_id_and_show_run_screen():
        if os.path.exists("userId.txt") and os.path.getsize("userId.txt") > 0:
            try:
                global userids
                with open("userId.txt", 'r', encoding='utf-8') as file:
                    userids = file.read()  # 读取文件内容并存储为字符串
                    print(userids)  # 输出文件内容（可选）
                    show_run_screen()
                    messagebox.showinfo("注意！", "注意请每天第一次跑步前打开小程序手动点一下开始跑步，然后直接点结束跑步，然后再用本程序跑步。请填写合理的时间和距离，以及点击开始后和倒计时为1s会卡住一段时间属于正常情况。如果使用到一半程序关闭，请打开跑步小程序手动点击结束再使用本程序。")
            except FileNotFoundError:
                print(f"文件 {"userId.txt"} 未找到。")
            except IOError:
                print(f"读取文件 {"userId.txt"} 时出错。")

        else:
            messagebox.showwarning("获取用户ID", "请先获取用户ID")
            
    run_button = tk.Button(main_frame, text="跑步", command=check_user_id_and_show_run_screen)
    run_button.pack(pady=20)

    get_user_id_button = tk.Button(main_frame, text="获取用户ID", command=show_user_id_screen)
    get_user_id_button.pack(anchor='ne', padx=10, pady=10)

    # 界面2
    user_id_frame = tk.Frame(root)

    install_certificate_button = tk.Button(user_id_frame, text="安装证书", command=install_certificate)
    install_certificate_button.pack(pady=10)

    start_getting_user_id_button = tk.Button(user_id_frame, text="开始获取用户ID", command=start_getting_user_id)
    start_getting_user_id_button.pack(pady=10)

    back_button = tk.Button(user_id_frame, text="返回", command=show_main_screen)
    back_button.pack(pady=10)


    # 新界面
    run_frame = tk.Frame(root)

    run_time_label = tk.Label(run_frame, text="跑步时间(分钟):")
    run_time_label.pack(pady=5)
    run_time_entry = tk.Entry(run_frame)
    run_time_entry.pack(pady=5)

    run_distance_label = tk.Label(run_frame, text="跑步距离(公里):")
    run_distance_label.pack(pady=5)
    run_distance_entry = tk.Entry(run_frame)
    run_distance_entry.pack(pady=5)

    confirm_button = tk.Button(run_frame, text="确定", command=start_countdown)
    confirm_button.pack(pady=10)

    countdown_label = tk.Label(run_frame, text="")
    countdown_label.pack(pady=10)

    back_button_run = tk.Button(run_frame, text="返回", command=show_main_screen)
    back_button_run.pack(pady=10)
    root.mainloop()

