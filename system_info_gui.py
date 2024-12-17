import tkinter as tk
from tkinter import ttk, messagebox
import socket
import psutil
import platform
import subprocess

# Функция для получения информации о сетевых интерфейсах и IP

def get_network_info():
    network_info = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for iface, addr_list in addrs.items():
        iface_info = {
            "Interface": iface,
            "Status": "Up" if stats[iface].isup else "Down",
            "IPv4": "N/A",
            "Netmask": "N/A",
            "CIDR": "N/A",
            "MAC": "N/A"
        }
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                iface_info["IPv4"] = addr.address
                iface_info["Netmask"] = addr.netmask
                iface_info["CIDR"] = sum(bin(int(x)).count('1') for x in addr.netmask.split('.'))
            elif addr.family == psutil.AF_LINK:
                iface_info["MAC"] = addr.address
        network_info.append(iface_info)
    return network_info

# Функция для получения списка дисков
def get_disk_info():
    disk_info = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                "Drive": partition.device,
                "Total": f"{round(usage.total / (1024 ** 3), 2)} GB",
                "Used": f"{round(usage.used / (1024 ** 3), 2)} GB",
                "Free": f"{round(usage.free / (1024 ** 3), 2)} GB"
            })
        except PermissionError:
            continue
    return disk_info

# Получение базовой информации
def get_system_info():
    video_card = subprocess.getoutput("wmic path win32_videocontroller get caption")
    info = {
        "Hostname": socket.gethostname(),
        "OS Version": platform.platform(),
        "CPU": platform.processor(),
        "RAM": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "Video Card": video_card.strip().split("\n")[-1]  # Последняя строка с видеокартой
    }
    return info

# Функция для копирования в буфер обмена
def copy_to_clipboard(event):
    text = event.widget.cget("text")
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    messagebox.showinfo("Copied", f"'{text}' copied to clipboard")

def fetch_data():
    try:
        sys_info = get_system_info()
        net_info = get_network_info()
        disk_info = get_disk_info()
        update_output(sys_info, net_info, disk_info)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при получении данных: {str(e)}")

# Функция для обновления интерфейса
def update_output(sys_info, net_info, disk_info):
    for widget in info_frame.winfo_children():
        widget.destroy()

    row = 0
    # Основная системная информация
    header = tk.Label(info_frame, text="System Information", font=('Arial', 12, 'bold'), bg='#950740', fg='#C3073F', anchor='w')
    header.grid(row=row, column=0, columnspan=6, sticky='we', pady=5)
    row += 1

    for key, value in sys_info.items():
        label_key = tk.Label(info_frame, text=key, font=('Arial', 10, 'bold'), bg='#6F2232', fg='#C3073F', anchor='w')
        label_key.grid(row=row, column=0, sticky='w', padx=5, pady=2)
        label_value = tk.Label(info_frame, text=value, font=('Arial', 10), bg='#4E4E50', fg='#FFFFFF', anchor='w')
        label_value.grid(row=row, column=1, sticky='w', padx=5, pady=2)
        label_value.bind("<Button-1>", copy_to_clipboard)
        row += 1

    # Диски
    header_disk = tk.Label(info_frame, text="Drives Information", font=('Arial', 12, 'bold'), bg='#950740', fg='#C3073F', anchor='w')
    header_disk.grid(row=row, column=0, columnspan=6, sticky='we', pady=5)
    row += 1

    disk_headers = ["Drive", "Total", "Used", "Free"]
    for col, header in enumerate(disk_headers):
        tk.Label(info_frame, text=header, font=('Arial', 10, 'bold'), bg='#6F2232', fg='#C3073F', anchor='center').grid(row=row, column=col, sticky='we', padx=1)
    row += 1

    for disk in disk_info:
        for col, key in enumerate(["Drive", "Total", "Used", "Free"]):
            cell = tk.Label(info_frame, text=disk[key], font=('Arial', 10), bg='#4E4E50', fg='#FFFFFF', anchor='center')
            cell.grid(row=row, column=col, sticky='we', padx=1)
            cell.bind("<Button-1>", copy_to_clipboard)
        row += 1

    # Сетевые интерфейсы
    header_net = tk.Label(info_frame, text="Network Interfaces", font=('Arial', 12, 'bold'), bg='#950740', fg='#C3073F', anchor='w')
    header_net.grid(row=row, column=0, columnspan=6, sticky='we', pady=5)
    row += 1

    net_headers = ["Interface", "Status", "IPv4", "Netmask", "CIDR", "MAC"]
    for col, header in enumerate(net_headers):
        tk.Label(info_frame, text=header, font=('Arial', 10, 'bold'), bg='#6F2232', fg='#C3073F', anchor='center').grid(row=row, column=col, sticky='we', padx=1)
    row += 1

    for iface in net_info:
        for col, key in enumerate(["Interface", "Status", "IPv4", "Netmask", "CIDR", "MAC"]):
            cell = tk.Label(info_frame, text=iface[key], font=('Arial', 10), bg='#4E4E50', fg='#FFFFFF', anchor='center')
            cell.grid(row=row, column=col, sticky='we', padx=1)
            cell.bind("<Button-1>", copy_to_clipboard)
        row += 1

# Создание основного окна
root = tk.Tk()
root.title("System Info")
root.geometry("1000x700")
root.resizable(False, False)
root.configure(bg='#1A1A1D')

# Заголовок
title = tk.Label(root, text="System Information Viewer", font=("Arial", 14, "bold"), bg='#1A1A1D', fg='#C3073F')
title.pack(pady=5)

# Фрейм для информации
info_frame = tk.Frame(root, bg='#1A1A1D', bd=2, relief=tk.GROOVE)
info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Кнопка для обновления данных
btn_refresh = ttk.Button(root, text="Refresh Data", command=fetch_data)
btn_refresh.pack(pady=5)

# Подпись разработчика
footer = tk.Label(root, text="Developer: https://github.com/julfys", font=("Arial", 10), bg='#1A1A1D', fg='#C3073F', cursor="hand2")
footer.pack(side=tk.BOTTOM, pady=5)
footer.bind("<Button-1>", lambda e: root.clipboard_append("https://github.com/julfys"))

# Запуск программы
fetch_data()  # Получить данные при старте программы
root.mainloop()
