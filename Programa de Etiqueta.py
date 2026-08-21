import sys
import os
import subprocess
import json
import time
import threading
import queue

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import qrcode

import win32print

import tkinter as tk
from tkinter import ttk, messagebox


# =========================
# Arquivos e caminhos
# =========================
def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)  # EXE
    return os.path.dirname(os.path.abspath(__file__))  # Python/VSCode


# ========= CONFIG FIXA =========
JSON_FILE = #(Crie Seu JSON e Coloque Aqui)  # service account
CONFIG_PATH = os.path.join(app_dir(), "config.json")
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
# ===============================


# =========================
# Utils
# =========================
def to_a1(col_num: int) -> str:
    """1 -> A, 2 -> B ... 27 -> AA"""
    s = ""
    n = col_num
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def is_impresso(v) -> bool:
    v = str(v or "").strip().lower()
    return v in ("sim", "yes", "1", "true", "ok", "x")


def listar_impressoras():
    printers = []
    for p in win32print.EnumPrinters(
        win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
    ):
        printers.append(p[2])
    return printers


def carregar_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def salvar_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# =========================
# Tela inicial (1ª vez)
# =========================
def tela_config_inicial():
    printers = listar_impressoras()
    default_printer = win32print.GetDefaultPrinter() if printers else ""

    root = tk.Tk()
    root.title("Configurar Impressora Automática")
    root.resizable(False, False)

    # ícone
    try:
        ico = os.path.join(app_dir(), "Impressao.ico")
        if os.path.exists(ico):
            root.iconbitmap(ico)
    except:
        pass

    frm = ttk.Frame(root, padding=12)
    frm.grid()

    ttk.Label(frm, text="ID da Planilha (Google Sheets):").grid(row=0, column=0, sticky="w")
    id_var = tk.StringVar()
    ttk.Entry(frm, textvariable=id_var, width=62).grid(row=1, column=0, pady=(4, 10), sticky="w")

    ttk.Label(frm, text="Impressora:").grid(row=2, column=0, sticky="w")
    printer_var = tk.StringVar(value=default_printer)
    cb = ttk.Combobox(frm, textvariable=printer_var, values=printers, width=59, state="readonly")
    cb.grid(row=3, column=0, pady=(4, 10), sticky="w")

    ttk.Label(frm, text="Dica: o ID fica entre /d/ e /edit na URL da planilha.").grid(row=4, column=0, sticky="w")

    def on_save():
        planilha_id = id_var.get().strip()
        impressora = printer_var.get().strip()

        if not planilha_id:
            messagebox.showerror("Erro", "Informe o ID da planilha.")
            return
        if not impressora:
            messagebox.showerror("Erro", "Selecione uma impressora.")
            return

        salvar_config({"PLANILHA_ID": planilha_id, "IMPRESSORA": impressora})
        messagebox.showinfo("OK", "Configuração salva! O programa vai iniciar o monitoramento.")
        root.destroy()

    ttk.Button(frm, text="Salvar e Iniciar", command=on_save).grid(row=5, column=0, sticky="e")
    root.mainloop()


# =========================
# PDF (100x150mm) - profissional
# =========================
def gerar_pdf_etiqueta(dado: dict):
    pedido = str(dado.get("Pedido", "")).strip()
    vendedor = str(dado.get("Vendedor", "")).strip()
    produto = str(dado.get("Produto", "")).strip()
    valor = str(dado.get("Valor", "")).strip()

    qr_texto = f"Pedido:{pedido} | Vendedor:{vendedor} | Produto:{produto} | Valor:{valor}"

    W, H = 100 * mm, 150 * mm
    mx, my = 5 * mm, 5 * mm

    # Arquivo temporário fixo (recomendado: NÃO deixar aberto no Adobe)
    nome_pdf = os.path.join(app_dir(), "etiqueta_temp.pdf")
    c = canvas.Canvas(nome_pdf, pagesize=(W, H))

    # topo (faixa escura)
    top_h = 18 * mm
    c.setFillColorRGB(0.06, 0.09, 0.14)
    c.rect(0, H - top_h, W, top_h, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(W / 2, H - 12 * mm, "FENIX")
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, H - 16 * mm, "CAMISETAS PERSONALIZADAS")

    c.setFillColorRGB(0, 0, 0)

    # bloco pedido
    y = H - top_h - 6 * mm
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(W / 2, y - 10 * mm, f"PEDIDO {pedido}")

    c.setLineWidth(0.6)
    c.line(mx, y - 14 * mm, W - mx, y - 14 * mm)

    # dados
    c.setFont("Helvetica", 10)
    c.drawString(mx + 2 * mm, y - 22 * mm, f"Produto: {produto}")
    c.drawString(mx + 2 * mm, y - 27 * mm, f"Valor: {valor}")
    c.drawString(mx + 2 * mm, y - 38 * mm, f"Vendedor: {vendedor}")

    # caixa do pedido
    c.setLineWidth(0.8)
    c.rect(mx, y - 50 * mm, W - 2 * mx, 18 * mm)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(mx + 2 * mm, y - 45 * mm, f"N° Pedido: {pedido}")

    # checkboxes
    box = 8 * mm
    c.setLineWidth(1.0)
    c.rect(mx, y - 70 * mm, box, box)
    c.setFont("Helvetica", 11)
    c.drawString(mx + 12 * mm, y - 68 * mm, "EMBALADO")

    c.rect(mx, y - 84 * mm, box, box)
    c.drawString(mx + 12 * mm, y - 82 * mm, "CONFERIDO")

    # QR
    qr_size = 32 * mm
    qr_x = W - mx - qr_size
    qr_y = my + 4 * mm

    qr_img = qrcode.make(qr_texto)
    qr_path = os.path.join(app_dir(), "qr_temp.png")
    qr_img.save(qr_path)

    c.setLineWidth(0.8)
    c.rect(qr_x - 1 * mm, qr_y - 1 * mm, qr_size + 2 * mm, qr_size + 2 * mm)
    c.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size)

    # rodapé
    c.setFont("Helvetica", 8)
    c.drawString(mx, my + 1 * mm, "Controle interno")

    c.save()
    return nome_pdf


# =========================
# Impressão PDF (Adobe/Reader)
# =========================
def imprimir_pdf(caminho_pdf: str, impressora: str):
    if not os.path.exists(caminho_pdf):
        print("PDF não encontrado:", caminho_pdf)
        return

    caminhos_possiveis = [
        r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
        r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
        r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
        r"C:\Program Files (x86)\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
    ]

    acro = None
    for p in caminhos_possiveis:
        if os.path.exists(p):
            acro = p
            break

    if not acro:
        raise RuntimeError("Adobe Reader/Acrobat não encontrado. Instale o Adobe Reader DC.")

    caminho_pdf = os.path.abspath(caminho_pdf)

    # /t imprime direto passando impressora (pode ainda piscar janela dependendo do Windows/driver)
    subprocess.run([acro, "/t", caminho_pdf, impressora], check=False)

    # dá tempo do spooler pegar o arquivo
    time.sleep(2)


# =========================
# Worker de monitoramento (thread)
# =========================
class MonitorWorker:
    def __init__(self, sheet, impressora):
        self.sheet = sheet
        self.impressora = impressora

        self.ui_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = None
        self.print_enabled = True

        self.last_snapshot = []  # cache de dicts com _ROW

        # coluna "Impresso" (definida no start)
        self.idx_impresso0 = None  # 0-based
        self.col_impresso1 = None  # 1-based
        self.col_impresso_a1 = None  # letra

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def set_print_enabled(self, enabled: bool):
        self.print_enabled = enabled

    def init_header(self):
        header = self.sheet.row_values(1)
        if "Impresso" not in header:
            raise RuntimeError("Crie uma coluna chamada 'Impresso' na planilha.")
        self.idx_impresso0 = header.index("Impresso")
        self.col_impresso1 = self.idx_impresso0 + 1
        self.col_impresso_a1 = to_a1(self.col_impresso1)

    def loop(self):
        try:
            self.init_header()
        except Exception as e:
            self.ui_queue.put(("erro", str(e)))
            return

        while not self.stop_event.is_set():
            try:
                # 1) lê tudo
                values = self.sheet.get_all_values()
                if len(values) < 2:
                    self.ui_queue.put(("table", []))
                    self.ui_queue.put(("status", "Sem dados"))
                    time.sleep(5)
                    continue

                header = values[0]
                registros = []
                for row_real in range(2, len(values) + 1):
                    row_vals = values[row_real - 1]
                    row_dict = {
                        header[i]: (row_vals[i] if i < len(row_vals) else "")
                        for i in range(len(header))
                    }
                    row_dict["_ROW"] = row_real
                    registros.append(row_dict)

                self.last_snapshot = registros
                self.ui_queue.put(("table", registros))

                if not self.print_enabled:
                    self.ui_queue.put(("status", "PAUSADO"))
                    time.sleep(5)
                    continue

                # 2) imprime pendentes e faz batch_update
                updates = []
                for row in registros:
                    if is_impresso(row.get("Impresso")):
                        continue

                    self.ui_queue.put(("status", f"IMPRIMINDO linha {row['_ROW']}..."))

                    pdf = gerar_pdf_etiqueta(row)
                    imprimir_pdf(pdf, self.impressora)

                    updates.append(row["_ROW"])
                    time.sleep(1)

                if updates:
                    body = []
                    for r in updates:
                        a1 = f"{self.col_impresso_a1}{r}"
                        body.append({"range": a1, "values": [["SIM"]]})
                    self.sheet.batch_update(body)
                    self.ui_queue.put(("status", f"OK: {len(updates)} marcada(s) como SIM"))
                else:
                    self.ui_queue.put(("status", "ATIVO (sem pendências)"))

            except Exception as e:
                self.ui_queue.put(("erro", f"Falha no monitoramento: {e}"))

            time.sleep(8)


# =========================
# Painel (Tkinter)
# =========================
def abrir_painel(sheet, impressora):
    root = tk.Tk()
    root.title("Impressora Automática - Painel")
    root.geometry("1100x620")

    # ícone da janela
    try:
        ico = os.path.join(app_dir(), "Impressao.ico")
        if os.path.exists(ico):
            root.iconbitmap(ico)
    except:
        pass

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    # Topbar
    top = ttk.Frame(root, padding=10)
    top.pack(fill="x")

    lbl_title = ttk.Label(top, text="Impressora Automática", font=("Segoe UI", 12, "bold"))
    lbl_title.pack(side="left")

    lbl_status = ttk.Label(top, text="Status: Iniciando...", font=("Segoe UI", 10))
    lbl_status.pack(side="left", padx=(14, 0))

    btn_reprint = ttk.Button(top, text="Reimprimir selecionado")
    btn_reprint.pack(side="right", padx=(6, 0))

    btn_refresh = ttk.Button(top, text="Atualizar")
    btn_refresh.pack(side="right", padx=(6, 0))

    btn_toggle = ttk.Button(top, text="Pausar impressão")
    btn_toggle.pack(side="right", padx=(6, 0))

    lbl_prn = ttk.Label(top, text=f"Impressora: {impressora}", font=("Segoe UI", 9))
    lbl_prn.pack(side="right", padx=(10, 12))

    # Table
    columns = ("ROW", "ID", "Pedido", "Vendedor", "Produto", "Valor", "Status", "Impresso")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
    tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    widths = {
        "ROW": 60,
        "ID": 80,
        "Pedido": 120,
        "Vendedor": 140,
        "Produto": 280,
        "Valor": 120,
        "Status": 120,
        "Impresso": 90,
    }

    for c in columns:
        tree.heading(c, text=c)
        tree.column(c, width=widths.get(c, 120), anchor="w")

    # Worker
    worker = MonitorWorker(sheet, impressora)
    worker.start()

    # UI queue pump
    def process_ui_queue():
        while True:
            try:
                kind, payload = worker.ui_queue.get_nowait()
            except queue.Empty:
                break

            if kind == "status":
                lbl_status.config(text=f"Status: {payload}")

            elif kind == "erro":
                lbl_status.config(text="Status: ERRO")
                messagebox.showerror("Erro", payload)

            elif kind == "table":
                tree.delete(*tree.get_children())
                for row in payload:
                    tree.insert(
                        "",
                        "end",
                        values=(
                            row.get("_ROW", ""),
                            row.get("ID", ""),
                            row.get("Pedido", ""),
                            row.get("Vendedor", ""),
                            row.get("Produto", ""),
                            row.get("Valor", ""),
                            row.get("Status", ""),
                            row.get("Impresso", ""),
                        ),
                    )

        root.after(200, process_ui_queue)

    def on_toggle():
        worker.set_print_enabled(not worker.print_enabled)
        if worker.print_enabled:
            btn_toggle.config(text="Pausar impressão")
            lbl_status.config(text="Status: ATIVO")
        else:
            btn_toggle.config(text="Ativar impressão")
            lbl_status.config(text="Status: PAUSADO")

    def on_refresh():
        # o loop já atualiza sozinho; aqui só dá feedback
        lbl_status.config(text="Status: Atualizando...")

    def on_reprint():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione uma linha para reimprimir.")
            return

        item = tree.item(sel[0], "values")
        try:
            row_real = int(item[0])  # ROW
        except:
            messagebox.showerror("Erro", "Não consegui ler o número da linha (ROW).")
            return

        # acha no cache
        alvo = None
        for r in worker.last_snapshot:
            if r.get("_ROW") == row_real:
                alvo = r
                break

        if not alvo:
            messagebox.showerror("Erro", "Não encontrei essa linha no cache. Clique em Atualizar.")
            return

        try:
            lbl_status.config(text=f"Status: REIMPRIMINDO linha {row_real}...")
            pdf = gerar_pdf_etiqueta(alvo)
            imprimir_pdf(pdf, impressora)
            lbl_status.config(text=f"Status: REIMPRESSO linha {row_real}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao reimprimir: {e}")

    btn_toggle.config(command=on_toggle)
    btn_refresh.config(command=on_refresh)
    btn_reprint.config(command=on_reprint)

    def on_close():
        worker.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    process_ui_queue()
    root.mainloop()


# =========================
# MAIN
# =========================
def main():
    # 1) config
    cfg = carregar_config()
    if not cfg:
        tela_config_inicial()
        cfg = carregar_config()

    if not cfg:
        print("Config não encontrada. Saindo.")
        return

    planilha_id = cfg.get("PLANILHA_ID", "").strip()
    impressora = cfg.get("IMPRESSORA", "").strip()

    if not planilha_id or not impressora:
        messagebox.showerror("Erro", "Config inválida. Apague o config.json e execute novamente.")
        return

    # 2) credenciais
    json_path = os.path.join(app_dir(), JSON_FILE)
    if not os.path.exists(json_path):
        messagebox.showerror(
            "Erro",
            f"Arquivo JSON do Google não encontrado:\n{json_path}\n\nColoque o JSON na mesma pasta do programa.",
        )
        return

    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, SCOPE)
    client = gspread.authorize(creds)

    # 3) planilha
    sheet = client.open_by_key(planilha_id).sheet1

    # 4) painel
    abrir_painel(sheet, impressora)


if __name__ == "__main__":
    main()
