import tkinter as tk
from tkinter import messagebox
import socket
import threading
import queue
import time


DARK = {
    "bg":        "#1a1a1a",
    "panel":     "#222222",
    "card":      "#2a2a2a",
    "row_alt":   "#252525",
    "border":    "#383838",
    "text":      "#e0e0e0",
    "muted":     "#666666",
    "accent":    "#4a90d9",
    "accent_h":  "#357abd",
    "taken":     "#d9534a",
    "available": "#4aad6f",
    "checking":  "#e0a030",
    "input_bg":  "#2f2f2f",
}

THREAD_COUNT = 10
TIMEOUT = 5


def clean_domain(raw: str) -> str:
    d = raw.strip().lower()
    for prefix in ("https://", "http://", "www."):
        if d.startswith(prefix):
            d = d[len(prefix):]
    d = d.split("/")[0]
    return d


def check_domain(domain: str) -> str:
    try:
        socket.setdefaulttimeout(TIMEOUT)
        socket.gethostbyname(domain)
        return "dolu"
    except socket.gaierror:
        return "müsait"
    except Exception:
        return "hata"


class DomainChecker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Domain Checker")
        self.geometry("700x560")
        self.minsize(560, 400)
        self.configure(bg=DARK["bg"])

        self._results = {}
        self._checking = False
        self._queue = queue.Queue()

        self._build_ui()

    def _build_ui(self):
        left = tk.Frame(self, bg=DARK["bg"], width=260)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(14, 6), pady=14)
        left.pack_propagate(False)

        right = tk.Frame(self, bg=DARK["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 14), pady=14)

        self._build_input(left)
        self._build_results(right)

    def _build_input(self, parent):
        tk.Label(
            parent, text="Domainleri girin",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            parent, text="Her satıra bir domain",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(0, 8))

        text_frame = tk.Frame(parent, bg=DARK["card"])
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = tk.Scrollbar(text_frame, bg=DARK["card"], troughcolor=DARK["card"], bd=0, width=8)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._text = tk.Text(
            text_frame,
            bg=DARK["input_bg"], fg=DARK["text"],
            insertbackground=DARK["text"],
            relief=tk.FLAT, font=("Consolas", 10),
            bd=0, padx=8, pady=8,
            yscrollcommand=scrollbar.set,
            wrap=tk.NONE
        )
        self._text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._text.yview)

        self._text.insert("1.0", "ornek.com\nornek.net\nornek.io")

        tk.Label(
            parent, text="Uzantı ekle (opsiyonel)",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(0, 4))

        self._ext_var = tk.StringVar(value=".com .net .io .org")
        tk.Entry(
            parent, textvariable=self._ext_var,
            bg=DARK["input_bg"], fg=DARK["text"],
            insertbackground=DARK["text"],
            relief=tk.FLAT, font=("Segoe UI", 9)
        ).pack(fill=tk.X, ipady=5, pady=(0, 10))

        tk.Label(
            parent,
            text="Uzantısız domain girerseniz\nyukarıdaki uzantılar eklenir.",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8), justify=tk.LEFT
        ).pack(anchor="w", pady=(0, 10))

        self._check_btn = tk.Button(
            parent, text="Kontrol Et",
            command=self._start,
            bg=DARK["accent"], fg="#ffffff",
            activebackground=DARK["accent_h"], activeforeground="#ffffff",
            relief=tk.FLAT, font=("Segoe UI", 10, "bold"),
            pady=8, cursor="hand2"
        )
        self._check_btn.pack(fill=tk.X)

        self._progress_label = tk.Label(
            parent, text="",
            bg=DARK["bg"], fg=DARK["muted"],
            font=("Segoe UI", 8)
        )
        self._progress_label.pack(pady=(6, 0))

    def _build_results(self, parent):
        header = tk.Frame(parent, bg=DARK["panel"])
        header.pack(fill=tk.X, pady=(0, 4))

        for text, anchor, w in [("Domain", "w", 24), ("Durum", "center", 10)]:
            tk.Label(
                header, text=text, width=w, anchor=anchor,
                bg=DARK["panel"], fg=DARK["muted"],
                font=("Segoe UI", 8, "bold"), padx=8, pady=5
            ).pack(side=tk.LEFT)

        summary = tk.Frame(parent, bg=DARK["bg"])
        summary.pack(fill=tk.X, pady=(0, 6))

        self._avail_label = tk.Label(summary, text="Müsait: 0", bg=DARK["bg"], fg=DARK["available"], font=("Segoe UI", 9))
        self._avail_label.pack(side=tk.LEFT, padx=(0, 12))

        self._taken_label = tk.Label(summary, text="Dolu: 0", bg=DARK["bg"], fg=DARK["taken"], font=("Segoe UI", 9))
        self._taken_label.pack(side=tk.LEFT, padx=(0, 12))

        self._error_label = tk.Label(summary, text="", bg=DARK["bg"], fg=DARK["muted"], font=("Segoe UI", 9))
        self._error_label.pack(side=tk.LEFT)

        list_frame = tk.Frame(parent, bg=DARK["card"])
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, bg=DARK["card"], troughcolor=DARK["card"], bd=0, width=8)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = tk.Canvas(list_frame, bg=DARK["card"], highlightthickness=0, yscrollcommand=scrollbar.set)
        self._canvas.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._canvas.yview)

        self._rows = tk.Frame(self._canvas, bg=DARK["card"])
        self._win = self._canvas.create_window((0, 0), window=self._rows, anchor="nw")

        self._rows.bind("<Configure>", lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>", lambda e: self._canvas.itemconfig(self._win, width=e.width))

    def _parse_domains(self) -> list:
        raw_lines = self._text.get("1.0", tk.END).strip().splitlines()
        exts = [e.strip() for e in self._ext_var.get().split() if e.strip()]
        domains = []

        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            d = clean_domain(line)
            if not d:
                continue
            if "." in d:
                domains.append(d)
            else:
                for ext in exts:
                    ext = ext if ext.startswith(".") else "." + ext
                    domains.append(d + ext)

        return list(dict.fromkeys(domains))

    def _start(self):
        if self._checking:
            return

        domains = self._parse_domains()
        if not domains:
            messagebox.showwarning("Uyarı", "Kontrol edilecek domain bulunamadı.")
            return

        self._results = {d: "bekleniyor" for d in domains}
        self._checking = True
        self._check_btn.config(state=tk.DISABLED, text="Kontrol ediliyor...")
        self._render_results()

        def worker():
            q = queue.Queue()
            for d in domains:
                q.put(d)

            total = len(domains)
            done_count = [0]
            lock = threading.Lock()

            def process():
                while True:
                    try:
                        domain = q.get_nowait()
                    except queue.Empty:
                        break
                    result = check_domain(domain)
                    with lock:
                        self._results[domain] = result
                        done_count[0] += 1
                        count = done_count[0]
                    self.after(0, lambda d=domain, r=result, c=count: self._update_row(d, r, c, total))
                    q.task_done()

            threads = [threading.Thread(target=process, daemon=True) for _ in range(min(THREAD_COUNT, len(domains)))]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            self.after(0, self._finish)

        threading.Thread(target=worker, daemon=True).start()

    def _render_results(self):
        for w in self._rows.winfo_children():
            w.destroy()

        for i, (domain, status) in enumerate(self._results.items()):
            bg = DARK["card"] if i % 2 == 0 else DARK["row_alt"]
            self._make_row(domain, status, bg, i)

    def _make_row(self, domain, status, bg, i):
        row = tk.Frame(self._rows, bg=bg, name=f"row_{i}")
        row.pack(fill=tk.X)

        tk.Label(
            row, text=domain, anchor="w", width=26,
            bg=bg, fg=DARK["text"],
            font=("Consolas", 9), padx=10, pady=6
        ).pack(side=tk.LEFT)

        color = {
            "müsait":    DARK["available"],
            "dolu":      DARK["taken"],
            "hata":      DARK["muted"],
            "bekleniyor": DARK["checking"],
        }.get(status, DARK["muted"])

        icon = {
            "müsait":    "✓ Müsait",
            "dolu":      "✗ Dolu",
            "hata":      "? Hata",
            "bekleniyor": "… Bekliyor",
        }.get(status, status)

        tk.Label(
            row, text=icon, anchor="center", width=12,
            bg=bg, fg=color,
            font=("Segoe UI", 9, "bold"), pady=6
        ).pack(side=tk.LEFT)

    def _update_row(self, domain, result, done, total):
        self._results[domain] = result
        self._render_results()
        self._progress_label.config(text=f"{done} / {total} kontrol edildi")
        self._update_summary()

    def _update_summary(self):
        vals = list(self._results.values())
        avail = vals.count("müsait")
        taken = vals.count("dolu")
        errors = vals.count("hata")
        self._avail_label.config(text=f"Müsait: {avail}")
        self._taken_label.config(text=f"Dolu: {taken}")
        self._error_label.config(text=f"Hata: {errors}" if errors else "")

    def _finish(self):
        self._checking = False
        self._check_btn.config(state=tk.NORMAL, text="Kontrol Et")
        total = len(self._results)
        self._progress_label.config(text=f"Tamamlandı — {total} domain kontrol edildi")
        self._update_summary()


if __name__ == "__main__":
    app = DomainChecker()
    app.mainloop()
