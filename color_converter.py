#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Studio — интерактивный конвертер CMYK <-> RGB <-> HLS
Вариант 6: CMYK ↔ RGB ↔ HLS
Автор: Янушкевич Максим Викторович
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import colorsys
import math
import sys

# ---------------------- Утилиты конвертаций ---------------------- #

def clamp(val, a, b):
    return max(a, min(b, val))

def rgb_to_cmyk(r, g, b):
    clipped = False
    if r < 0 or g < 0 or b < 0 or r > 255 or g > 255 or b > 255:
        clipped = True
    r_f, g_f, b_f = clamp(r, 0, 255) / 255.0, clamp(g, 0, 255) / 255.0, clamp(b, 0, 255) / 255.0
    if r_f == 0 and g_f == 0 and b_f == 0:
        return 0.0, 0.0, 0.0, 1.0, clipped
    c = 1 - r_f
    m = 1 - g_f
    y = 1 - b_f
    k = min(c, m, y)
    denom = (1 - k)
    if denom == 0:
        return 0.0, 0.0, 0.0, 1.0, clipped
    c = (c - k) / denom
    m = (m - k) / denom
    y = (y - k) / denom
    return clamp(c, 0.0, 1.0), clamp(m, 0.0, 1.0), clamp(y, 0.0, 1.0), clamp(k, 0.0, 1.0), clipped

def cmyk_to_rgb(c, m, y, k):
    c_, m_, y_, k_ = clamp(c, 0.0, 1.0), clamp(m, 0.0, 1.0), clamp(y, 0.0, 1.0), clamp(k, 0.0, 1.0)
    r = 255.0 * (1 - c_) * (1 - k_)
    g = 255.0 * (1 - m_) * (1 - k_)
    b = 255.0 * (1 - y_) * (1 - k_)
    clipped = False
    if any(v < 0 or v > 255 for v in (r, g, b)):
        clipped = True
    return int(round(clamp(r, 0, 255))), int(round(clamp(g, 0, 255))), int(round(clamp(b, 0, 255))), clipped

def rgb_to_hls_vals(r, g, b):
    rf, gf, bf = clamp(r, 0, 255)/255.0, clamp(g, 0, 255)/255.0, clamp(b, 0, 255)/255.0
    h, l, s = colorsys.rgb_to_hls(rf, gf, bf)
    clipped = False
    if r < 0 or g < 0 or b < 0 or r > 255 or g > 255 or b > 255:
        clipped = True
    return h, l, s, clipped

def hls_to_rgb_vals(h, l, s):
    if not math.isfinite(h) or not math.isfinite(l) or not math.isfinite(s):
        return 0,0,0, True
    h_wrapped = h % 1.0
    l_c = clamp(l, 0.0, 1.0)
    s_c = clamp(s, 0.0, 1.0)
    r_f, g_f, b_f = colorsys.hls_to_rgb(h_wrapped, l_c, s_c)
    r, g, b = int(round(r_f * 255)), int(round(g_f * 255)), int(round(b_f * 255))
    clipped = False
    return r, g, b, clipped

def rgb_to_hex(r, g, b):
    return f"#{clamp(int(round(r)),0,255):02x}{clamp(int(round(g)),0,255):02x}{clamp(int(round(b)),0,255):02x}"

def hex_to_rgb(hexstr):
    s = hexstr.strip().lstrip('#')
    if len(s) == 3:
        s = ''.join(ch*2 for ch in s)
    if len(s) != 6:
        raise ValueError("HEX должен быть в формате RRGGBB")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)

# ---------------------- GUI Приложение ---------------------- #

class ColorStudioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Studio — CMYK ↔ RGB ↔ HLS")
        self.root.geometry("900x640")
        self.root.minsize(820, 560)

        self._updating = False
        self.current_rgb = [255, 0, 0]
        self.swatches = []

        self.build_ui()
        self.update_from_rgb(self.current_rgb, reason="init")

    def build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="Color Studio", font=("Segoe UI", 16, "bold")).pack(side="left")
        self.status_var = tk.StringVar(value="Готово")
        self.status = ttk.Label(top, textvariable=self.status_var, anchor="e")
        self.status.pack(side="right")

        content = ttk.Frame(self.root)
        content.pack(fill="both", expand=True, padx=8, pady=6)

        left = ttk.Frame(content)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(content, width=300)
        right.pack(side="right", fill="y")

        self.notebook = ttk.Notebook(left)
        self.notebook.pack(fill="both", expand=True, pady=(0,8))

        self.tab_cmyk = ttk.Frame(self.notebook)
        self.tab_rgb = ttk.Frame(self.notebook)
        self.tab_hls = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_cmyk, text="CMYK")
        self.notebook.add(self.tab_rgb, text="RGB")
        self.notebook.add(self.tab_hls, text="HLS")

        self.build_cmyk_tab(self.tab_cmyk)
        self.build_rgb_tab(self.tab_rgb)
        self.build_hls_tab(self.tab_hls)

        self.build_preview_panel(right)

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=8, pady=(0,8))
        ttk.Button(bottom, text="Сохранить swatch", command=self.save_swatch).pack(side="left")
        ttk.Button(bottom, text="Экспорт .png предпросмотра", command=self.export_preview_image).pack(side="left", padx=6)
        ttk.Label(bottom, text="  ").pack(side="left", expand=True)
        ttk.Button(bottom, text="Сбросить к белому", command=self.reset_white).pack(side="right")

    # ------------------ Вкладки ------------------ #
    def build_cmyk_tab(self, parent):
        self.c_var = tk.DoubleVar(value=0.0)
        self.m_var = tk.DoubleVar(value=1.0)
        self.y_var = tk.DoubleVar(value=1.0)
        self.k_var = tk.DoubleVar(value=0.0)

        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_model_controls(frame,
                                   labels=["C", "M", "Y", "K"],
                                   vars_list=[self.c_var, self.m_var, self.y_var, self.k_var],
                                   ranges=[(0.0,1.0)]*4,
                                   steps=[0.001]*4,
                                   on_change=self.cmyk_changed,
                                   show_percent=True)

    def build_rgb_tab(self, parent):
        self.r_var = tk.IntVar(value=255)
        self.g_var = tk.IntVar(value=0)
        self.b_var = tk.IntVar(value=0)

        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_model_controls(frame,
                                   labels=["R", "G", "B"],
                                   vars_list=[self.r_var, self.g_var, self.b_var],
                                   ranges=[(0,255)]*3,
                                   steps=[1]*3,
                                   on_change=self.rgb_changed,
                                   show_percent=False)

    def build_hls_tab(self, parent):
        self.h_var = tk.DoubleVar(value=0.0)
        self.l_var = tk.DoubleVar(value=0.5)
        self.s_var = tk.DoubleVar(value=1.0)

        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_model_controls(frame,
                                   labels=["H", "L", "S"],
                                   vars_list=[self.h_var, self.l_var, self.s_var],
                                   ranges=[(0.0,1.0),(0.0,1.0),(0.0,1.0)],
                                   steps=[0.001,0.001,0.001],
                                   on_change=self.hls_changed,
                                   show_percent=False,
                                   hls_mode=True)

    def _build_model_controls(self, parent, labels, vars_list, ranges, steps, on_change, show_percent=False, hls_mode=False):
        rows = len(labels)
        for i, (label, var) in enumerate(zip(labels, vars_list)):
            row = ttk.Frame(parent)
            row.pack(fill="x", pady=6)
            ttk.Label(row, text=label, width=3).pack(side="left")

            frm, to = ranges[0] if len(ranges)==1 else ranges[i]
            scale = ttk.Scale(row, from_=frm, to=to, orient="horizontal", variable=var,
                              command=lambda e, cb=on_change: cb())
            scale.pack(side="left", fill="x", expand=True, padx=(6,6))

            if isinstance(var, tk.IntVar):
                spin = ttk.Spinbox(row, from_=frm, to=to, textvariable=var, width=6, increment=1,
                                   command=on_change)
                spin.pack(side="left", padx=(0,6))
                spin.bind("<Return>", lambda e, cb=on_change: cb())
            else:
                ent = ttk.Entry(row, textvariable=var, width=8)
                ent.pack(side="left", padx=(0,6))
                ent.bind("<Return>", lambda e, cb=on_change: cb())
                def wheel(e, v=var, r=(frm,to), step=steps[i]):
                    delta = 1 if e.delta>0 else -1
                    v.set(clamp(v.get() + delta*step, r[0], r[1]))
                    on_change()
                ent.bind("<MouseWheel>", wheel)
            if show_percent:
                pct = ttk.Label(row, textvariable=tk.StringVar(value=f"{round(var.get()*100)}%"))
                pct.pack(side="left")
                def update_pct(var=var, label_var=pct):
                    label_var.config(text=f"{round(var.get()*100)}%")
                var.trace_add("write", lambda *a, fn=update_pct: fn())

            if hls_mode and label == "H":
                ttk.Label(row, text="(0..1 ≡ 0°..360°)").pack(side="left", padx=(4,0))

        bottom = ttk.Frame(parent)
        bottom.pack(fill="x", pady=(8,0))
        if any(isinstance(v, tk.IntVar) for v in vars_list):
            if any(lab == "R" for lab in labels):
                btn = ttk.Button(bottom, text="Палитра (Color Picker)", command=self.choose_color)
                btn.pack(side="left")
                ttk.Label(bottom, text="HEX:").pack(side="left", padx=(8,2))
                self.hex_var = tk.StringVar(value=rgb_to_hex(*self.current_rgb))
                hex_entry = ttk.Entry(bottom, textvariable=self.hex_var, width=10)
                hex_entry.pack(side="left")
                ttk.Button(bottom, text="Применить HEX", command=self.apply_hex).pack(side="left", padx=(6,0))

    # ---------------------- Панель предпросмотра и swatches ---------------------- #
    def build_preview_panel(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=False, padx=6, pady=6)

        ttk.Label(frame, text="Preview", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.preview_canvas = tk.Canvas(frame, width=280, height=180, bd=1, relief="solid")
        self.preview_canvas.pack(pady=(6,8))
        self.preview_rect = self.preview_canvas.create_rectangle(2,2,278,178, fill=rgb_to_hex(*self.current_rgb), outline="")

        info = ttk.Frame(frame)
        info.pack(fill="x")
        ttk.Label(info, text="HEX:").grid(row=0, column=0, sticky="w")
        self.preview_hex_var = tk.StringVar(value=rgb_to_hex(*self.current_rgb))
        ttk.Entry(info, textvariable=self.preview_hex_var, width=12).grid(row=0, column=1, sticky="w")
        ttk.Button(info, text="Копировать", command=self.copy_hex).grid(row=0, column=2, padx=6)

        ttk.Label(info, text="RGB:").grid(row=1, column=0, sticky="w", pady=(4,0))
        self.preview_rgb_var = tk.StringVar(value=f"{self.current_rgb[0]}, {self.current_rgb[1]}, {self.current_rgb[2]}")
        ttk.Entry(info, textvariable=self.preview_rgb_var, width=18).grid(row=1, column=1, sticky="w", pady=(4,0))

        ttk.Label(frame, text="Swatches").pack(anchor="w", pady=(10,0))
        self.swatch_frame = ttk.Frame(frame)
        self.swatch_frame.pack(fill="x", pady=(4,0))

        self.swatch_canvas = tk.Canvas(self.swatch_frame, width=280, height=120)
        self.swatch_canvas.pack(side="left", fill="both", expand=True)
        self.swatch_items = []

        self.update_swatches_ui()

    # ---------------------- Действия пользователя ---------------------- #

    def choose_color(self):
        chosen = colorchooser.askcolor(color=rgb_to_hex(*self.current_rgb), parent=self.root)
        if chosen and chosen[0]:
            r,g,b = map(int, chosen[0])
            self.update_from_rgb([r,g,b], reason="picker")

    def apply_hex(self):
        s = self.hex_var.get().strip()
        try:
            r,g,b = hex_to_rgb(s)
        except Exception as e:
            self.set_status(f"Неверный HEX: {e}", error=True)
            return
        self.update_from_rgb([r,g,b], reason="hex")

    def copy_hex(self):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.preview_hex_var.get())
            self.set_status("HEX скопирован в буфер обмена")
        except Exception:
            self.set_status("Не удалось скопировать в буфер", error=True)

    def save_swatch(self):
        h = self.preview_hex_var.get()
        if h not in self.swatches:
            self.swatches.insert(0, h)
        # limit to 24
        self.swatches = self.swatches[:24]
        self.update_swatches_ui()
        self.set_status(f"Сохранён swatch {h}")

    def export_preview_image(self):
        from tkinter import filedialog
        r,g,b = self.current_rgb
        fname = filedialog.asksaveasfilename(defaultextension=".ppm", filetypes=[("PPM image","*.ppm"),("All files","*.*")])
        if not fname:
            return
        try:
            with open(fname, "wb") as f:
                w,h = 256,128
                f.write(b"P6\n%d %d\n255\n" % (w,h))
                f.write(bytes([r,g,b])*w*h)
            self.set_status(f"Экспортировано в {fname}")
        except Exception as e:
            self.set_status(f"Ошибка экспорта: {e}", error=True)

    def reset_white(self):
        self.update_from_rgb([255,255,255], reason="reset")

    # ---------------------- Обработчики изменений для моделей ---------------------- #
    def cmyk_changed(self):
        if self._updating:
            return
        self._updating = True
        try:
            c = float(self.c_var.get())
            m = float(self.m_var.get())
            y = float(self.y_var.get())
            k = float(self.k_var.get())
        except Exception:
            self.set_status("Ошибка ввода CMYK", error=True)
            self._updating = False
            return
        r,g,b, clipped = cmyk_to_rgb(c,m,y,k)
        if clipped:
            self.set_status("Клиппинг при CMYK->RGB (значения были ограничены)", error=False)
        else:
            self.set_status("CMYK изменён")
        self.update_from_rgb([r,g,b], reason="cmyk")
        self._updating = False

    def rgb_changed(self):
        if self._updating:
            return
        self._updating = True
        try:
            r = int(self.r_var.get())
            g = int(self.g_var.get())
            b = int(self.b_var.get())
        except Exception:
            self.set_status("Ошибка ввода RGB", error=True)
            self._updating = False
            return
        r, g, b = clamp(r,0,255), clamp(g,0,255), clamp(b,0,255)
        self.update_from_rgb([r,g,b], reason="rgb")
        self._updating = False

    def hls_changed(self):
        if self._updating:
            return
        self._updating = True
        try:
            h = float(self.h_var.get())
            l = float(self.l_var.get())
            s = float(self.s_var.get())
        except Exception:
            self.set_status("Ошибка ввода HLS", error=True)
            self._updating = False
            return
        r,g,b, clipped = hls_to_rgb_vals(h,l,s)
        if clipped:
            self.set_status("Клиппинг при HLS->RGB", error=False)
        else:
            self.set_status("HLS изменён")
        self.update_from_rgb([r,g,b], reason="hls")
        self._updating = False

    # ---------------------- Централизация обновлений ---------------------- #
    def update_from_rgb(self, rgb_triplet, reason=""):
        r, g, b = map(int, rgb_triplet)
        self.current_rgb = [r,g,b]

        hexstr = rgb_to_hex(r,g,b)
        self.preview_canvas.itemconfig(self.preview_rect, fill=hexstr)
        self.preview_hex_var.set(hexstr.upper())
        self.preview_rgb_var.set(f"{r}, {g}, {b}")
        self._updating = True
        try:
            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)
            c, m, y, k, clipped_cmyk = rgb_to_cmyk(r,g,b)
            self.c_var.set(round(c, 6))
            self.m_var.set(round(m, 6))
            self.y_var.set(round(y, 6))
            self.k_var.set(round(k, 6))
            h, l, s, clipped_hls = rgb_to_hls_vals(r,g,b)
            self.h_var.set(round(h,6))
            self.l_var.set(round(l,6))
            self.s_var.set(round(s,6))
            try:
                self.hex_var.set(hexstr.upper())
            except Exception:
                pass
            self.update_swatches_ui()
            if reason == "init":
                self.set_status("Интерфейс готов")
            else:
                self.set_status(f"Обновление по {reason}")
            if clipped_cmyk or clipped_hls:
                self.set_status("Произошло округление/обрезание при переводах (клиппинг).", error=False)
        finally:
            self._updating = False

    # ---------------------- UI: swatches ---------------------- #
    def update_swatches_ui(self):
        c = self.swatch_canvas
        c.delete("all")
        pad = 6
        w = 40
        h = 24
        cols = 6
        for idx, hexc in enumerate(self.swatches):
            row = idx // cols
            col = idx % cols
            x = pad + col*(w+pad)
            y = pad + row*(h+pad)
            rect = c.create_rectangle(x, y, x+w, y+h, fill=hexc, outline="black")
            def make_apply(hexcolor):
                return lambda e: self.update_from_rgb(list(hex_to_rgb(hexcolor)), reason="swatch")
            c.tag_bind(rect, "<Button-1>", make_apply(hexc))
            def make_remove(ix):
                return lambda e: self.remove_swatch(ix)
            c.tag_bind(rect, "<Button-3>", make_remove(idx))

    def remove_swatch(self, idx):
        if idx < len(self.swatches):
            removed = self.swatches.pop(idx)
            self.update_swatches_ui()
            self.set_status(f"Удалён swatch {removed}")

    # ---------------------- UX / статус ---------------------- #
    def set_status(self, text, error=False):
        self.status_var.set(text)
        if error:
            self.status.configure(foreground="red")
        else:
            self.status.configure(foreground="black")

# ---------------------- Main ---------------------- #
def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    app = ColorStudioApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
