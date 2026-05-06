from datetime import datetime
from fractions import Fraction
from io import BytesIO
from xml.sax.saxutils import escape

import numpy as np
import streamlit as st

from logica.grafico import generar_grafica_plotly, resolver_grafico
from logica.simplex import extraer_solucion, resolver_simplex


st.set_page_config(
    page_title="Programación Lineal - UNISTMO",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def css(modo_claro=False):
    css_modo_claro = """
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"],
        .block-container {
            background:#f4f6fa!important;
            color:#1f2937!important;
        }
        [data-testid="stHeader"] {
            background:rgba(244,246,250,.92)!important;
        }
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"] {
            background:#ffffff!important;
            color:#1f2937!important;
        }
        .pl-header, .card, [data-testid="stExpander"] {
            background:#ffffff!important;
            border-color:#e5e7eb!important;
            box-shadow:0 2px 18px rgba(30,41,59,.08)!important;
        }
        .pl-sub, .ibox, .interp, .fbox, .pl-tbl, .vtx-tbl,
        .stMarkdown, .stMarkdown p, .stMarkdown li, label,
        [data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] {
            color:#1f2937!important;
        }
        .ibox, .interp { background:#eff6ff!important; border-color:#bfdbfe!important; }
        .fbox { background:#f8f7ff!important; border-color:#c4b5fd!important; }
        .fs, .sec-lbl, .m-lbl { color:#6b7280!important; }
        .m-card { background:#f8fafc!important; border-color:#e5e7eb!important; }
        .pl-tbl td, .vtx-tbl td { border-color:#e5e7eb!important; }
        .pl-tbl th, .vtx-tbl th {
            background:#ede9fe!important;
            color:#5b21b6!important;
            border-color:#ddd6fe!important;
        }
        [data-testid="stExpander"] summary {
            background:#ede9fe!important;
            color:#4c1d95!important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background:#ffffff!important;
            border-color:#e5e7eb!important;
        }
        .stTabs [data-baseweb="tab"] { color:#475569!important; }
        .stTabs [aria-selected="true"] { color:#ffffff!important; }
        [data-baseweb="input"],
        [data-baseweb="select"],
        [data-baseweb="base-input"],
        [data-baseweb="popover"],
        textarea {
            background:#ffffff!important;
            color:#111827!important;
            border-color:#cbd5e1!important;
        }
        input, textarea, [contenteditable="true"] {
            color:#111827!important;
            caret-color:#111827!important;
        }
        div[style*="background:#111827"],
        div[style*="background:#0f172a"] {
            background:#ffffff!important;
            color:#111827!important;
            border-color:#e5e7eb!important;
        }
        div[style*="background:#1f2937"] {
            background:#eef2ff!important;
            color:#1f2937!important;
        }
        div[style*="color:white"] { color:#1f2937!important; }
    """ if modo_claro else ""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
        *, html, body, [class*="css"] { font-family: 'Nunito', sans-serif; box-sizing: border-box; }
        .stApp { background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e); }
        .pl-header {
            display:flex; align-items:center; justify-content:space-between; gap:18px;
            padding:18px 24px; margin-bottom:14px; border:1px solid rgba(167,139,250,.25);
            border-radius:14px; background:rgba(22,20,50,.78); box-shadow:0 8px 30px rgba(0,0,0,.26);
        }
        .pl-title {
            font-size:1.7rem; font-weight:800;
            background:linear-gradient(90deg,#c4b5fd,#60a5fa,#22d3ee);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        }
        .pl-sub { color:rgba(255,255,255,.62); font-size:.84rem; }
        .pl-badge {
            color:white; padding:7px 16px; border-radius:999px; white-space:nowrap;
            background:linear-gradient(135deg,#7c3aed,#2563eb); font-size:.78rem; font-weight:800;
        }
        .card, [data-testid="stExpander"] {
            background:rgba(22,20,50,.78)!important; border:1px solid rgba(167,139,250,.23)!important;
            border-radius:12px!important; box-shadow:0 8px 30px rgba(0,0,0,.22)!important;
        }
        .card { padding:18px 20px; margin-bottom:14px; }
        .card-title {
            color:#c4b5fd; font-weight:800; font-size:.78rem; letter-spacing:.8px;
            text-transform:uppercase; margin-bottom:12px;
        }
        .ibox, .interp {
            background:rgba(96,165,250,.10); border:1px solid rgba(96,165,250,.24);
            border-radius:10px; color:rgba(255,255,255,.9); padding:13px 16px; line-height:1.65;
            margin-bottom:14px; font-size:.92rem;
        }
        .fbox {
            background:rgba(15,12,41,.72); border:1px solid rgba(167,139,250,.28);
            border-radius:10px; padding:12px 15px; color:rgba(255,255,255,.92); line-height:1.9;
        }
        .fo { color:#4ade80; font-weight:800; }
        .fr { color:#60a5fa; }
        .fs { color:rgba(255,255,255,.55); font-size:.82rem; }
        .fnn { color:#c4b5fd; }
        .sec-lbl {
            color:rgba(255,255,255,.5); font-size:.74rem; font-weight:800; letter-spacing:.7px;
            text-transform:uppercase; margin:8px 0 3px;
        }
        .metric-row { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:16px; }
        .m-card {
            flex:1; min-width:96px; padding:13px 10px; text-align:center; border-radius:12px;
            background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.08);
        }
        .m-lbl { color:rgba(255,255,255,.55); font-size:.68rem; text-transform:uppercase; letter-spacing:.9px; }
        .m-val { font-size:1.55rem; font-weight:800; }
        .mg { color:#4ade80; } .mb { color:#60a5fa; } .mp { color:#c4b5fd; } .ma { color:#fbbf24; }
        .pl-tbl, .vtx-tbl { width:100%; border-collapse:collapse; color:rgba(255,255,255,.88); font-size:.86rem; }
        .pl-tbl th, .vtx-tbl th {
            background:rgba(124,58,237,.23); color:#c4b5fd; padding:9px 12px;
            border:1px solid rgba(167,139,250,.25); font-weight:800;
        }
        .pl-tbl td, .vtx-tbl td { padding:9px 12px; border:1px solid rgba(255,255,255,.08); text-align:center; }
        .vtx-tbl td:first-child, .vtx-tbl th:first-child { text-align:left; }
        .rz td { background:rgba(22,163,74,.12); color:#4ade80; font-weight:800; }
        .pvc { background:rgba(217,119,6,.22)!important; color:#fbbf24!important; font-weight:800; }
        .pvc2 { background:rgba(217,119,6,.44)!important; outline:2px solid #f59e0b; color:#fff7ed!important; font-weight:900; }
        .opt-row td { background:rgba(22,163,74,.12); }
        [data-testid="stExpander"] summary { background:rgba(124,58,237,.22)!important; color:#ddd6fe!important; font-weight:800!important; }
        .stButton > button, .stDownloadButton > button {
            background:linear-gradient(135deg,#7c3aed,#2563eb)!important; color:#fff!important; border:0!important;
            border-radius:12px!important; font-weight:800!important; width:100%!important; padding:12px 18px!important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:4px;
        }
        .stTabs [data-baseweb="tab"] { border-radius:9px; color:rgba(255,255,255,.72); font-weight:800; }
        .stTabs [aria-selected="true"] { background:linear-gradient(135deg,#7c3aed,#2563eb)!important; color:#fff!important; }
        footer { visibility:hidden; }
        @media (prefers-color-scheme: light) {
            .stApp { background:#f4f6fa; }
            .pl-header, .card, [data-testid="stExpander"] { background:#fff!important; border-color:#e5e7eb!important; box-shadow:0 2px 18px rgba(30,41,59,.08)!important; }
            .pl-sub, .ibox, .interp, .fbox, .pl-tbl, .vtx-tbl { color:#1f2937; }
            .ibox, .interp { background:#eff6ff; border-color:#bfdbfe; }
            .fbox { background:#f8f7ff; border-color:#c4b5fd; }
            .fs, .sec-lbl, .m-lbl { color:#6b7280; }
            .m-card { background:#f8fafc; border-color:#e5e7eb; }
            .pl-tbl td, .vtx-tbl td { border-color:#e5e7eb; }
        }
        __CSS_MODO_CLARO__
        </style>
        """.replace("__CSS_MODO_CLARO__", css_modo_claro),
        unsafe_allow_html=True,
    )


def metric_row(items):
    cards = "".join(
        f'<div class="m-card"><div class="m-lbl">{label}</div><div class="m-val {color}">{value}</div></div>'
        for label, value, color in items
    )
    return f'<div class="metric-row">{cards}</div>'


def fmt_num(valor, fracciones=False):
    if fracciones:
        frac = valor if isinstance(valor, Fraction) else Fraction(str(float(valor))).limit_denominator(10_000)
        return str(frac.numerator) if frac.denominator == 1 else f"{frac.numerator}/{frac.denominator}"
    return round(float(valor), 4)


def _partes_restriccion(restriccion):
    if len(restriccion) == 2:
        fila, b = restriccion
        return fila, "<=", b
    if len(restriccion) == 3 and not isinstance(restriccion[1], str):
        a1, a2, b = restriccion
        return [a1, a2], "<=", b
    fila, sentido, b = restriccion
    return fila, sentido, b


def validar_grafico(c1, c2, restricciones):
    avisos = []
    if abs(c1) < 1e-9 and abs(c2) < 1e-9:
        avisos.append("⚠️ La función objetivo tiene todos sus coeficientes en 0. Cambia al menos uno para que Z tenga sentido.")
    for i, restriccion in enumerate(restricciones, start=1):
        fila, _, b = _partes_restriccion(restriccion)
        a1, a2 = fila
        if abs(a1) < 1e-9 and abs(a2) < 1e-9:
            avisos.append(f"⚠️ Revisa la restricción {i}: x1 y x2 no pueden tener ambos coeficientes en 0.")
        if False and b < 0:
            avisos.append(f"⚠️ Revisa la restricción {i}: el lado derecho (b) no puede ser negativo en esta app.")
    return avisos


def validar_simplex(c, restricciones):
    avisos = []
    if all(abs(ci) < 1e-9 for ci in c):
        avisos.append("⚠️ La función objetivo tiene todos sus coeficientes en 0. Cambia al menos uno para poder optimizar.")
    for j, restriccion in enumerate(restricciones, start=1):
        fila, _, b = _partes_restriccion(restriccion)
        if all(abs(aij) < 1e-9 for aij in fila):
            avisos.append(f"⚠️ Revisa la restricción {j}: todos los coeficientes están en 0.")
        if False and b < 0:
            avisos.append(f"⚠️ Revisa la restricción {j}: el lado derecho (b) no puede ser negativo para este Simplex.")
    return avisos


def tabla_simplex_html(tabla, encab, etiq, pcol=-1, prow=-1, destacar=True, fracciones=False):
    eh = "".join(f"<th>{h}</th>" for h in encab)
    filas = ""
    for ri, (et, fila) in enumerate(zip(etiq, tabla)):
        es_z = ri == len(etiq) - 1
        rk = 'class="rz"' if es_z else ""
        celdas = ""
        for ci, val in enumerate(fila):
            clase = ""
            if destacar and ci == pcol and not es_z:
                clase = "pvc2" if ri == prow else "pvc"
            celdas += f'<td class="{clase}">{fmt_num(val, fracciones)}</td>'
        filas += f"<tr {rk}><th style='text-align:left'>{et}</th>{celdas}</tr>"
    return f"<div style='overflow-x:auto'><table class='pl-tbl'><thead><tr><th style='text-align:left'>Base</th>{eh}</tr></thead><tbody>{filas}</tbody></table></div>"


def pivote_de_tabla(tabla):
    fila_z = [float(v) for v in tabla[-1, :-1]]
    if not any(v < -1e-9 for v in fila_z):
        return -1, -1, []
    pcol = int(np.argmin(fila_z))
    rhs = [float(v) for v in tabla[:-1, -1]]
    col = [float(v) for v in tabla[:-1, pcol]]
    razones = [rhs[i] / col[i] if col[i] > 1e-9 else np.inf for i in range(len(rhs))]
    prow = int(np.argmin(razones)) if not all(r == np.inf for r in razones) else -1
    return pcol, prow, razones


def _limpiar_pdf(texto):
    return (
        str(texto)
        .replace("≤", "<=")
        .replace("≥", ">=")
        .replace("·", "-")
        .replace("ó", "o")
        .replace("Ó", "O")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ú", "u")
        .replace("ñ", "n")
    )


def _escapar_pdf(texto):
    texto = _limpiar_pdf(texto)
    return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))


def _pdf_color(hex_color, stroke=False):
    r, g, b = _rgb(hex_color)
    return f"{r:.3f} {g:.3f} {b:.3f} {'RG' if stroke else 'rg'}"


def _pdf_texto(cmds, texto, x, y, size=9, bold=False, color="#111827"):
    font = "F2" if bold else "F1"
    cmds.append(_pdf_color(color))
    cmds.append(f"BT /{font} {size} Tf {x} {y} Td ({_escapar_pdf(texto)}) Tj ET")


def _pdf_rect(cmds, x, y, w, h, fill="#ffffff", stroke=None, line_width=0.8):
    if fill:
        cmds.append(_pdf_color(fill))
        cmds.append(f"{x} {y} {w} {h} re f")
    if stroke:
        cmds.append(_pdf_color(stroke, stroke=True))
        cmds.append(f"{line_width} w {x} {y} {w} {h} re S")


def _pdf_wrap(texto, chars=82):
    texto = _limpiar_pdf(texto)
    partes, linea = [], ""
    for palabra in texto.split():
        if len(linea) + len(palabra) + 1 > chars:
            partes.append(linea)
            linea = palabra
        else:
            linea = f"{linea} {palabra}".strip()
    if linea:
        partes.append(linea)
    return partes or [""]


def _pdf_diseno(titulo, objetivo, restricciones, resultado, metodo, tablas=None, grafica=None, interpretacion=None):
    width, height = 612, 792
    margin = 42
    content_w = width - margin * 2
    paginas = []
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    def nueva_pagina():
        cmds = []
        _pdf_rect(cmds, 0, 0, width, height, fill="#f8fafc")
        _pdf_rect(cmds, 0, height - 96, width, 96, fill="#312e81")
        _pdf_rect(cmds, 0, height - 102, width, 6, fill="#7c3aed")
        _pdf_texto(cmds, titulo, margin, height - 48, 18, True, "#ffffff")
        _pdf_texto(cmds, f"{metodo}  |  {fecha}", margin, height - 68, 9, False, "#ddd6fe")
        _pdf_texto(cmds, "Programacion Lineal", width - 174, height - 48, 9, True, "#ffffff")
        paginas.append(cmds)
        return cmds, height - 132

    cmds, y = nueva_pagina()

    def asegurar(altura=40):
        nonlocal cmds, y
        if y - altura < 56:
            cmds, y = nueva_pagina()

    def seccion(nombre):
        nonlocal y
        asegurar(34)
        _pdf_texto(cmds, nombre.upper(), margin, y, 10, True, "#4f46e5")
        _pdf_rect(cmds, margin, y - 8, content_w, 1.2, fill="#c7d2fe")
        y -= 24

    def parrafo(texto, caja=False):
        nonlocal y
        lineas = _pdf_wrap(texto, 86)
        alto = 20 + len(lineas) * 12 if caja else len(lineas) * 13
        asegurar(alto + 8)
        if caja:
            _pdf_rect(cmds, margin, y - alto + 10, content_w, alto, fill="#eef2ff", stroke="#c7d2fe")
            tx, ty = margin + 12, y - 8
        else:
            tx, ty = margin, y
        for linea in lineas:
            _pdf_texto(cmds, linea, tx, ty, 9, False, "#1f2937")
            ty -= 12
        y -= alto + 6

    def tabla(titulo_tabla, columnas, filas):
        nonlocal y
        seccion(titulo_tabla)
        if not columnas:
            return
        n_cols = len(columnas)
        col_w = content_w / n_cols
        font_size = 7 if n_cols <= 6 else 5.6
        row_h = 22

        def dibujar_fila(valores, header=False, idx=0):
            nonlocal y
            asegurar(row_h + 12)
            fill = "#312e81" if header else ("#ffffff" if idx % 2 == 0 else "#f1f5f9")
            txt = "#ffffff" if header else "#111827"
            _pdf_rect(cmds, margin, y - row_h + 5, content_w, row_h, fill=fill, stroke="#cbd5e1", line_width=0.45)
            for c, valor in enumerate(valores):
                x = margin + c * col_w
                if c > 0:
                    _pdf_rect(cmds, x, y - row_h + 5, 0.45, row_h, fill="#cbd5e1")
                limpio = _limpiar_pdf(valor)
                max_chars = max(5, int(col_w / (font_size * 0.48)))
                if len(limpio) > max_chars:
                    limpio = limpio[: max_chars - 1] + "."
                _pdf_texto(cmds, limpio, x + 5, y - 10, font_size, header, txt)
            y -= row_h

        dibujar_fila(columnas, header=True)
        for idx, fila in enumerate(filas):
            dibujar_fila([str(v) for v in fila], idx=idx)
        y -= 8

    def puntos_vertices():
        for datos in tablas or []:
            columnas = [str(c).lower() for c in datos.get("columnas", [])]
            if "vertice" not in columnas:
                continue
            idx_v = columnas.index("vertice")
            idx_z = columnas.index("z") if "z" in columnas else -1
            idx_r = columnas.index("resultado") if "resultado" in columnas else -1
            puntos = []
            for fila in datos.get("filas", []):
                try:
                    texto = str(fila[idx_v]).strip().strip("()")
                    x_txt, y_txt = texto.split(",", 1)
                    z_val = fila[idx_z] if idx_z >= 0 else ""
                    es_opt = idx_r >= 0 and "opt" in str(fila[idx_r]).lower()
                    puntos.append((float(x_txt), float(y_txt), z_val, es_opt))
                except Exception:
                    continue
            return puntos
        return []

    def grafica_vertices():
        nonlocal y
        puntos = puntos_vertices()
        if not puntos:
            parrafo("La grafica se muestra en la app. Para incrustar la imagen exacta en el PDF instala kaleido junto con reportlab.", caja=True)
            return
        asegurar(230)
        chart_x, chart_y, chart_w, chart_h = margin, y - 205, content_w, 205
        plot_x, plot_y, plot_w, plot_h = chart_x + 46, chart_y + 42, chart_w - 74, chart_h - 72
        _pdf_rect(cmds, chart_x, chart_y, chart_w, chart_h, fill="#ffffff", stroke="#cbd5e1")
        _pdf_texto(cmds, "Vertices factibles y punto optimo", chart_x + 14, chart_y + chart_h - 24, 10, True, "#1e1b4b")
        _pdf_rect(cmds, plot_x, plot_y, plot_w, plot_h, fill="#f8fafc", stroke="#c7d2fe")
        for i in range(1, 5):
            gx = plot_x + plot_w * i / 5
            gy = plot_y + plot_h * i / 5
            _pdf_rect(cmds, gx, plot_y, 0.4, plot_h, fill="#e2e8f0")
            _pdf_rect(cmds, plot_x, gy, plot_w, 0.4, fill="#e2e8f0")
        max_x = max([p[0] for p in puntos] + [1])
        max_y = max([p[1] for p in puntos] + [1])
        max_x = max_x if max_x > 0 else 1
        max_y = max_y if max_y > 0 else 1
        _pdf_texto(cmds, "x1", plot_x + plot_w - 8, plot_y - 18, 8, True, "#475569")
        _pdf_texto(cmds, "x2", plot_x - 28, plot_y + plot_h + 2, 8, True, "#475569")
        _pdf_texto(cmds, "0", plot_x - 9, plot_y - 14, 7, False, "#64748b")
        _pdf_texto(cmds, str(round(max_x, 2)), plot_x + plot_w - 18, plot_y - 14, 7, False, "#64748b")
        _pdf_texto(cmds, str(round(max_y, 2)), plot_x - 34, plot_y + plot_h - 2, 7, False, "#64748b")
        for x_val, y_val, z_val, es_opt in puntos:
            px = plot_x + (x_val / max_x) * (plot_w - 8)
            py = plot_y + (y_val / max_y) * (plot_h - 8)
            color = "#f59e0b" if es_opt else "#4f46e5"
            size = 8 if es_opt else 6
            _pdf_rect(cmds, px - size / 2, py - size / 2, size, size, fill=color, stroke="#ffffff", line_width=0.6)
            etiqueta = f"({round(x_val, 2)}, {round(y_val, 2)})"
            if es_opt:
                etiqueta += f"  Z={z_val}"
            _pdf_texto(cmds, etiqueta, px + 6, py + 5, 6.5, es_opt, "#334155")
        y -= chart_h + 18

    seccion("Modelo")
    parrafo(objetivo, caja=True)

    seccion("Restricciones")
    for restriccion in restricciones:
        parrafo(f"- {restriccion}")

    tabla("Resumen del resultado", ["Concepto", "Valor"], [[k, v] for k, v in resultado.items()])

    if grafica is not None:
        seccion("Grafica")
        grafica_vertices()

    for datos in tablas or []:
        tabla(datos.get("titulo", "Tabla"), [str(c) for c in datos.get("columnas", [])], datos.get("filas", []))

    if interpretacion:
        seccion("Interpretacion")
        parrafo(interpretacion, caja=True)

    objetos = ["<< /Type /Catalog /Pages 2 0 R >>"]
    kids = []
    for idx, pagina_cmds in enumerate(paginas):
        page_obj = 3 + idx * 2
        content_obj = page_obj + 1
        kids.append(f"{page_obj} 0 R")
        stream = "\n".join(pagina_cmds).encode("latin-1", errors="replace")
        objetos.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> /F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> >> >> /Contents {content_obj} 0 R >>")
        objetos.append(f"<< /Length {len(stream)} >>\nstream\n{stream.decode('latin-1')}\nendstream")

    objetos.insert(1, f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(paginas)} >>")
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objetos, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n{obj}\nendobj\n".encode("latin-1", errors="replace"))
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode("ascii"))
    return bytes(pdf)


def _texto_pdf(valor):
    return _limpiar_pdf(valor)


def _tabla_pdf(datos):
    columnas = [_texto_pdf(c) for c in datos.get("columnas", [])]
    filas = datos.get("filas", [])
    return [columnas] + [[_texto_pdf(c) for c in fila] for fila in filas]


def _imagen_plotly(fig):
    if fig is None:
        return None
    try:
        return BytesIO(fig.to_image(format="png", width=1000, height=650, scale=2))
    except Exception:
        return None


def generar_reporte(nombre, objetivo, restricciones, resultado, metodo, tablas=None, grafica=None, interpretacion=None):
    lineas = [
        "Reporte de Programación Lineal",
        f"Método: {metodo}",
        f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "Modelo",
        objetivo,
        "Sujeto a:",
        *[f"- {r}" for r in restricciones],
        "",
        "Resultado",
        *[f"- {k}: {v}" for k, v in resultado.items()],
    ]
    for datos in tablas or []:
        lineas.extend(["", datos.get("titulo", "Tabla")])
        columnas = [str(c) for c in datos.get("columnas", [])]
        if columnas:
            lineas.append(" | ".join(columnas))
            lineas.append("-" * min(92, max(12, len(lineas[-1]))))
        for fila in datos.get("filas", []):
            lineas.append(" | ".join(str(c) for c in fila))
    if grafica is not None:
        lineas.extend(["", "Grafica", "La grafica se incluye cuando esta disponible el exportador de imagenes de Plotly."])
    if interpretacion:
        lineas.extend(["", "Interpretacion", interpretacion])
    texto = "\n".join(lineas)

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="TituloPL", parent=styles["Title"], textColor=colors.HexColor("#1e1b4b"), fontSize=20, leading=24, alignment=TA_CENTER, spaceAfter=8))
        styles.add(ParagraphStyle(name="SubtituloPL", parent=styles["Normal"], textColor=colors.HexColor("#475569"), fontSize=9, leading=12, alignment=TA_CENTER, spaceAfter=18))
        styles.add(ParagraphStyle(name="SeccionPL", parent=styles["Heading2"], textColor=colors.HexColor("#4f46e5"), fontSize=12, leading=15, spaceBefore=10, spaceAfter=7))
        styles.add(ParagraphStyle(name="TextoPL", parent=styles["Normal"], textColor=colors.HexColor("#1f2937"), fontSize=9, leading=13))
        styles.add(ParagraphStyle(name="CajaPL", parent=styles["Normal"], textColor=colors.HexColor("#111827"), backColor=colors.HexColor("#eef2ff"), borderColor=colors.HexColor("#c7d2fe"), borderWidth=0.8, borderPadding=8, fontSize=9, leading=13, spaceAfter=8))

        elementos = [
            Paragraph(escape(_texto_pdf(nombre)), styles["TituloPL"]),
            Paragraph(escape(_texto_pdf(f"{metodo} | {datetime.now().strftime('%d/%m/%Y %H:%M')}")), styles["SubtituloPL"]),
            Paragraph("Modelo", styles["SeccionPL"]),
            Paragraph(escape(_texto_pdf(objetivo)), styles["CajaPL"]),
            Paragraph("Restricciones", styles["SeccionPL"]),
        ]
        for restriccion in restricciones:
            elementos.append(Paragraph(escape(_texto_pdf(f"- {restriccion}")), styles["TextoPL"]))

        elementos.extend([Spacer(1, 8), Paragraph("Resumen del resultado", styles["SeccionPL"])])
        resumen = [["Concepto", "Valor"]] + [[_texto_pdf(k), _texto_pdf(v)] for k, v in resultado.items()]
        tabla_resumen = Table(resumen, colWidths=[180, 300], hAlign="LEFT")
        tabla_resumen.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
            ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#cbd5e1")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        elementos.append(tabla_resumen)

        imagen = _imagen_plotly(grafica)
        if imagen is not None:
            elementos.extend([Spacer(1, 12), Paragraph("Grafica", styles["SeccionPL"])])
            elementos.append(Image(imagen, width=500, height=325))

        for datos in tablas or []:
            elementos.extend([Spacer(1, 12), Paragraph(escape(_texto_pdf(datos.get("titulo", "Tabla"))), styles["SeccionPL"])])
            tabla = Table(_tabla_pdf(datos), repeatRows=1, hAlign="LEFT")
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#312e81")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.6),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]))
            elementos.append(tabla)

        if interpretacion:
            elementos.extend([Spacer(1, 12), Paragraph("Interpretacion", styles["SeccionPL"]), Paragraph(escape(_texto_pdf(interpretacion)), styles["CajaPL"])])

        doc.build(elementos)
        buffer.seek(0)
        return buffer.getvalue(), "application/pdf", "reporte_programacion_lineal.pdf"
    except Exception:
        return _pdf_diseno(nombre, objetivo, restricciones, resultado, metodo, tablas, grafica, interpretacion), "application/pdf", "reporte_programacion_lineal.pdf"


def mostrar_tutorial():
    with st.expander("📖 ¿Cómo usar esta app? Haz clic aquí", expanded=False):
        c1, c2 = st.columns([1.15, 1])
        with c1:
            st.markdown(
                """
                **Pasos rápidos**

                1. Elige si quieres **maximizar** o **minimizar**.
                2. Escribe los coeficientes de la función objetivo, por ejemplo `3x1 + 2x2`.
                3. Agrega las restricciones con su lado derecho `b`.
                4. Presiona **Resolver problema**.
                5. Revisa la gráfica, la tabla o mueve el slider del Simplex para avanzar paso a paso.
                6. Descarga el reporte para entregar tu evidencia.
                """
            )
            st.markdown(
                """
                <div style="border:1px solid rgba(255,255,255,.14);border-radius:12px;overflow:hidden;background:#111827;margin-top:12px">
                  <div style="padding:9px 12px;background:#1f2937;color:white;font-weight:800">Captura guía 1 · Captura el modelo</div>
                  <div style="padding:14px;display:grid;gap:10px;color:white">
                    <div style="height:34px;border-radius:8px;background:#312e81;padding:7px 10px">Función objetivo: Max Z = 3x1 + 2x2</div>
                    <div style="height:34px;border-radius:8px;background:#0f766e;padding:7px 10px">Restricción 1: x1 + x2 ≤ 4</div>
                    <div style="height:34px;border-radius:8px;background:#0f766e;padding:7px 10px">Restricción 2: x1 + 2x2 ≤ 6</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                """
                <div style="height:315px;border-radius:12px;overflow:hidden;background:#0f172a;border:1px solid rgba(255,255,255,.14);position:relative;color:white;font-family:Nunito,Arial">
                  <div style="padding:12px 14px;background:#111827;font-weight:800">Mini video: de modelo a solución</div>
                  <div style="position:absolute;left:36px;top:78px;width:250px;height:120px;border:2px solid #60a5fa;border-radius:10px;padding:12px;animation:pulse 2s infinite">
                    Max Z = 3x1 + 2x2<br>R1: x1 + x2 <= 4<br>R2: x1 + 2x2 <= 6
                  </div>
                  <div style="position:absolute;right:34px;bottom:42px;width:210px;height:120px;border:2px solid #4ade80;border-radius:10px;padding:12px;background:rgba(34,197,94,.10)">
                    Óptimo<br><span style="font-size:28px;font-weight:900">Z = 12</span><br>x1 = 4, x2 = 0
                  </div>
                  <div style="position:absolute;left:310px;top:150px;font-size:34px;color:#fbbf24;animation:move 2.2s infinite">→</div>
                </div>
                <style>
                @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.04)} }
                @keyframes move { 0%{transform:translateX(0);opacity:.35} 50%{transform:translateX(24px);opacity:1} 100%{transform:translateX(0);opacity:.35} }
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div style="border:1px solid rgba(255,255,255,.14);border-radius:12px;overflow:hidden;background:#111827;margin-top:12px">
                  <div style="padding:9px 12px;background:#1f2937;color:white;font-weight:800">Captura guía 2 · Interpreta resultados</div>
                  <div style="padding:14px;color:white">
                    <div style="height:120px;border-radius:10px;background:linear-gradient(135deg,#1d4ed8,#6d28d9);display:flex;align-items:center;justify-content:center;font-weight:900">Gráfica + línea de nivel</div>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:10px">
                      <div style="background:#064e3b;border-radius:8px;padding:8px;text-align:center">x1 = 4</div>
                      <div style="background:#064e3b;border-radius:8px;padding:8px;text-align:center">x2 = 0</div>
                      <div style="background:#92400e;border-radius:8px;padding:8px;text-align:center">Z = 12</div>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


with st.sidebar:
    st.markdown("### Apariencia")
    tema_app = st.radio(
        "Modo",
        ["Oscuro", "Claro"],
        horizontal=True,
        key="tema_app",
        help="Cambia el fondo y los componentes principales de la app.",
    )

modo_claro = tema_app == "Claro"
css(modo_claro)

st.markdown(
    """
    <div class="pl-header">
      <div style="display:flex;align-items:center;gap:14px">
        <div style="background:linear-gradient(135deg,#7c3aed,#2563eb);border-radius:12px;padding:10px;font-size:1.35rem">📐</div>
        <div>
          <div class="pl-title">Programación Lineal</div>
          <div class="pl-sub">Universidad del Istmo · Investigación de Operaciones · Clave 8085</div>
        </div>
      </div>
      <div class="pl-badge">v1.0 · Streamlit + Plotly</div>
    </div>
    """,
    unsafe_allow_html=True,
)

mostrar_tutorial()

tab1, tab2, tab3 = st.tabs(
    ["📊 Método Gráfico (2 variables)", "📋 Método Simplex (N variables)", "📚 Glosario"]
)


with tab1:
    st.markdown(
        """
        <div class="ibox">
          <strong>Método Gráfico:</strong> representa las restricciones como rectas en el plano.
          La solución óptima se encuentra en un vértice de la región factible. La línea naranja
          muestra la línea de nivel de la función objetivo cuando toca el punto óptimo.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_izq, col_der = st.columns([1, 1.65], gap="large")
    with col_izq:
        st.markdown('<div class="card"><div class="card-title">⚡ Función Objetivo</div>', unsafe_allow_html=True)
        tipo = st.radio(
            "Objetivo",
            ["Maximizar", "Minimizar"],
            horizontal=True,
            key="g_tipo",
            label_visibility="collapsed",
            help="Indica si quieres encontrar el valor más grande o más pequeño de Z.",
        )
        maximizar = tipo == "Maximizar"
        c1c, c2c = st.columns(2)
        c1 = c1c.number_input("Coef. x1", value=3.0, key="g_c1", step=1.0, help="Coeficiente de x1 en Z. Ej: si ganas $3 por unidad, pon 3.")
        c2 = c2c.number_input("Coef. x2", value=2.0, key="g_c2", step=1.0, help="Coeficiente de x2 en Z. Ej: si ganas $2 por unidad, pon 2.")
        tipo_s = "Max" if maximizar else "Min"
        st.markdown(f'<div class="fbox"><span class="fs">Función objetivo</span><br><span class="fo">{tipo_s} Z = {c1}x1 + {c2}x2</span></div></div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">🔒 Restricciones</div>', unsafe_allow_html=True)
        n_r = int(st.number_input("Número de restricciones", min_value=1, max_value=8, value=2, step=1, key="g_nr", help="Cantidad de condiciones o límites del problema."))
        restricciones, frests = [], []
        for i in range(n_r):
            st.markdown(f'<div class="sec-lbl">Restricción {i + 1}</div>', unsafe_allow_html=True)
            ca, cb, cs, cc = st.columns([1, 1, 0.8, 1])
            a1 = ca.number_input("x1", value=1.0, key=f"ga1_{i}", step=1.0, help=f"Coeficiente de x1 en la restricción {i + 1}.")
            a2 = cb.number_input("x2", value=1.0, key=f"ga2_{i}", step=1.0, help=f"Coeficiente de x2 en la restricción {i + 1}.")
            b = cc.number_input("b", value=4.0 if i == 0 else 6.0, key=f"gb_{i}", step=1.0, help="Lado derecho de la restriccion.")
            sentido = cs.selectbox("Sentido", ["<=", ">=", "="], key=f"gs_{i}", help="Tipo de desigualdad de esta restriccion.")
            restricciones.append(([a1, a2], sentido, b))
            frests.append(f"{a1}x1 + {a2}x2 {sentido} {b}")

        rh = "".join(f'<span class="fr">&nbsp;&nbsp;&nbsp;{r}</span><br>' for r in frests)
        objetivo_g = f"{tipo_s} Z = {c1}x1 + {c2}x2"
        st.markdown(f'<div class="fbox" style="margin-top:10px"><span class="fs">Planteamiento completo</span><br><span class="fo">{objetivo_g}</span><br><span class="fs">sujeto a:</span><br>{rh}<span class="fnn">&nbsp;&nbsp;&nbsp;x1, x2 ≥ 0</span></div></div>', unsafe_allow_html=True)

        avisos_g = validar_grafico(c1, c2, restricciones)
        for aviso in avisos_g:
            st.warning(aviso)
        resolver = st.button("Resolver problema", key="btn_grafico")

    with col_der:
        if resolver and not avisos_g:
            vertices, resultados, optimo, estado_g, optimos = resolver_grafico(c1, c2, restricciones, maximizar)
            if estado_g == "infactible":
                st.error("No se encontro region factible. Revisa tus restricciones.")
            elif estado_g == "no_acotado":
                st.error("El problema no tiene solucion acotada: la region factible permite mejorar Z indefinidamente.")
            elif not vertices:
                st.error("No se encontró región factible. Revisa tus restricciones.")
            else:
                popt, zopt = optimo
                tipo_lbl = "máximo" if maximizar else "mínimo"
                st.markdown(
                    metric_row([("x1 óptimo", round(popt[0], 4), "mb"), ("x2 óptimo", round(popt[1], 4), "mp"), (f"Z {tipo_lbl.upper()}", round(zopt, 4), "mg")]),
                    unsafe_allow_html=True,
                )
                st.info("La línea naranja punteada es la línea de nivel Z = k desplazada hasta tocar el vértice óptimo.")
                if len(optimos) > 1:
                    st.warning("Hay solucion multiple: mas de un vertice alcanza el mismo valor optimo, por lo que todo el segmento entre ellos tambien es optimo.")
                fig = generar_grafica_plotly(c1, c2, restricciones, vertices, optimo, maximizar, oscuro=not modo_claro, optimos=optimos)
                st.plotly_chart(fig, use_container_width=True, key="g_chart")

                sorted_res = sorted(resultados, key=lambda r: r[1], reverse=maximizar)
                filas = ""
                filas_vertices_reporte = []
                for v, z in sorted_res:
                    es_optimo = any(round(v[0], 4) == round(o[0], 4) and round(v[1], 4) == round(o[1], 4) for o in optimos)
                    cls = 'class="opt-row"' if es_optimo else ""
                    badge = "Óptimo" if es_optimo else ""
                    filas += f"<tr {cls}><td>({round(v[0], 4)}, {round(v[1], 4)})</td><td>{round(z, 4)}</td><td>{badge}</td></tr>"
                    filas_vertices_reporte.append([f"({round(v[0], 4)}, {round(v[1], 4)})", round(z, 4), "Optimo" if es_optimo else ""])
                st.markdown(f'<div class="card"><div class="card-title">📍 Evaluación en todos los vértices</div><div style="overflow-x:auto"><table class="vtx-tbl"><thead><tr><th>Vértice</th><th>Z</th><th>Resultado</th></tr></thead><tbody>{filas}</tbody></table></div></div>', unsafe_allow_html=True)

                holguras = [float(round(b - (fila[0] * popt[0] + fila[1] * popt[1]), 4)) for fila, _, b in restricciones]
                st.markdown(f'<div class="interp"><strong>Interpretación:</strong> El valor {tipo_lbl} de Z es <strong>{round(zopt, 4)}</strong>, alcanzado en <strong>({round(popt[0], 4)}, {round(popt[1], 4)})</strong>. Las holguras son: {", ".join(f"R{i + 1}: {h}" for i, h in enumerate(holguras))}.</div>', unsafe_allow_html=True)

                data, mime, filename = generar_reporte(
                    "Reporte del Método Gráfico",
                    objetivo_g,
                    frests + ["x1, x2 ≥ 0"],
                    {"x1 óptimo": float(round(popt[0], 4)), "x2 óptimo": float(round(popt[1], 4)), "Z óptimo": float(round(zopt, 4)), "Holguras": holguras},
                    "Método Gráfico",
                    tablas=[
                        {"titulo": "Evaluacion en todos los vertices", "columnas": ["Vertice", "Z", "Resultado"], "filas": filas_vertices_reporte},
                        {"titulo": "Holguras por restriccion", "columnas": ["Restriccion", "Holgura"], "filas": [[f"R{i + 1}", h] for i, h in enumerate(holguras)]},
                    ],
                    grafica=fig,
                    interpretacion=f"El valor {tipo_lbl} de Z es {round(zopt, 4)}, alcanzado en ({round(popt[0], 4)}, {round(popt[1], 4)}). Las holguras son: {', '.join(f'R{i + 1}: {h}' for i, h in enumerate(holguras))}.",
                )
                st.download_button("📄 Descargar reporte", data=data, file_name=filename, mime=mime, key="dl_grafico")
        elif resolver and avisos_g:
            st.error("Corrige las advertencias para poder resolver el modelo.")
        else:
            st.markdown('<div class="ibox" style="text-align:center;min-height:260px;display:flex;align-items:center;justify-content:center">Ingresa tu modelo a la izquierda y presiona <strong>&nbsp;Resolver problema&nbsp;</strong>.</div>', unsafe_allow_html=True)


with tab2:
    st.markdown(
        """
        <div class="ibox">
          <strong>Método Simplex:</strong> resuelve problemas con varias variables. En esta versión
          puedes mover el slider para ver una tabla a la vez y entender cómo cambia el pivote.
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_izq2, col_der2 = st.columns([1, 1.65], gap="large")

    with col_izq2:
        st.markdown('<div class="card"><div class="card-title">⚙️ Configuración</div>', unsafe_allow_html=True)
        tipo2 = st.radio("Objetivo", ["Maximizar", "Minimizar"], horizontal=True, key="tipo2", label_visibility="collapsed", help="Elige el tipo de optimización para Z.")
        maximizar2 = tipo2 == "Maximizar"
        sv1, sv2, sv3 = st.columns(3)
        n_vars = int(sv1.number_input("Variables", min_value=2, max_value=8, value=2, step=1, help="Número de variables de decisión: x1, x2, x3, ..."))
        n_rest = int(sv2.number_input("Restricciones", min_value=1, max_value=8, value=2, step=1, help="Número de restricciones del modelo."))
        ver_fracciones = sv3.toggle("Fracciones", value=False, help="Muestra tablas y resultados como fracciones exactas.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">🎯 Función Objetivo</div>', unsafe_allow_html=True)
        c = []
        cols_c = st.columns(n_vars)
        for i in range(n_vars):
            ci = cols_c[i].number_input(f"c{i + 1}·x{i + 1}", value=3.0 if i == 0 else 2.0, key=f"sc_{i}", step=1.0, help=f"Coeficiente de x{i + 1} en la función objetivo.")
            c.append(ci)
        tipo_s2 = "Max" if maximizar2 else "Min"
        obj_str = " + ".join(f"{c[i]}x{i + 1}" for i in range(n_vars))
        objetivo_s = f"{tipo_s2} Z = {obj_str}"
        st.markdown(f'<div class="fbox"><span class="fs">Función objetivo</span><br><span class="fo">{objetivo_s}</span></div></div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">🔒 Restricciones</div>', unsafe_allow_html=True)
        restricciones2, rest_strs = [], []
        for j in range(n_rest):
            st.markdown(f'<div class="sec-lbl">Restricción {j + 1}</div>', unsafe_allow_html=True)
            cols_r = st.columns(n_vars + 2)
            fila, partes = [], []
            for i in range(n_vars):
                aij = cols_r[i].number_input(f"x{i + 1}", value=1.0, key=f"sa_{j}_{i}", step=1.0, help=f"Coeficiente de x{i + 1} en la restricción {j + 1}.")
                fila.append(aij)
                partes.append(f"{aij}x{i + 1}")
            b = cols_r[n_vars + 1].number_input("b", value=4.0 if j == 0 else 6.0, key=f"sb_{j}", step=1.0, help="Lado derecho de la restriccion.")
            sentido = cols_r[n_vars].selectbox("Sentido", ["<=", ">=", "="], key=f"ss_{j}", help="Tipo de desigualdad de esta restriccion.")
            restricciones2.append((fila, sentido, b))
            rest_strs.append(" + ".join(partes) + f" {sentido} {b}")
        vars_nn = ", ".join(f"x{i + 1}" for i in range(n_vars)) + " ≥ 0"
        rh2 = "".join(f'<span class="fr">&nbsp;&nbsp;&nbsp;{r}</span><br>' for r in rest_strs)
        st.markdown(f'<div class="fbox" style="margin-top:10px"><span class="fs">Planteamiento completo</span><br><span class="fo">{objetivo_s}</span><br><span class="fs">sujeto a:</span><br>{rh2}<span class="fnn">&nbsp;&nbsp;&nbsp;{vars_nn}</span></div></div>', unsafe_allow_html=True)

        avisos_s = validar_simplex(c, restricciones2)
        for aviso in avisos_s:
            st.warning(aviso)
        resolver2 = st.button("Resolver problema", key="btn_simplex")

    with col_der2:
        if (resolver2 and not avisos_s) or ("simplex_resultado" in st.session_state):
            if resolver2 and not avisos_s:
                tabla_f, historial, estado, info_simplex = resolver_simplex(c, restricciones2, maximizar2, n_vars, n_rest)
                st.session_state["simplex_resultado"] = (tabla_f, historial, estado, info_simplex, maximizar2, n_vars, n_rest, objetivo_s, rest_strs, vars_nn)
            else:
                tabla_f, historial, estado, info_simplex, maximizar2, n_vars, n_rest, objetivo_s, rest_strs, vars_nn = st.session_state["simplex_resultado"]
            if estado == "no_acotado":
                st.error("El problema no tiene solución acotada.")
            elif estado == "infactible":
                st.error("El problema es infactible: no existe una solucion que cumpla todas las restricciones.")
            else:
                solucion, z_opt = extraer_solucion(tabla_f, n_vars, n_rest, maximizar2, info_simplex.get("base_indices"))
                tipo_lbl2 = "máximo" if maximizar2 else "mínimo"
                cols_map = ["mb", "mp", "ma", "mg"]
                items_m = [(f"x{i + 1}", fmt_num(solucion[i], ver_fracciones), cols_map[i % 4]) for i in range(n_vars)]
                items_m.append((f"Z {tipo_lbl2.upper()}", fmt_num(z_opt, ver_fracciones), "mg"))
                st.markdown(metric_row(items_m), unsafe_allow_html=True)

                encab = info_simplex.get("etiquetas", [f"x{i + 1}" for i in range(n_vars)] + [f"s{i + 1}" for i in range(n_rest)]) + ["RHS"]
                etiq = [f"R{i + 1}" for i in range(n_rest)] + ["Z"]
                st.markdown(f'<div class="card"><div class="card-title">📋 Animación del Simplex · {len(historial) - 1} iteración(es)</div>', unsafe_allow_html=True)
                if len(historial) > 1:
                    k = st.slider("Iteración", 0, len(historial) - 1, len(historial) - 1, help="Mueve el control para ver la tabla inicial y cada iteración del Simplex.")
                else:
                    k = 0
                    st.info("La tabla inicial ya es óptima, por eso no hay iteraciones para recorrer.")
                tabla = historial[k]
                pcol, prow, razones = pivote_de_tabla(tabla)
                titulo = "Tabla inicial" if k == 0 else f"Iteración {k}"
                st.markdown(f"**{titulo}**")
                st.markdown(tabla_simplex_html(tabla, encab, etiq, pcol, prow, destacar=k < len(historial) - 1, fracciones=ver_fracciones), unsafe_allow_html=True)
                pasos = info_simplex.get("pasos", [])
                if k < len(pasos):
                    st.caption(pasos[k]["mensaje"])
                if pcol >= 0 and k < len(historial) - 1:
                    razon_txt = ", ".join("inf" if r == np.inf else str(fmt_num(r, ver_fracciones)) for r in razones)
                    st.caption(f"Columna pivote: {encab[pcol]} · Fila pivote: {etiq[prow]} · Razones: {razon_txt}")
                else:
                    st.success("Esta es la tabla óptima: ya no hay coeficientes negativos en la fila Z.")
                if info_simplex.get("multiples"):
                    st.warning("Hay solucion multiple: existe al menos una variable no basica con costo reducido cero.")
                st.markdown("</div>", unsafe_allow_html=True)

                filas_vars = ""
                filas_vars_reporte = []
                for i, nom in enumerate(encab[:-1]):
                    if nom.startswith("a"):
                        continue
                    tipo_v = "Variable" if nom.startswith("x") else ("Holgura" if nom.startswith("s") else "Exceso")
                    val = solucion[i]
                    estado_v = "Básica" if abs(val) > 1e-9 else "No básica"
                    filas_vars += f"<tr><td>{nom}</td><td>{tipo_v}</td><td>{fmt_num(val, ver_fracciones)}</td><td>{estado_v}</td></tr>"
                    filas_vars_reporte.append([nom, tipo_v, fmt_num(val, ver_fracciones), "Basica" if abs(val) > 1e-9 else "No basica"])
                st.markdown(f'<div class="card"><div class="card-title">📊 Variables en la solución óptima</div><div style="overflow-x:auto"><table class="vtx-tbl"><thead><tr><th>Variable</th><th>Tipo</th><th>Valor</th><th>Estado</th></tr></thead><tbody>{filas_vars}</tbody></table></div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="interp"><strong>Interpretación:</strong> El valor {tipo_lbl2} de Z es <strong>{fmt_num(z_opt, ver_fracciones)}</strong>, alcanzado en <strong>{len(historial) - 1} iteración(es)</strong>. Las variables de holgura con valor 0 señalan restricciones activas.</div>', unsafe_allow_html=True)

                resultado = {f"x{i + 1}": float(round(float(solucion[i]), 4)) for i in range(n_vars)}
                resultado["Z óptimo"] = float(round(float(z_opt), 4))
                resultado["Iteraciones"] = len(historial) - 1
                tabla_optima_reporte = []
                for i, fila in enumerate(tabla_f):
                    etiqueta = etiq[i] if i < len(etiq) else f"Fila {i + 1}"
                    tabla_optima_reporte.append([etiqueta] + [fmt_num(v, ver_fracciones) for v in fila])
                data, mime, filename = generar_reporte(
                    "Reporte del Método Simplex",
                    objetivo_s,
                    rest_strs + [vars_nn],
                    resultado,
                    "Método Simplex",
                    tablas=[
                        {"titulo": "Variables en la solucion optima", "columnas": ["Variable", "Tipo", "Valor", "Estado"], "filas": filas_vars_reporte},
                        {"titulo": "Tabla optima del Simplex", "columnas": ["Base"] + encab, "filas": tabla_optima_reporte},
                    ],
                    interpretacion=f"El valor {tipo_lbl2} de Z es {fmt_num(z_opt, ver_fracciones)}, alcanzado en {len(historial) - 1} iteracion(es). Las variables de holgura con valor 0 senalan restricciones activas.",
                )
                st.download_button("📄 Descargar reporte", data=data, file_name=filename, mime=mime, key="dl_simplex")
        elif resolver2 and avisos_s:
            st.error("Corrige las advertencias para poder resolver el modelo.")
        else:
            st.markdown('<div class="ibox" style="text-align:center;min-height:260px;display:flex;align-items:center;justify-content:center">Captura el modelo y presiona <strong>&nbsp;Resolver problema&nbsp;</strong> para ver el Simplex paso a paso.</div>', unsafe_allow_html=True)


with tab3:
    st.markdown(
        """
        <div class="ibox">
          <strong>Glosario rápido:</strong> definiciones cortas con ejemplos para estudiar antes de entregar la tarea.
        </div>
        """,
        unsafe_allow_html=True,
    )
    terminos = [
        ("Región factible", "Zona del plano donde se cumplen todas las restricciones al mismo tiempo. Ej: si x1 + x2 ≤ 4, todos los puntos debajo de esa recta son candidatos."),
        ("Vértice", "Esquina de la región factible. En programación lineal, el óptimo aparece en uno de estos puntos."),
        ("Función objetivo", "Fórmula que quieres mejorar. Ej: Z = 3x1 + 2x2 si cada x1 aporta 3 y cada x2 aporta 2."),
        ("Línea de nivel", "Recta con el mismo valor de Z. Ej: 3x1 + 2x2 = 12. Se desplaza hasta tocar el mejor vértice."),
        ("Variable de holgura", "Cantidad de recurso que sobra. Si una restricción tiene holgura 0, está justo al límite."),
        ("Pivote", "Número clave que usa Simplex para cambiar de una tabla a la siguiente."),
        ("Columna pivote", "Variable que entra a la base porque puede mejorar Z."),
        ("Fila pivote", "Restricción que marca el límite para avanzar sin romper la factibilidad."),
        ("Solución no acotada", "Caso donde Z puede crecer sin límite porque las restricciones no cierran la región en la dirección de mejora."),
    ]
    cols = st.columns(3)
    for idx, (titulo, definicion) in enumerate(terminos):
        with cols[idx % 3]:
            st.markdown(f'<div class="card"><div class="card-title">{titulo}</div><div style="line-height:1.65">{definicion}</div></div>', unsafe_allow_html=True)
