from itertools import combinations

import numpy as np
import plotly.graph_objects as go
from scipy.optimize import linprog
from scipy.spatial import ConvexHull


EPS = 1e-9


def _normalizar_restriccion(restriccion):
    if len(restriccion) == 3 and not isinstance(restriccion[1], str):
        a1, a2, b = restriccion
        sentido = "<="
    else:
        fila, sentido, b = restriccion
        a1, a2 = fila
    return float(a1), float(a2), sentido, float(b)


def _cumple(a1, a2, sentido, b, x1, x2):
    valor = a1 * x1 + a2 * x2
    if sentido == "<=":
        return valor <= b + EPS
    if sentido == ">=":
        return valor >= b - EPS
    return abs(valor - b) <= 1e-7


def calcular_vertices(restricciones):
    restricciones = [_normalizar_restriccion(r) for r in restricciones]
    rectas = [(a1, a2, b) for a1, a2, _, b in restricciones]
    rectas.extend([(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)])

    candidatos = []
    for (a1, a2, b), (c1, c2, d) in combinations(rectas, 2):
        A = np.array([[a1, a2], [c1, c2]], dtype=float)
        if abs(np.linalg.det(A)) > EPS:
            p = np.linalg.solve(A, [b, d])
            candidatos.append(tuple(p))

    factibles = []
    for x1, x2 in candidatos:
        if x1 < -EPS or x2 < -EPS:
            continue
        if all(_cumple(a1, a2, sentido, b, x1, x2) for a1, a2, sentido, b in restricciones):
            factibles.append((round(max(0.0, x1), 6), round(max(0.0, x2), 6)))
    return sorted(set(factibles))


def _matrices_linprog(restricciones):
    a_ub, b_ub, a_eq, b_eq = [], [], [], []
    for a1, a2, sentido, b in [_normalizar_restriccion(r) for r in restricciones]:
        if sentido == "<=":
            a_ub.append([a1, a2])
            b_ub.append(b)
        elif sentido == ">=":
            a_ub.append([-a1, -a2])
            b_ub.append(-b)
        else:
            a_eq.append([a1, a2])
            b_eq.append(b)
    return a_ub or None, b_ub or None, a_eq or None, b_eq or None


def resolver_grafico(c1, c2, restricciones, maximizar):
    objetivo = [-c1, -c2] if maximizar else [c1, c2]
    a_ub, b_ub, a_eq, b_eq = _matrices_linprog(restricciones)
    lp = linprog(objetivo, A_ub=a_ub, b_ub=b_ub, A_eq=a_eq, b_eq=b_eq, bounds=[(0, None), (0, None)], method="highs")
    if lp.status == 2:
        return [], [], None, "infactible", []
    if lp.status == 3:
        vertices = calcular_vertices(restricciones)
        resultados = [(v, c1 * v[0] + c2 * v[1]) for v in vertices]
        return vertices, resultados, None, "no_acotado", []
    if not lp.success:
        return [], [], None, "error", []

    vertices = calcular_vertices(restricciones)
    if not vertices:
        punto = (round(float(lp.x[0]), 6), round(float(lp.x[1]), 6))
        vertices = [punto]
    resultados = [(v, c1 * v[0] + c2 * v[1]) for v in vertices]
    zopt = -lp.fun if maximizar else lp.fun
    optimo = (min(vertices, key=lambda v: abs((c1 * v[0] + c2 * v[1]) - zopt)), zopt)
    optimos = [v for v, z in resultados if abs(z - zopt) <= 1e-6]
    return vertices, resultados, optimo, "optimo", optimos


def generar_grafica_plotly(c1, c2, restricciones, vertices, optimo, maximizar, oscuro=True, optimos=None):
    restricciones = [_normalizar_restriccion(r) for r in restricciones]
    optimos = optimos or ([optimo[0]] if optimo else [])
    if oscuro:
        paper_bg = "#1a1a2e"
        plot_bg = "#0f172a"
        font_color = "white"
        grid_color = "rgba(255,255,255,0.07)"
        zero_color = "rgba(255,255,255,0.5)"
        tick_color = "#94a3b8"
        legend_bg = "rgba(15,23,42,0.92)"
        legend_border = "rgba(167,139,250,0.35)"
        annot_bg_eq = "rgba(22,33,62,0.85)"
        annot_bg_vtx = "rgba(15,12,41,0.82)"
        annot_vtx_border = "rgba(100,116,139,0.5)"
        annot_opt_bg = "rgba(120,53,15,0.85)"
        vtx_color = "#64748b"
        vtx_line_color = "#94a3b8"
        txt_color = "#cbd5e1"
        modebar_bg = "rgba(15,23,42,0.8)"
        title_color = "white"
    else:
        paper_bg = "#f8f7ff"
        plot_bg = "#ffffff"
        font_color = "#1e1b4b"
        grid_color = "rgba(0,0,0,0.07)"
        zero_color = "rgba(0,0,0,0.35)"
        tick_color = "#5b4fa8"
        legend_bg = "rgba(255,255,255,0.95)"
        legend_border = "rgba(124,58,237,0.3)"
        annot_bg_eq = "rgba(240,237,255,0.92)"
        annot_bg_vtx = "rgba(248,247,255,0.92)"
        annot_vtx_border = "rgba(124,58,237,0.3)"
        annot_opt_bg = "rgba(254,243,199,0.95)"
        vtx_color = "#7c3aed"
        vtx_line_color = "#a78bfa"
        txt_color = "#1e1b4b"
        modebar_bg = "rgba(240,237,255,0.8)"
        title_color = "#1e1b4b"

    todos_x = [v[0] for v in vertices] + [0]
    todos_y = [v[1] for v in vertices] + [0]
    for a1, a2, _, b in restricciones:
        if abs(a1) > EPS:
            todos_x.append(b / a1)
        if abs(a2) > EPS:
            todos_y.append(b / a2)

    max_x = max([x for x in todos_x if x >= 0] or [10])
    max_y = max([y for y in todos_y if y >= 0] or [10])
    rango = max(max_x, max_y, 1) * 1.25
    rango = int(np.ceil(rango / 5) * 5) if rango > 5 else int(np.ceil(rango)) + 2

    fig = go.Figure()
    colores = ["#3b82f6", "#10b981", "#ec4899", "#f59e0b", "#8b5cf6", "#f97316"]
    x_linea = np.linspace(0, rango * 1.1, 800)

    for i, (a1, a2, sentido, b) in enumerate(restricciones):
        color = colores[i % len(colores)]
        simbolo = {"<=": "<=", ">=": ">=", "=": "="}[sentido]
        if abs(a2) > EPS:
            y_vals = (b - a1 * x_linea) / a2
            mask = (y_vals >= -rango * 0.1) & (y_vals <= rango * 1.2) & (x_linea >= 0)
            label = f"{a1}x1 + {a2}x2 = {b}"
            fig.add_trace(
                go.Scatter(
                    x=x_linea[mask],
                    y=y_vals[mask],
                    mode="lines",
                    name=f"R{i + 1}: {a1}x1 + {a2}x2 {simbolo} {b}",
                    line=dict(color=color, width=2.5),
                    hovertemplate=f"<b>R{i + 1}: {label}</b><br>x1=%{{x:.3f}}, x2=%{{y:.3f}}<extra></extra>",
                )
            )
        elif abs(a1) > EPS:
            xv = b / a1
            fig.add_shape(type="line", x0=xv, x1=xv, y0=0, y1=rango, line=dict(color=color, width=2.5))

    if len(vertices) >= 3:
        try:
            pts = np.array(vertices)
            hull = ConvexHull(pts)
            hull_pts = pts[hull.vertices]
            hull_pts = np.vstack([hull_pts, hull_pts[0]])
            fig.add_trace(
                go.Scatter(
                    x=hull_pts[:, 0],
                    y=hull_pts[:, 1],
                    fill="toself",
                    fillcolor="rgba(124,58,237,0.18)",
                    line=dict(color="rgba(167,139,250,0.5)", width=1.5, dash="dot"),
                    name="Region factible",
                    hoverinfo="skip",
                    showlegend=True,
                )
            )
        except Exception:
            pass

    if optimo:
        popt, zopt = optimo
        for v in vertices:
            z = c1 * v[0] + c2 * v[1]
            es_optimo = any(round(v[0], 4) == round(o[0], 4) and round(v[1], 4) == round(o[1], 4) for o in optimos)
            fig.add_trace(
                go.Scatter(
                    x=[v[0]],
                    y=[v[1]],
                    mode="markers",
                    marker=dict(size=18 if es_optimo else 11, color="#f59e0b" if es_optimo else vtx_color, symbol="star" if es_optimo else "circle", line=dict(color="#fef3c7" if es_optimo else vtx_line_color, width=2)),
                    name=f"Optimo: Z={round(zopt, 4)}" if es_optimo else None,
                    showlegend=es_optimo,
                    hovertemplate=f"<b>{'Punto optimo' if es_optimo else 'Vertice'}</b><br>x1={round(v[0], 4)}, x2={round(v[1], 4)}<br>Z={round(z, 4)}<extra></extra>",
                )
            )
            fig.add_annotation(
                x=v[0] + rango * 0.04,
                y=v[1] + rango * 0.04,
                text=f"({round(v[0], 3)}, {round(v[1], 3)})<br>Z={round(z, 3)}",
                showarrow=True,
                arrowhead=2,
                arrowsize=0.8,
                arrowcolor="#f59e0b" if es_optimo else vtx_color,
                arrowwidth=1.2,
                ax=18,
                ay=-28,
                font=dict(size=11, color=txt_color),
                bgcolor=annot_opt_bg if es_optimo else annot_bg_vtx,
                bordercolor="#f59e0b" if es_optimo else annot_vtx_border,
                borderwidth=1,
                borderpad=5,
            )

        if abs(c2) > EPS:
            y_obj = (zopt - c1 * x_linea) / c2
            mask_obj = (y_obj >= -rango * 0.08) & (y_obj <= rango) & (x_linea >= -rango * 0.08)
            fig.add_trace(
                go.Scatter(
                    x=x_linea[mask_obj],
                    y=y_obj[mask_obj],
                    mode="lines",
                    name=f"Linea de nivel: Z = {round(zopt, 4)}",
                    line=dict(color="#f59e0b", width=3, dash="dash"),
                    hovertemplate=f"<b>Linea de nivel optima</b><br>{c1}x1 + {c2}x2 = {round(zopt, 4)}<extra></extra>",
                )
            )

    tipo_str = "Maximizar" if maximizar else "Minimizar"
    tickvals = list(range(0, rango + 1, max(1, rango // 10)))
    fig.update_layout(
        title=dict(text=f"<b>{tipo_str}  Z = {c1}x1 + {c2}x2</b>", font=dict(size=17, color=title_color, family="Inter"), x=0.5, xanchor="center"),
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=font_color, family="Inter"),
        xaxis=dict(title=dict(text="x1", font=dict(color="#a78bfa", size=14)), gridcolor=grid_color, zerolinecolor=zero_color, zerolinewidth=2, tickfont=dict(color=tick_color, size=11), range=[-rango * 0.08, rango], tickvals=tickvals, showgrid=True, dtick=max(1, rango // 10)),
        yaxis=dict(title=dict(text="x2", font=dict(color="#a78bfa", size=14)), gridcolor=grid_color, zerolinecolor=zero_color, zerolinewidth=2, tickfont=dict(color=tick_color, size=11), range=[-rango * 0.08, rango], tickvals=tickvals, showgrid=True, dtick=max(1, rango // 10)),
        legend=dict(bgcolor=legend_bg, bordercolor=legend_border, borderwidth=1, font=dict(color=font_color, size=11), x=0.01, y=0.99, xanchor="left", yanchor="top"),
        hovermode="closest",
        dragmode="zoom",
        margin=dict(l=60, r=30, t=60, b=60),
        height=540,
        modebar=dict(bgcolor=modebar_bg, color="#a78bfa", activecolor="#7c3aed"),
    )
    return fig
