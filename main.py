
import tkinter as tk
from tkinter import ttk, messagebox
from dijkstra import dijkstra
import math

BG, PANEL = "#061426", "#0A1D33"
CYAN, GREEN, BLUE = "#40D9FF", "#19E6B4", "#168FF0"
WHITE, MUTED = "#EAF6FF", "#8DAFC8"

graph = {}
limit = 0
count = 0

root = tk.Tk()
root.title("Air Traffic Control | Dijkstra")
root.geometry("1150x720")
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", fieldbackground=PANEL,
                background=PANEL, foreground=WHITE,
                arrowcolor=CYAN)

def label(p, text, size=10, color=WHITE, bold=False):
    return tk.Label(p, text=text, bg=p.cget("bg"), fg=color,
                    font=("Segoe UI", size, "bold" if bold else "normal"))

def button(p, text, fn, color=BLUE):
    return tk.Button(p, text=text, command=fn, bg=color, fg=BG,
                     relief="flat", cursor="hand2",
                     font=("Segoe UI", 10, "bold"), pady=8)

def field(p, text):
    label(p, text, 9, MUTED).pack(anchor="w", padx=12, pady=(8, 3))
    e = tk.Entry(p, bg="#102943", fg=WHITE,
                 insertbackground=WHITE, relief="flat")
    e.pack(fill="x", padx=12, ipady=7)
    return e

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=18, pady=14)
label(header, "✈ AIR TRAFFIC CONTROL", 20, CYAN, True).pack(side="left")
label(header, "ROUTE INTELLIGENCE  /  DIJKSTRA", 10, MUTED).pack(side="right")

body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

left = tk.Frame(body, bg=PANEL, width=270)
left.pack(side="left", fill="y", padx=(0, 12))
left.pack_propagate(False)

label(left, "FLIGHT NETWORK", 14, CYAN, True).pack(pady=14)
n = field(left, "NUMBER OF AIRPORTS")
names = field(left, "AIRPORT NAMES (comma separated)")
r = field(left, "TOTAL ROUTES")

src = ttk.Combobox(left, state="readonly")
dst = ttk.Combobox(left, state="readonly")
label(left, "ROUTE SOURCE", 9, MUTED).pack(anchor="w", padx=12, pady=(14, 3))
src.pack(fill="x", padx=12)
label(left, "ROUTE DESTINATION", 9, MUTED).pack(anchor="w", padx=12, pady=(8, 3))
dst.pack(fill="x", padx=12)

km = field(left, "DISTANCE (KM)")

right = tk.Frame(body, bg=BG)
right.pack(side="left", fill="both", expand=True)

cards = tk.Frame(right, bg=BG)
cards.pack(fill="x", pady=(0, 10))

def card(title, value):
    f = tk.Frame(cards, bg=PANEL, padx=12, pady=10)
    f.pack(side="left", fill="x", expand=True, padx=(0, 8))
    label(f, title, 9, MUTED).pack(anchor="w")
    v = label(f, value, 17, CYAN, True)
    v.pack(anchor="w", pady=(5, 0))
    return v

air_stat = card("AIRPORTS", "0")
route_stat = card("ROUTES", "0")
dist_stat = card("SHORTEST KM", "--")

mapbox = tk.Frame(right, bg="#041322")
mapbox.pack(fill="both", expand=True)
label(mapbox, "◉ RADAR / AIRPORT NETWORK", 12, CYAN, True).pack(
    anchor="w", padx=12, pady=10)
canvas = tk.Canvas(mapbox, bg="#041322", highlightthickness=0)
canvas.pack(fill="both", expand=True, padx=8, pady=5)

result = label(right, "Initialize airports to begin.", 11, GREEN, True)
result.pack(anchor="w", pady=10)

def setup():
    global graph, count, limit
    try:
        total = int(n.get())
        limit = int(r.get())
        airports = [x.strip() for x in names.get().split(",") if x.strip()]
        if (total < 2 or len(airports) != total
                or len(set(airports)) != total
                or limit < 1 or limit > total*(total-1)//2):
            raise ValueError
    except ValueError:
        messagebox.showerror("Input error", "Check airport names and counts.")
        return

    graph = {a: {} for a in airports}
    count = 0
    for c in (src, dst):
        c["values"] = airports
        c.set("")
    air_stat.config(text=str(total))
    route_stat.config(text=f"0/{limit}")
    dist_stat.config(text="--")
    result.config(text="Airports initialized. Add routes.")
    draw()

def add_route():
    global count
    a, b = src.get(), dst.get()
    try:
        d = float(km.get())
        if (not graph or a not in graph or b not in graph
                or a == b or d <= 0 or count >= limit):
            raise ValueError
    except ValueError:
        messagebox.showerror("Route error", "Select valid airports and distance.")
        return
    if b in graph[a]:
        messagebox.showerror("Duplicate", "Route already exists.")
        return
    graph[a][b] = graph[b][a] = d
    count += 1
    route_stat.config(text=f"{count}/{limit}")
    result.config(text=f"Connection added: {a} ↔ {b}")
    draw()

def shortest():
    a, b = src.get(), dst.get()
    if a not in graph or b not in graph or a == b:
        messagebox.showerror("Selection", "Select two different airports.")
        return
    path, total = dijkstra(graph, a, b)
    if not path:
        result.config(text="No connected route found.")
        dist_stat.config(text="--")
        draw()
        return
    dist_stat.config(text=f"{total:g}")
    result.config(text=f"{' → '.join(path)}  |  {total:g} km")
    draw(path)

def draw(path=None):
    canvas.delete("all")
    if not graph:
        canvas.create_text(250, 150, text="INITIALIZE AIRPORTS",
                           fill=MUTED, font=("Consolas", 14))
        return

    canvas.update_idletasks()
    w, h = max(canvas.winfo_width(), 400), max(canvas.winfo_height(), 300)
    cx, cy = w/2, h/2
    radius = min(w, h)*0.37

    for i in range(1, 5):
        rr = radius*i/4
        canvas.create_oval(cx-rr, cy-rr, cx+rr, cy+rr,
                           outline="#123B58")
    airports = list(graph)
    points = {}
    for i, a in enumerate(airports):
        angle = 2*math.pi*i/len(airports)-math.pi/2
        points[a] = (cx+radius*math.cos(angle),
                     cy+radius*math.sin(angle))

    for a in graph:
        for b, d in graph[a].items():
            if airports.index(a) >= airports.index(b):
                continue
            x1, y1 = points[a]
            x2, y2 = points[b]
            active = path and a in path and b in path and abs(
                path.index(a)-path.index(b)) == 1
            canvas.create_line(x1, y1, x2, y2,
                               fill=GREEN if active else "#1766A1",
                               width=4 if active else 2)
            canvas.create_text((x1+x2)/2, (y1+y2)/2,
                               text=str(d), fill=CYAN,
                               font=("Consolas", 9))

    for a, (x, y) in points.items():
        active = path and a in path
        canvas.create_oval(x-13, y-13, x+13, y+13,
                           fill="#0B2A48",
                           outline=GREEN if active else CYAN, width=2)
        canvas.create_text(x, y+25, text=a, fill=WHITE,
                           font=("Segoe UI", 9, "bold"))

canvas.bind("<Configure>", lambda e: draw())

button(left, "INITIALIZE AIRPORTS", setup, CYAN).pack(
    fill="x", padx=12, pady=(14, 5))
button(left, "ADD ROUTE", add_route, BLUE).pack(
    fill="x", padx=12, pady=5)
button(left, "FIND SHORTEST PATH", shortest, GREEN).pack(
    fill="x", padx=12, pady=5)

root.mainloop()
