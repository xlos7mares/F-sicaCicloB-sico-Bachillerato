import re
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from sympy import S, Symbol, latex, nsimplify, simplify, solve

st.set_page_config(
    page_title="Física paso a paso · Bachillerato",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

NOTION_URL = "https://mahogany-lizard-400.notion.site"  # cambialo cuando acortes tu dominio

# clave: (LaTeX, texto, nombre, unidad, color)
VARS = {
    "dx": (r"\Delta x", "Δx", "desplazamiento", "m", "#22e3ff"),
    "v0": ("v_0", "v₀", "velocidad inicial", "m/s", "#ff4fd8"),
    "v": ("v", "v", "velocidad final", "m/s", "#b8ff2c"),
    "a": ("a", "a", "aceleración", "m/s²", "#ff9f1c"),
    "t": ("t", "t", "tiempo", "s", "#ffe14a"),
}
E = {k: Symbol(k, real=True) for k in VARS}
dx, v0, v, a, t = (E[k] for k in ("dx", "v0", "v", "a", "t"))

# La clave es la variable que NO aparece en la ecuación
EQ = {
    "dx": ("velocidad según el tiempo", r"@v=@v0+@a\cdot@t", v, v0 + a * t),
    "v": ("ecuación horaria de la posición", r"@dx=@v0\cdot@t+\dfrac{1}{2}\cdot@a\cdot@t^2", dx, v0 * t + a * t**2 / 2),
    "t": ("ecuación de Torricelli (no usa el tiempo)", r"@v^2=@v0^2+2\cdot@a\cdot@dx", v**2, v0**2 + 2 * a * dx),
    "a": ("desplazamiento con la velocidad media", r"@dx=\dfrac{@v0+@v}{2}\cdot@t", dx, (v0 + v) * t / 2),
    "v0": ("desplazamiento con la velocidad final", r"@dx=@v\cdot@t-\dfrac{1}{2}\cdot@a\cdot@t^2", dx, v * t - a * t**2 / 2),
}

# Módulos habilitados en esta versión
MODULOS_HABILITADOS = {
    "Introducción y mediciones": "mediciones",
    "Cinemática": "cinematica",
    "Dinámica y leyes de Newton": "dinamica",
    "Introducción al electromagnetismo": "ohm",
}

PLAN = {
    "1.º año · 4.º de Liceo (Tramo 7)": [
        ("Introducción y mediciones", "SI, cifras significativas, errores e incertidumbre"),
        ("Vibraciones y ondas", "Ondas mecánicas y sonoras, reflexión, refracción y difracción"),
        ("Luz y óptica geométrica", "Espectro electromagnético, espejos, lentes y colores"),
        ("Introducción al electromagnetismo", "Circuitos básicos, Ley de Ohm, Kirchhoff, Faraday y Lenz"),
    ],
    "2.º año · 5.º de Liceo (Tramo 8)": [
        ("Cinemática", "MRU, MRUA, caída libre, tiro vertical · próximos: parabólico y circular"),
        ("Dinámica y leyes de Newton", "Vectores, fuerzas, leyes de Newton y Gravitación Universal"),
        ("Trabajo, energía y conservación", "Trabajo, potencia, energía mecánica, impulso y cantidad de movimiento"),
        ("Termodinámica", "Equilibrio térmico, calor, 1.º y 2.º principio, máquinas térmicas"),
    ],
    "3.º año · 6.º de Liceo": [
        ("Electrostática y campo eléctrico", "Coulomb, campo eléctrico, Ley de Gauss, potencial y condensadores"),
        ("Magnetismo y electromagnetismo", "Fuerza magnética, Ampère-Maxwell e inducción de Faraday"),
        ("Ecuaciones de Maxwell y ondas", "Síntesis del electromagnetismo y propagación de ondas EM"),
        ("Física moderna", "Efecto fotoeléctrico, modelos atómicos y relatividad especial"),
    ],
}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=Figtree:wght@400;500;600;700&display=swap');
.stApp{background:radial-gradient(900px 500px at 90% -5%,#00d4ff26,transparent),radial-gradient(800px 500px at 0% 10%,#3b22a055,transparent),#080b21;color:#e8ecff;font-family:'Figtree',sans-serif}
header[data-testid="stHeader"]{background:transparent}[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
.block-container{max-width:1250px;padding-top:1.4rem}h1,h2,h3{font-family:'Bricolage Grotesque',sans-serif!important}
.hero h1{margin:0;font-size:2.7rem;font-weight:800;letter-spacing:-.02em;background:linear-gradient(90deg,#fff,#22e3ff 60%,#b388ff);-webkit-background-clip:text;background-clip:text;color:transparent;padding:0}
.hero p{color:#aab3e6;max-width:720px;margin:4px 0 14px;font-size:1.05rem}
.st-key-pegar,.st-key-teoria,.st-key-solver,.st-key-resul{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.12);border-radius:24px;padding:20px 24px;backdrop-filter:blur(14px)}
.st-key-pegar{border-color:#22e3ff88;box-shadow:0 0 40px -14px #22e3ff}
textarea{background:rgba(0,0,0,.4)!important;color:#e8ecff!important;border-radius:14px!important;font-size:1.02rem!important}
div[data-baseweb="textarea"]{border:1.5px solid #22e3ff!important;border-radius:14px!important;background:rgba(0,0,0,.4)!important}
div[data-baseweb="textarea"]:focus-within{box-shadow:0 0 0 3px #22e3ff44,0 0 28px #22e3ff}
.plan-h{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.25rem;color:#ffe14a;text-shadow:0 0 12px #ffe14a77;margin:6px 0 2px}
.cap{color:#8d97cf;font-size:.8rem;margin:-6px 0 8px;line-height:1.3}
.chip{display:inline-block;padding:1px 11px;margin:2px 3px 2px 0;border-radius:999px;color:var(--k);font-weight:700;background:color-mix(in srgb,var(--k) 14%,transparent);border:1px solid var(--k);text-shadow:0 0 10px var(--k)}
.hint,.warn,.sign,.ok{margin:10px 0 4px;padding:12px 14px;border-radius:14px;line-height:1.5}
.hint{background:rgba(255,225,74,.08);border-left:3px solid #ffe14a;color:#f3f0d0}
.warn{background:rgba(255,79,216,.09);border-left:3px solid #ff4fd8;color:#ffd6f6}.warn b{color:#ff4fd8}
.sign{background:rgba(34,227,255,.09);border-left:3px solid #22e3ff;color:#d4f8ff}.sign b{color:#22e3ff}
.ok{background:rgba(184,255,44,.1);border:1px solid #b8ff2c;color:#e6ffb3;box-shadow:0 0 24px -8px #b8ff2c;font-size:1.1rem}
.sh{margin:14px 0 4px;font-family:'Bricolage Grotesque',sans-serif;font-size:1.2rem;font-weight:800;color:#fff}
.frase{margin:8px 0;padding:10px 14px;border-radius:14px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1)}
.frase i{color:#aab3e6}
.stApp .katex{font-size:1.25em}.stApp .katex *{text-shadow:0 0 8px currentColor}
[data-testid="stBaseButton-primary"]{background:linear-gradient(90deg,#22e3ff,#b388ff)!important;color:#080b21!important;border:0!important;font-weight:800!important;border-radius:14px!important;transition:transform .2s,box-shadow .2s}
[data-testid="stBaseButton-primary"]:hover{transform:translateY(-2px);box-shadow:0 8px 30px #22e3ff77}
[data-testid="stBaseButton-secondary"]{background:rgba(255,255,255,.06)!important;color:#e8ecff!important;border:1px solid rgba(255,255,255,.18)!important;border-radius:14px!important;text-align:left;transition:all .2s}
[data-testid="stBaseButton-secondary"]:hover:not(:disabled){border-color:#22e3ff!important;color:#22e3ff!important;box-shadow:0 0 22px -4px #22e3ff}
[data-testid="stBaseButton-secondary"]:disabled{opacity:.45}
[data-testid="stNumberInput"] div,[data-testid="stNumberInput"] input{background:transparent!important}
[data-testid="stNumberInput"] div[data-baseweb="input"]{background:rgba(0,0,0,.45)!important;border:1.5px solid var(--k)!important;border-radius:14px!important}
[data-testid="stNumberInput"] input{color:var(--k)!important;font-weight:800;font-size:1.4rem;text-shadow:0 0 12px var(--k)}
[data-testid="stNumberInput"] button{color:var(--k)!important}
.credit{margin:36px auto 12px;max-width:600px;text-align:center;padding:16px 22px;border-radius:18px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.12);color:#aab3e6;line-height:1.65;transition:box-shadow .25s,border-color .25s}
.credit:hover{border-color:#b8ff2c;box-shadow:0 0 30px -8px #b8ff2c}
.credit b{color:#ffe14a;font-size:1.15rem;text-shadow:0 0 12px #ffe14a88}
.credit .agro{color:#b8ff2c;font-weight:600}
.credit a{color:#22e3ff;text-decoration:none;font-weight:600}
.credit a:hover{text-decoration:underline}
__VARCSS__</style>""".replace("__VARCSS__", "".join(f".st-key-c{k}{{--k:{x[4]}}}" for k, x in VARS.items()))
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Utilidades ----------
def C(k, txt):
    return rf"{{\color{{{VARS[k][4]}}}{txt}}}"


def dec(x):
    """Decimal con coma si es finito; si no, fracción o aproximación."""
    x = S(x)
    if x.is_Rational:
        q = x.q
        while q % 2 == 0:
            q //= 2
        while q % 5 == 0:
            q //= 5
        return f"{float(x):.10g}".replace(".", "{,}") if q == 1 else latex(x)
    return f"{float(x):.4g}".replace(".", "{,}")


def exacto(x):
    x = S(x)
    return x.is_Rational and dec(x) == f"{float(x):.10g}".replace(".", "{,}")


def val(k, x):
    s = dec(x)
    return C(k, f"({s})" if x < 0 else s)


def eq_tex(k, P):
    return re.sub(r"@(\w+)", lambda m: P[m.group(1)], EQ[k][1])


def chip(txt, k):
    return f'<span class="chip" style="--k:{k}">{txt}</span>'


def box(kind, title, body):
    st.markdown(f'<div class="{kind}"><b>{title}</b><br>{body}</div>', unsafe_allow_html=True)


def plano(x):
    x = S(x)
    t_ = f"{float(x):.10g}" if exacto(x) else "≈" + f"{float(x):.4g}"
    return t_.replace(".", ",")


def num_txt(k, x):
    return f"{VARS[k][1]} = {plano(x)} {VARS[k][3]}"


# ---------- Motor exacto (SymPy): Cinemática ----------
def resolver(datos):
    sub = {E[k]: nsimplify(x, rational=True) for k, x in datos.items()}
    inc = [k for k in VARS if k not in datos]
    out = []
    for u1, u2 in (inc, inc[::-1]):
        try:
            for r1 in solve((EQ[u2][2] - EQ[u2][3]).subs(sub), E[u1]):
                s2 = {**sub, E[u1]: r1}
                for r2 in solve((EQ[u1][2] - EQ[u1][3]).subs(s2), E[u2]):
                    full = {**s2, E[u2]: r2}
                    if r1.is_real and r2.is_real and all(simplify((q[2] - q[3]).subs(full)) == 0 for q in EQ.values()):
                        vals = {k: simplify(full[E[k]]) for k in VARS}
                        if vals["t"] >= 0 and all(vals != o["vals"] for o in out):
                            out.append({"orden": (u1, u2), "vals": vals})
        except Exception:
            continue
    if any(o["vals"]["t"] > 0 for o in out):
        out = [o for o in out if o["vals"]["t"] > 0]
    return out


def lin(xs, ys, titulo, k, pt):
    f = go.Figure(go.Scatter(
        x=xs, y=ys, mode="lines",
        line=dict(color=VARS[k][4], width=3.5),
        hovertemplate="t=%{x:.2f} s<br>%{y:.2f}<extra></extra>",
    ))
    f.add_trace(go.Scatter(x=[pt[0]], y=[pt[1]], mode="markers", marker=dict(size=11, color="#fff"), hoverinfo="skip"))
    ax = dict(gridcolor="rgba(255,255,255,.08)", zerolinecolor="rgba(255,255,255,.7)", color="#aab3e6")
    f.update_layout(
        title=dict(text=titulo, font=dict(color="#e8ecff", size=14)),
        height=300, showlegend=False,
        margin=dict(l=8, r=8, t=40, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,.25)",
        xaxis=dict(title="t (s)", **ax), yaxis=ax,
    )
    return f


def mostrar(datos):
    sols = resolver(datos)
    if not sols:
        box(
            "warn",
            "No encontré una solución física",
            "Revisá los datos y sus signos: con ellos el movimiento no es posible "
            "(por ejemplo, un tiempo negativo o una raíz de un número negativo).",
        )
        return
    SIM = {k: C(k, VARS[k][0]) for k in VARS}
    for i, s in enumerate(sols, 1):
        vals, (u1, u2) = s["vals"], s["orden"]
        if len(sols) > 1:
            st.markdown(f'<div class="sh">Solución {i} de {len(sols)}</div>', unsafe_allow_html=True)
            box(
                "sign",
                "¿Por qué dos?",
                "Las dos son matemáticamente válidas. Elegí según el contexto "
                "(por ejemplo, el cuerpo pasa dos veces por la misma altura: una subiendo y otra bajando).",
            )
        st.markdown('<div class="sh">1. Datos e incógnitas</div>', unsafe_allow_html=True)
        st.markdown(
            "".join(
                chip(num_txt(k, vals[k]), VARS[k][4]) if k in datos else chip(f"{VARS[k][1]} = ?  ({VARS[k][2]})", VARS[k][4])
                for k in VARS
            ),
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sh">2. Elegí la ecuación y reemplazá</div>', unsafe_allow_html=True)
        for n, (u, falta) in enumerate(((u1, u2), (u2, u1))):
            st.markdown(
                f"**{'Primero' if n == 0 else 'Después'}, hallá {VARS[u][1]} ({VARS[u][2]})**: usá una ecuación "
                f"**sin {VARS[falta][1]}**, que es la que todavía no conocés. Es la {EQ[falta][0]}."
            )
            st.latex(eq_tex(falta, SIM))
            P = {k: (SIM[k] if k == u else val(k, vals[k])) for k in VARS}
            st.latex(eq_tex(falta, P))
            ig = "=" if exacto(vals[u]) else r"\approx"
            st.latex(rf"{SIM[u]} {ig} {C(u, dec(vals[u]))}\ \text{{{VARS[u][3]}}}")
            if u == "t" and falta in ("v", "v0"):
                box("warn", "Ecuación de segundo grado", "Da dos valores de t. El tiempo no puede ser negativo: se descarta ese.")
            if u == "v" and falta == "t":
                box("warn", "Cuidado con ±", "Al sacar la raíz hay dos signos posibles. Se elige el que coincide con el sentido del movimiento.")
        st.markdown('<div class="sh">3. Respuesta</div>', unsafe_allow_html=True)
        resp = " · ".join(f"<b>{VARS[k][2]}</b>: {num_txt(k, vals[k])}" for k in (u1, u2))
        st.markdown(f'<div class="ok">{resp}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sh">4. Comprobá con otra ecuación</div>', unsafe_allow_html=True)
        chk = next((k for k in VARS if k in datos), u1)
        Pall = {k: val(k, vals[k]) for k in VARS}
        L, R = EQ[chk][2].subs({E[k]: vals[k] for k in VARS}), EQ[chk][3].subs({E[k]: vals[k] for k in VARS})
        st.latex(eq_tex(chk, Pall) + rf"\ \Rightarrow\ {dec(simplify(L))} = {dec(simplify(R))}")
        T = float(vals["t"])
        if T > 0:
            ts = np.linspace(0, T, 200)
            v0f, af = float(vals["v0"]), float(vals["a"])
            g1, g2 = st.columns(2)
            g1.plotly_chart(
                lin(ts, v0f * ts + af * ts**2 / 2, "Posición recorrida", "dx", (T, float(vals["dx"]))),
                use_container_width=True,
                config={"displaylogo": False},
            )
            g2.plotly_chart(
                lin(ts, v0f + af * ts, "Velocidad", "v", (T, float(vals["v"]))),
                use_container_width=True,
                config={"displaylogo": False},
            )


# ---------- Analizador de enunciados en español ----------
def analizar_enunciado(texto):
    limpio = texto.strip()
    baja = limpio.lower()

    fuera_tema = [
        ("newton|fuerza|masa|dinámica|dinamica|rozamiento", "Dinámica y leyes de Newton"),
        ("energía|energia|trabajo|potencia|cinética|cinetica|potencial", "Trabajo y energía"),
        ("ohm|voltaje|corriente|resistencia|circuito|amperes|amperios", "Electricidad y circuitos"),
        ("refracción|refraccion|reflexión|reflexion|lente|espejo|snell", "Óptica geométrica"),
        ("calor|temperatura|gas ideal|termodinámica|termodinamica", "Termodinámica"),
    ]
    for patron, nombre_tema in fuera_tema:
        if re.search(patron, baja) and not re.search(r"velocidad|aceleración|aceleracion|caída|caida|mrua|mru", baja):
            return {
                "tipo": "otro",
                "tema": nombre_tema,
                "datos": {},
                "frases": [],
                "incognita": None,
                "cuidados": [f"Este enunciado parece corresponder a <b>{nombre_tema}</b>. Podés abrir ese módulo desde el menú de temas."],
            }, None

    datos = {}
    frases = []
    cuidados = []

    if re.search(r"\b(reposo|se suelta|deja caer|dejado caer|parte del reposo)\b", baja):
        datos["v0"] = 0.0
        frases.append({
            "frase": "reposo / se suelta / se deja caer",
            "clave": "v0",
            "valor": 0.0,
            "por_que": "Dato implícito: al partir del reposo o soltarse, la velocidad inicial es 0 m/s.",
        })

    if re.search(r"\b(se detiene|frena hasta detenerse|punto más alto|altura máxima|llega arriba)\b", baja):
        datos["v"] = 0.0
        frases.append({
            "frase": "se detiene / punto más alto",
            "clave": "v",
            "valor": 0.0,
            "por_que": "Dato implícito: al detenerse o alcanzar el punto más alto, la velocidad final (o en ese instante) es 0 m/s.",
        })

    es_vertical = bool(re.search(r"\b(caída libre|caida libre|tiro vertical|cae|sube|altura|puente|edificio|pozo)\b", baja))
    if es_vertical and "a" not in datos:
        datos["a"] = -9.8
        frases.append({
            "frase": "movimiento vertical bajo gravedad (g = 9,8 m/s²)",
            "clave": "a",
            "valor": -9.8,
            "por_que": "Con el eje positivo hacia arriba, la aceleración gravitatoria es -9,8 m/s².",
        })
        cuidados.append("Revisá el signo de la aceleración (g = 9,8 m/s²) según el sentido positivo que elijas en tu eje vertical.")

    patron_num = r"(-?\d+(?:[.,]\d+)?)\s*(km/h|m/s²|m/s2|m/s|km|cm|mm|m|min|horas|hora|h|s)\b"
    for m in re.finditer(patron_num, baja):
        raw_num = m.group(1).replace(",", ".")
        unidad = m.group(2)
        try:
            num = float(raw_num)
        except ValueError:
            continue

        span_ini = max(0, m.start() - 35)
        span_fin = min(len(baja), m.end() + 35)
        contexto = baja[span_ini:span_fin]
        fragmento_real = limpio[max(0, m.start() - 18):min(len(limpio), m.end() + 18)].strip()

        if unidad == "km/h":
            conv = round(num / 3.6, 6)
            clave = "v0" if "v0" not in datos or re.search(r"inicial|parte|arranca|sale", contexto) else "v"
            datos[clave] = conv
            frases.append({
                "frase": fragmento_real,
                "clave": clave,
                "valor": conv,
                "por_que": f"Convertido de {raw_num.replace('.', ',')} km/h a m/s dividiendo entre 3,6.",
            })
            cuidados.append(f"Se convirtió {raw_num.replace('.', ',')} km/h a m/s (÷ 3,6) para trabajar en unidades del SI.")
        elif unidad == "m/s":
            if re.search(r"inicial|parte|arranca|sale|lanza|dispara", contexto) and "v0" not in datos:
                clave = "v0"
            elif re.search(r"final|llega|alcanza|al cabo", contexto) and "v" not in datos:
                clave = "v"
            else:
                clave = "v0" if "v0" not in datos else "v"
            datos[clave] = num
            frases.append({
                "frase": fragmento_real,
                "clave": clave,
                "valor": num,
                "por_que": "Velocidad expresada directamente en m/s.",
            })
        elif unidad in ("m/s²", "m/s2"):
            if re.search(r"frena|frenado|desacelera", contexto) and num > 0:
                num = -num
                cuidados.append("Al frenar en el sentido del movimiento positivo, la aceleración es negativa.")
            datos["a"] = num
            frases.append({
                "frase": fragmento_real,
                "clave": "a",
                "valor": num,
                "por_que": "Aceleración en m/s².",
            })
        elif unidad in ("km", "cm", "mm", "m"):
            val_m = num
            if unidad == "km":
                val_m = num * 1000.0
                cuidados.append(f"Se convirtieron {raw_num.replace('.', ',')} km a metros (× 1000).")
            elif unidad == "cm":
                val_m = num / 100.0
                cuidados.append(f"Se convirtieron {raw_num.replace('.', ',')} cm a metros (÷ 100).")
            elif unidad == "mm":
                val_m = num / 1000.0
                cuidados.append(f"Se convirtieron {raw_num.replace('.', ',')} mm a metros (÷ 1000).")
            if "dx" not in datos:
                datos["dx"] = val_m
                frases.append({
                    "frase": fragmento_real,
                    "clave": "dx",
                    "valor": val_m,
                    "por_que": "Distancia / desplazamiento en metros (SI).",
                })
        elif unidad in ("min", "horas", "hora", "h", "s"):
            val_s = num
            if unidad == "min":
                val_s = num * 60.0
                cuidados.append(f"Se convirtieron {raw_num.replace('.', ',')} min a segundos (× 60).")
            elif unidad in ("horas", "hora", "h"):
                val_s = num * 3600.0
                cuidados.append(f"Se convirtieron {raw_num.replace('.', ',')} h a segundos (× 3600).")
            if "t" not in datos:
                datos["t"] = val_s
                frases.append({
                    "frase": fragmento_real,
                    "clave": "t",
                    "valor": val_s,
                    "por_que": "Tiempo en segundos (SI).",
                })

    incognita = None
    if re.search(r"cuánto tarda|cuanto tarda|qué tiempo|que tiempo|en qué momento|tiempo", baja) and "t" not in datos:
        incognita = "t"
    elif re.search(r"qué altura|que altura|qué distancia|que distancia|cuánto recorre|cuanto recorre|desplazamiento", baja) and "dx" not in datos:
        incognita = "dx"
    elif re.search(r"aceleración|aceleracion|frena con", baja) and "a" not in datos:
        incognita = "a"
    elif re.search(r"velocidad inicial|con qué velocidad parte|con que velocidad sale", baja) and "v0" not in datos:
        incognita = "v0"
    elif re.search(r"velocidad|qué rapidez|que rapidez|al llegar|al impactar", baja):
        incognita = "v" if "v" not in datos else "v0"
    else:
        incognita = next((k for k in VARS if k not in datos), None)

    if not cuidados:
        cuidados.append("Verificá que todos los datos estén en el Sistema Internacional (m, m/s, m/s², s) antes de despejar.")

    return {
        "tipo": "mrua",
        "tema": "Cinemática",
        "datos": datos,
        "frases": frases,
        "incognita": incognita,
        "cuidados": cuidados[:3],
    }, None


def cargar(datos):
    for k in VARS:
        st.session_state[f"s_{k}"] = k in datos
        st.session_state[f"n_{k}"] = float(datos.get(k, 0.0))
    st.session_state.tema = "cinematica"


def volver():
    st.session_state.tema = "home"


st.session_state.setdefault("tema", "home")
for k in VARS:
    st.session_state.setdefault(f"s_{k}", False)
    st.session_state.setdefault(f"n_{k}", 0.0)


def ir(clave):
    st.session_state.tema = clave


def pie():
    st.markdown(
        f'<div class="credit">Desarrollador: <b>Leonardo Olivea</b><br>'
        f'<span class="agro">🌾 Bachiller en Agronomía</span><br>'
        f'<a href="{NOTION_URL}" target="_blank">Ver mi sitio</a></div>',
        unsafe_allow_html=True,
    )


def datos_validos(d):
    out = {}
    for k in VARS:
        x = (d or {}).get(k)
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            out[k] = x
    return out


# ---------- Páginas ----------
def home():
    st.markdown(
        '<div class="hero"><h1>Física paso a paso</h1><p>Pegá un ejercicio y lo desmenuzo: qué datos tiene, '
        'qué teoría usar y cómo resolverlo sin perderte. Las cuentas exactas las hace SymPy.</p></div>',
        unsafe_allow_html=True,
    )
    with st.container(key="pegar"):
        st.markdown("#### 1. Pegá tu ejercicio")
        texto = st.text_area(
            "Enunciado",
            height=120,
            label_visibility="collapsed",
            key="enun",
            placeholder="Ej: Una piedra se deja caer desde un puente y tarda 3 s en llegar al agua. ¿Qué altura tiene el puente?",
        )
        if st.button("Desmenuzar ejercicio", type="primary", disabled=len(texto.strip()) < 15):
            with st.spinner("Analizando el enunciado…"):
                st.session_state.analisis = analizar_enunciado(texto)

    res = st.session_state.get("analisis")
    if res:
        info, err = res
        if err:
            box("warn", "No se pudo analizar", err)
        else:
            with st.container(key="resul"):
                st.markdown("#### 2. Así se lee tu ejercicio")
                for f in info.get("frases", []):
                    k = f.get("clave")
                    if k in VARS:
                        st.markdown(
                            f'<div class="frase">{chip(num_txt(k, nsimplify(str(f.get("valor", 0)), rational=True)), VARS[k][4])} '
                            f'<i>«{f.get("frase", "")}»</i><br>{f.get("por_que", "")}</div>',
                            unsafe_allow_html=True,
                        )
                d = datos_validos(info.get("datos"))
                inc = info.get("incognita")
                if inc in VARS:
                    st.markdown(f"**Qué te piden:** {chip(VARS[inc][1] + ' · ' + VARS[inc][2], VARS[inc][4])}", unsafe_allow_html=True)
                for c_ in info.get("cuidados", []):
                    box("warn", "Cuidado", c_)
                if info.get("tipo") == "otro":
                    box(
                        "sign",
                        "Tema de otro módulo",
                        f"Parece de <b>{info.get('tema', 'otro tema')}</b>. "
                        "Podés abrir el módulo correspondiente en el listado de temas de abajo.",
                    )
                elif len(d) == 3:
                    st.markdown("#### 3. Resolución")
                    mostrar(d)
                    st.button("Editar estos datos", on_click=cargar, args=(d,), key="ed")
                else:
                    box(
                        "sign",
                        "Revisá los datos",
                        f"Detecté {len(d)} datos y hacen falta exactamente 3. "
                        "Completalos o ajustalos en «Resolver con datos».",
                    )
                    st.button("Abrir con estos datos", on_click=cargar, args=(d,), key="ed")

    st.markdown("#### O elegí un tema")
    cols = st.columns(3, gap="large")
    for col_, (anio, temas) in zip(cols, PLAN.items()):
        with col_:
            st.markdown(f'<div class="plan-h">{anio}</div>', unsafe_allow_html=True)
            for nombre, resumen in temas:
                clave_mod = MODULOS_HABILITADOS.get(nombre)
                listo = clave_mod is not None
                st.button(
                    ("▶ " if listo else "") + nombre + ("" if listo else " · pronto"),
                    disabled=not listo,
                    on_click=ir,
                    args=(clave_mod or "home",),
                    use_container_width=True,
                    key=f"t_{
