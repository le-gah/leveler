import tkinter as tk
from tkinter import ttk, simpledialog
import pygame
import os
import glob
import json
import sys

# frozen 속성이 있으면 PyInstaller로 묶인 상태
if getattr(sys, "frozen", False):
    base_path = os.getcwd()
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# --- 설정 및 초기화 ---
songs = glob.glob(os.path.join(base_path, "*.mp3"))
if not songs:
    raise FileNotFoundError("현재 폴더에 .mp3 파일이 없습니다.")
current_song_index = 0
paused = False
pygame.mixer.init()

# 저장 파일들
task_file = os.path.join(base_path, "tasks.json")
xp_file   = os.path.join(base_path, "xp_data.json")
name_file = os.path.join(base_path, "name.txt")

# --- 데이터 로드/저장 함수 ---
def load_tasks():
    if os.path.exists(task_file):
        with open(task_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def load_xp():
    if os.path.exists(xp_file):
        with open(xp_file, "r", encoding="utf-8") as f:
            d = json.load(f)
            return d.get("xp", 0), d.get("level", 1)
    return 0, 1

def save_xp(xp, level):
    with open(xp_file, "w", encoding="utf-8") as f:
        json.dump({"xp": xp, "level": level}, f, indent=4, ensure_ascii=False)

def load_name():
    if os.path.exists(name_file):
        with open(name_file, "r", encoding="utf-8") as f:
            n = f.read().strip()
            return n if n else "레가"
    return "레가"

def save_name(n):
    with open(name_file, "w", encoding="utf-8") as f:
        f.write(n)

# --- XP / 레벨 관리 ---
xp, level = load_xp()
user_name = load_name()

def add_xp(amount):
    global xp, level
    xp += amount
    while xp >= 60:
        xp -= 60
        level += 1
    xp_var.set(xp)
    xp_bar.config(value=xp)
    level_label.config(text=f"{user_name} Lv.{level}")
    save_xp(xp, level)

def xp_tick():
    if pygame.mixer.music.get_busy() and not paused:
        add_xp(1)
    root.after(60000, xp_tick)

# --- 음악 종료 감지 함수 ---
def on_song_end():
    global paused
    play_button.config(text="재생")
    song_label.config(text="대기 중")
    paused = False

def check_song_end():
    if play_button.cget("text") == "일시 정지" and not pygame.mixer.music.get_busy():
        on_song_end()
    root.after(1000, check_song_end)

# --- 이름 변경 ---
def rename():
    global user_name
    new = simpledialog.askstring("이름 변경", "새 이름을 입력하세요:", initialvalue=user_name)
    if new:
        user_name = new
        level_label.config(text=f"{user_name} Lv.{level}")
        save_name(user_name)

# --- 음악 재생 함수들 ---
def play_music():
    global paused
    pygame.mixer.music.load(songs[current_song_index])
    pygame.mixer.music.play()
    paused = False
    song_label.config(text=f"재생 중: {os.path.basename(songs[current_song_index])}")

def toggle_play():
    global paused
    if not pygame.mixer.music.get_busy():
        play_music(); play_button.config(text="일시 정지")
    elif paused:
        pygame.mixer.music.unpause(); paused=False; play_button.config(text="일시 정지")
    else:
        pygame.mixer.music.pause(); paused=True; play_button.config(text="재생")

def next_song():
    global current_song_index
    current_song_index = (current_song_index + 1) % len(songs)
    play_music(); play_button.config(text="일시 정지")

def set_volume(val):
    pygame.mixer.music.set_volume(float(val)/100)

# --- 투두리스트 함수들 ---
tasks = load_tasks()
def update_task_list():
    listbox_tasks.delete(0, tk.END)
    for t in tasks:
        listbox_tasks.insert(tk.END, t)

def add_task():
    txt = entry_task.get().strip()
    if txt:
        tasks.append(txt); save_tasks(tasks)
        update_task_list(); entry_task.delete(0, tk.END)

def delete_selected():
    sel = listbox_tasks.curselection()
    if sel:
        tasks.pop(sel[0]); save_tasks(tasks)
        update_task_list(); add_xp(10)

# --- GUI 구성 ---
root = tk.Tk()
root.title("플레이어")
root.geometry("350x430")
root.configure(bg="#dadf7c")

# 전역 스타일
root.option_add("*Label.foreground", "#7f5232")
root.option_add("*Listbox.foreground", "#7f5232")
root.option_add("*Entry.foreground",   "#7f5232")
root.option_add("*Scale.foreground",   "#7f5232")
root.option_add("*Button.relief",      "flat")
root.option_add("*Button.bd",          0)
root.option_add("*Button.height",      1)
root.option_add("*Button.background",  "#bac432")
root.option_add("*Button.foreground",  "#7f5232")
root.option_add("*Button.activeBackground", "#edde2a")
root.option_add("*Button.activeForeground", "#7f5232")
root.option_add("*Frame.background",   "#dadf7c")
root.option_add("*Label.background",   "#dadf7c")
root.option_add("*Listbox.background", "#ffffff")
root.option_add("*Entry.background",   "#ffffff")

style = ttk.Style()
style.theme_use("clam")
style.configure("Horizontal.TProgressbar",
                troughcolor="#ffffff",
                background="#edde2a",
                thickness=4)

# --- 프로필 영역 ---
pf = tk.Frame(root); pf.pack(pady=(24,7))
level_label = tk.Label(pf, text=f"{user_name} Lv.{level}", font=("Arial",12,"bold"))
level_label.pack(side=tk.LEFT)
rename_btn = tk.Button(pf, text="변경", width=4, height=1, font=("Arial",8), command=rename)
rename_btn.pack(side=tk.LEFT, padx=5)

# XP 섹션 분리
xp_section = tk.Frame(root, bg="#dadf7c")
xp_section.pack(pady=(5,10))
tk.Label(xp_section, text="EXP", bg="#dadf7c", font=("Arial",9)).pack(side=tk.LEFT)
xp_var = tk.DoubleVar(value=xp)
xp_bar = ttk.Progressbar(xp_section, variable=xp_var, maximum=60, length=180, style="Horizontal.TProgressbar")
xp_bar.pack(side=tk.LEFT, padx=(5,0))

# --- 음악 플레이어 영역 ---
pl = tk.Frame(root); pl.pack(pady=10)
song_label = tk.Label(pl, text="대기 중", font=("Arial",10)); song_label.pack()
ctrl = tk.Frame(pl); ctrl.pack(pady=5)
play_button = tk.Button(ctrl, text="재생", width=10, command=toggle_play)
play_button.grid(row=0, column=0, padx=5)
next_button = tk.Button(ctrl, text="다음", width=10, command=next_song)
next_button.grid(row=0, column=1, padx=5)
volume_slider = tk.Scale(pl, from_=0, to=100, orient="horizontal", length=254, command=set_volume,
    showvalue=False, troughcolor="#ffffff", background="#bac432", relief="flat",
    sliderrelief="flat", bd=0, highlightthickness=0, highlightbackground="#edde2a",
    highlightcolor="#edde2a", activebackground="#edde2a")
volume_slider.set(50); volume_slider.pack(pady=5)

# --- 투두리스트 영역 ---
task_section = tk.Frame(root)
task_section.pack(pady=20, fill="x")

tk.Label(task_section, text="To-do", font=("Arial",11,"bold")).pack(pady=(0,5))

input_frame = tk.Frame(task_section); input_frame.pack(pady=(0,5))
entry_task = tk.Entry(input_frame, width=28); entry_task.pack(side=tk.LEFT, ipady=2)
button_add = tk.Button(input_frame, text="작성", width=5, command=add_task)
button_add.pack(side=tk.LEFT, padx=(5,0))

listbox_tasks = tk.Listbox(task_section, height=5, width=36)
listbox_tasks.pack(pady=(0,5))
update_task_list()

button_frame = tk.Frame(task_section); button_frame.pack(pady=(5,0))
button_done   = tk.Button(button_frame, text="완료", width=10, command=delete_selected)
button_delete = tk.Button(button_frame, text="삭제", width=10, command=delete_selected)
button_done.grid(row=0, column=0, padx=10)
button_delete.grid(row=0, column=1, padx=10)

# 종료 감지 및 XP 스케줄
root.after(1000, check_song_end)
root.after(60000, xp_tick)

root.mainloop()
