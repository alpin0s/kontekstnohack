#!/usr/bin/env python3
"""
KontekstnoHack GUI
Тёмная тема, принимает Room ID или Challenge ID, автоматически получает Challenge ID и отображает слова и ранги по мере поступления.
Dependencies: requests, tkinter (standard lib)
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import random

# ------------------------
# Core Logic
# ------------------------
API_BASE = 'https://xn--80aqu.xn--e1ajbkccewgd.xn--p1ai'

def generate_user_id() -> str:
    suffix = random.randint(10**11, 10**12 - 1)
    return f'daab6d58-c8a5-498b-9045-{suffix}'

def api_get(endpoint: str, **params) -> dict:
    url = f"{API_BASE}/{endpoint}"
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def get_challenge_id_from_room(room_id: str) -> str:
    data = api_get('get_room', room_id=room_id)
    cid = data.get('challenge_id')
    if not cid:
        raise ValueError('Room ID не найден')
    return cid

# ------------------------
# Fetch Generator
# ------------------------
def iter_tips(challenge_id: str):
    """
    Generator: инициализирует challenge и выдаёт по одному (word, rank).
    """
    user_id = generate_user_id()
    # Инициализация с "человек"
    api_get('get_score', challenge_id=challenge_id, user_id=user_id,
            word='человек', challenge_type='random')
    while True:
        tip = api_get('get_tip', challenge_id=challenge_id,
                      user_id=user_id, challenge_type='random')
        word = tip.get('word', '')
        rank = tip.get('rank', -1)
        yield word, rank
        if rank in (1, -1):
            break

# ------------------------
# Theme & Styles
# ------------------------
BG = '#1E1E1E'; PANEL = '#2D2D2D'; TXT = '#FFFFFF'; ACC = '#FFCC00'; BTN_TXT = '#000000'
HEADER_FONT = ('Segoe UI Semibold', 18)
BODY_FONT   = ('Segoe UI', 12)
BADGE_FONT  = ('Segoe UI Semibold', 10)
BUTTON_FONT = ('Segoe UI', 12, 'bold')

root = tk.Tk()
root.title('KontekstnoHack')
root.configure(bg=BG)
root.geometry('520x420')
root.minsize(400, 300)

style = ttk.Style(root)
style.theme_use('alt')
style.configure('TFrame', background=BG)
style.configure('Header.TLabel', font=HEADER_FONT, background=BG, foreground=TXT)
style.configure('TLabel', font=BODY_FONT, background=BG, foreground=TXT)
style.configure('TEntry', font=BODY_FONT, fieldbackground=PANEL, background=PANEL, foreground=TXT, insertcolor=TXT)
style.configure('Accent.TButton', font=BUTTON_FONT, background=ACC, foreground=BTN_TXT, relief='flat', padding=6)
style.map('Accent.TButton', background=[('active', ACC)], foreground=[('disabled', TXT)])
style.configure('TProgressbar', troughcolor=PANEL, background=ACC, bordercolor=PANEL)

# ------------------------
# Layout
# ------------------------
frm = ttk.Frame(root, padding=20, style='TFrame')
frm.pack(fill='both', expand=True)
frm.columnconfigure(1, weight=1)
frm.rowconfigure(3, weight=1)

# Header
ttk.Label(frm, text='KontekstnoHack', style='Header.TLabel').grid(row=0, column=0, columnspan=3, pady=(0, 20))

# ID Input
ttk.Label(frm, text='Room/Challenge ID:').grid(row=1, column=0, sticky='w')
ent = ttk.Entry(frm, style='TEntry')
ent.grid(row=1, column=1, columnspan=2, sticky='ew', padx=(10, 0))
# Paste handler
ent.bind('<Control-KeyPress>', lambda e: (ent.event_generate('<<Paste>>') if e.char.lower() in ('v','м') else None) and 'break')

# Hack Button
hack_btn = ttk.Button(frm, text='Hack', style='Accent.TButton', command=lambda: run_fetch())
hack_btn.grid(row=2, column=2, sticky='e', pady=(10, 0))

# Progress Bar
progress = ttk.Progressbar(frm, mode='indeterminate')
progress.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0), padx=(0, 10))

# Results Canvas
results_frame = ttk.Frame(frm, style='TFrame')
results_frame.grid(row=3, column=0, columnspan=3, sticky='nsew', pady=(20, 0))
canvas = tk.Canvas(results_frame, bg=PANEL, highlightthickness=0)
canvas.pack(fill='both', expand=True)
inner = ttk.Frame(canvas, style='TFrame')
canvas.create_window((0, 0), window=inner, anchor='nw')
inner.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units'))

# ------------------------
# UI Functions
# ------------------------
# Track row index
inner.row_index = 0

def clear_results():
    for w in inner.winfo_children(): w.destroy()
    inner.row_index = 0


def append_result(word: str, rank: int):
    row = inner.row_index
    ttk.Label(inner, text=word, style='TLabel').grid(row=row, column=0, sticky='w', pady=2, padx=(0, 10))
    tk.Label(inner, text=str(rank), font=BADGE_FONT, bg=ACC, fg=BTN_TXT, padx=6, pady=2).grid(row=row, column=1, sticky='e')
    inner.row_index += 1


def display_error(msg: str):
    clear_results()
    ttk.Label(inner, text=msg, style='TLabel').grid(row=0, column=0, pady=5)


def run_fetch():
    ident = ent.get().strip()
    # Determine challenge_id
    try:
        cid = get_challenge_id_from_room(ident)
    except Exception:
        cid = ident
    clear_results()
    hack_btn.config(state='disabled'); ent.config(state='disabled'); progress.start(10)

    def task():
        try:
            for word, rank in iter_tips(cid):
                root.after(0, lambda w=word, r=rank: append_result(w, r))
        except Exception:
            root.after(0, lambda: display_error('Неверный Room/Challenge ID'))
        finally:
            root.after(0, lambda: [progress.stop(), hack_btn.config(state='normal'), ent.config(state='normal')])

    threading.Thread(target=task, daemon=True).start()

# Start App
if __name__ == '__main__':
    ent.focus()
    root.mainloop()
