from fractions import Fraction

import numpy as np


EPS = 1e-9


def _frac(valor):
    if isinstance(valor, Fraction):
        return valor
    return Fraction(str(valor)).limit_denominator(1_000_000)


def _restriccion_normalizada(restriccion):
    if len(restriccion) == 2:
        fila, b = restriccion
        sentido = "<="
    else:
        fila, sentido, b = restriccion
    fila = [_frac(v) for v in fila]
    b = _frac(b)
    if b < 0:
        fila = [-v for v in fila]
        b = -b
        sentido = {">=": "<=", "<=": ">=", "=": "="}[sentido]
    return fila, sentido, b


def _a_float(valor):
    return float(valor)


def _tabla_numpy(tabla):
    return np.array(tabla, dtype=object)


def _preparar_objetivo(tabla, base, costos):
    fila_z = [-c for c in costos] + [Fraction(0)]
    for i, basica in enumerate(base):
        cb = costos[basica]
        if cb:
            fila_z = [fila_z[j] + cb * tabla[i][j] for j in range(len(fila_z))]
    tabla[-1] = fila_z


def _snapshot(tabla, fase, mensaje):
    return {
        "tabla": _tabla_numpy([[v for v in fila] for fila in tabla]),
        "fase": fase,
        "mensaje": mensaje,
    }


def _resolver_tabla(tabla, base, etiquetas, fase, historial, pasos, max_iter=200, bloqueadas=None):
    bloqueadas = bloqueadas or set()
    iteracion = 0
    while iteracion < max_iter:
        fila_z = tabla[-1][:-1]
        negativos = [(j, v) for j, v in enumerate(fila_z) if v < 0 and j not in bloqueadas]
        if not negativos:
            return "optimo"

        col_p, valor_col = min(negativos, key=lambda item: (item[1], item[0]))
        razones = []
        for i, fila in enumerate(tabla[:-1]):
            if fila[col_p] > 0:
                razones.append((i, fila[-1] / fila[col_p]))
            else:
                razones.append((i, None))

        candidatas = [(i, r) for i, r in razones if r is not None and r >= 0]
        if not candidatas:
            pasos.append(
                {
                    "fase": fase,
                    "col_p": col_p,
                    "fil_p": -1,
                    "razones": [r for _, r in razones],
                    "mensaje": (
                        f"Se elige {etiquetas[col_p]} porque tiene el coeficiente mas negativo "
                        "en la fila Z, pero no hay entradas positivas en su columna. "
                        "La funcion objetivo puede crecer sin limite."
                    ),
                }
            )
            return "no_acotado"

        fil_p, razon_min = min(candidatas, key=lambda item: (item[1], item[0]))
        variable_sale = etiquetas[base[fil_p]]
        pivote = tabla[fil_p][col_p]

        pasos.append(
            {
                "fase": fase,
                "col_p": col_p,
                "fil_p": fil_p,
                "razones": [r for _, r in razones],
                "mensaje": (
                    f"Entra {etiquetas[col_p]} porque su coeficiente en Z es {valor_col}. "
                    f"Sale {variable_sale} porque tiene la menor razon positiva "
                    f"({tabla[fil_p][-1]} / {pivote} = {razon_min})."
                ),
            }
        )

        tabla[fil_p] = [v / pivote for v in tabla[fil_p]]
        for i in range(len(tabla)):
            if i == fil_p:
                continue
            factor = tabla[i][col_p]
            if factor:
                tabla[i] = [tabla[i][j] - factor * tabla[fil_p][j] for j in range(len(tabla[i]))]
        base[fil_p] = col_p
        iteracion += 1
        historial.append(_snapshot(tabla, fase, pasos[-1]["mensaje"]))

    return "iteraciones_agotadas"


def construir_tabla(c, restricciones, maximizar, n_vars, n_rest):
    resultado = _construir_modelo(c, restricciones, maximizar, n_vars)
    return _tabla_numpy(resultado["tabla"])


def _construir_modelo(c, restricciones, maximizar, n_vars):
    restricciones_norm = [_restriccion_normalizada(r) for r in restricciones]
    etiquetas = [f"x{i + 1}" for i in range(n_vars)]
    filas = [[*fila] for fila, _, _ in restricciones_norm]
    base = []
    artificiales = []

    for i, (_, sentido, b) in enumerate(restricciones_norm):
        for fila in filas:
            fila.append(Fraction(0))
        if sentido == "<=":
            etiquetas.append(f"s{i + 1}")
            filas[i][-1] = Fraction(1)
            base.append(len(etiquetas) - 1)
        elif sentido == ">=":
            etiquetas.append(f"e{i + 1}")
            filas[i][-1] = Fraction(-1)
            for fila in filas:
                fila.append(Fraction(0))
            etiquetas.append(f"a{i + 1}")
            filas[i][-1] = Fraction(1)
            base.append(len(etiquetas) - 1)
            artificiales.append(len(etiquetas) - 1)
        else:
            etiquetas.append(f"a{i + 1}")
            filas[i][-1] = Fraction(1)
            base.append(len(etiquetas) - 1)
            artificiales.append(len(etiquetas) - 1)

    tabla = [[*filas[i], restricciones_norm[i][2]] for i in range(len(filas))]
    tabla.append([Fraction(0) for _ in range(len(etiquetas) + 1)])
    c_original = [_frac(v) if maximizar else -_frac(v) for v in c]
    c_original += [Fraction(0) for _ in range(len(etiquetas) - n_vars)]
    return {
        "tabla": tabla,
        "base": base,
        "etiquetas": etiquetas,
        "artificiales": artificiales,
        "costos": c_original,
    }


def resolver_simplex(c, restricciones, maximizar, n_vars, n_rest):
    modelo = _construir_modelo(c, restricciones, maximizar, n_vars)
    tabla = modelo["tabla"]
    base = modelo["base"]
    etiquetas = modelo["etiquetas"]
    artificiales = set(modelo["artificiales"])
    historial = [_snapshot(tabla, "Inicio", "Tabla inicial en forma canonica.")]
    pasos = []

    if artificiales:
        costos_fase1 = [Fraction(-1) if j in artificiales else Fraction(0) for j in range(len(etiquetas))]
        _preparar_objetivo(tabla, base, costos_fase1)
        historial = [_snapshot(tabla, "Fase I", "Se minimiza la suma de variables artificiales para comprobar factibilidad.")]
        estado = _resolver_tabla(tabla, base, etiquetas, "Fase I", historial, pasos)
        if estado != "optimo":
            return _tabla_numpy(tabla), [h["tabla"] for h in historial], estado, {
                "etiquetas": etiquetas,
                "base": [etiquetas[i] for i in base],
                "base_indices": list(base),
                "pasos": pasos,
                "historial_info": historial,
                "multiples": False,
            }
        if abs(_a_float(tabla[-1][-1])) > EPS:
            return _tabla_numpy(tabla), [h["tabla"] for h in historial], "infactible", {
               "etiquetas": etiquetas,
               "base": [etiquetas[i] for i in base],
                "base_indices": list(base),
                "pasos": pasos,
                "historial_info": historial,
                "multiples": False,
            }

    _preparar_objetivo(tabla, base, modelo["costos"])
    historial.append(_snapshot(tabla, "Fase II", "Se optimiza la funcion objetivo original."))
    estado = _resolver_tabla(tabla, base, etiquetas, "Fase II", historial, pasos, bloqueadas=artificiales)
    no_basicas = set(range(len(etiquetas))) - set(base) - artificiales
    multiples = estado == "optimo" and any(abs(_a_float(tabla[-1][j])) < EPS for j in no_basicas)
    info = {
        "etiquetas": etiquetas,
        "base": [etiquetas[i] for i in base],
        "base_indices": list(base),
        "pasos": pasos,
        "historial_info": historial,
        "multiples": multiples,
        "artificiales": sorted(artificiales),
    }
    return _tabla_numpy(tabla), [h["tabla"] for h in historial], estado, info


def extraer_solucion(tabla, n_vars, n_rest, maximizar, base_indices=None):
    filas = tabla.tolist() if hasattr(tabla, "tolist") else tabla
    n_cols = len(filas[0]) - 1
    solucion = []
    if base_indices is not None:
        solucion = [Fraction(0) for _ in range(n_cols)]
        for i, col_idx in enumerate(base_indices):
            if col_idx < n_cols:
                solucion[col_idx] = filas[i][-1]
        z = filas[-1][-1] if maximizar else -filas[-1][-1]
        return solucion, z
    for j in range(n_cols):
        col = [filas[i][j] for i in range(len(filas) - 1)]
        unos = [i for i, v in enumerate(col) if abs(_a_float(v) - 1.0) <= EPS]
        ceros = all(abs(_a_float(v)) <= EPS or idx in unos for idx, v in enumerate(col))
        if len(unos) == 1 and ceros:
            solucion.append(filas[unos[0]][-1])
        else:
            solucion.append(Fraction(0))
    z = filas[-1][-1] if maximizar else -filas[-1][-1]
    return solucion, z
