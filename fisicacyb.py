import json
import re

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from sympy import S, Symbol, latex, nsimplify, simplify, solve

st.set_page_config(page_title="Física paso a paso · Bachillerato", page_icon="🚀", layout="wide",
                   initial_sidebar_state="collapsed")

NOTION_URL = "https://mahogany-lizard-400.notion.site"  # cambialo cuando acortes tu dominio
MODEL = "claude-sonnet-5-5"  # para gastar menos: "claude-haiku-5-5"
MAX_IA = 8  # consultas de IA por visita (protege tu saldo)

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
PLAN = {
    "1.º año · 4.º de Liceo": [
        ("Introducción y mediciones", "SI, cifras significativas, errores e incertidumbre"),
        ("Óptica geométrica", "Reflexión, refracción, Snell, lentes e instrumentos"),
        ("Electricidad y circuitos", "Carga, corriente, voltaje, Ley de Ohm, serie y paralelo"),
        ("Magnetismo inicial", "Imanes, campo terrestre, corrientes e imanes")],
    "2.º año · 5.º de Liceo": [
        ("Cinemática", "MRU, MRUA, caída libre, tiro vertical · próximos: tiro parabólico y circular"),
        ("Dinámica y leyes de Newton", "Fuerzas, diagramas de cuerpo libre, gravitación"),
        ("Trabajo, energía y conservación", "Trabajo, potencia, energías, impulso"),
        ("Termodinámica", "Calor, gases ideales, principios, máquinas térmicas")],
    "3.º año · 6.º de Liceo": [
        ("Electrostática y campo eléctrico", "Coulomb, campo, Gauss, potencial"),
        ("Magnetostática y campo magnético", "Lorentz, Biot-Savart, Ampère"),
        ("Inducción y ondas", "Faraday-Lenz, Maxwell, ondas electromagnéticas"),
        ("Física moderna", "Cuántica inicial y relatividad especial")],
}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=Figtree:wght@400;500;600;700&display=swap');
.stApp{background:radial-gradient(900px 500px at 90% -5%,#00d4ff26,transparent),radial-gradient(800px 500px at 0% 10%,#3b22a055,transparent),#080b21;color:#e8ecff;font-family:'Figtree',sans-serif}
header[data-testid="stHeader"]{background:transparent}[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
.block-container{max-width:1250px;padding-top:1.4rem}h1,h2,h3{font-family:'Bricolage Grotesque',sans-serif!important}
.hero h1{margin:0;font-size:2.7rem;font-weight:800;letter-spacing:-.02em;background:linear-gradient(90deg,#fff,#22e3ff 60%,#b388ff);-webkit-background-clip:text;background-clip:text;color:transparent;padding:0}
.hero p{color:#aab3e6;max-width:680px;margin:4px 0 14px;font-size:1.05rem}
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
.credit{margin:36px auto 12px;max-width:560px;text-align:center;padding:14px 20px;border-radius:18px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.12);color:#aab3e6;line-height:1.6;transition:box-shadow .25s,border-color .25s}
.credit:hover{border-color:#ffe14a;box-shadow:0 0 30px -8px #ffe14a}.credit b{color:#ffe14a;font-size:1.15rem;text-shadow:0 0 12px #ffe14a88}.credit a{color:#22e3ff}
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


# ---------- Motor exacto (SymPy): la IA nunca hace las cuentas ----------
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
    f = go.Figure(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=VARS[k][4], width=3.5),
                             hovertemplate="t=%{x:.2f} s<br>%{y:.2f}<extra></extra>"))
    f.add_trace(go.Scatter(x=[pt[0]], y=[pt[1]], mode="markers", marker=dict(size=11, color="#fff"), hoverinfo="skip"))
    ax = dict(gridcolor="rgba(255,255,255,.08)", zerolinecolor="rgba(255,255,255,.7)", color="#aab3e6")
    f.update_layout(title=dict(text=titulo, font=dict(color="#e8ecff", size=14)), height=300, showlegend=False,
                    margin=dict(l=8, r=8, t=40, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,.25)",
                    xaxis=dict(title="t (s)", **ax), yaxis=ax)
    return f


def mostrar(datos):
    sols = resolver(datos)
    if not sols:
        box("warn", "No encontré una solución física", "Revisá los datos y sus signos: con ellos el movimiento no es posible "
            "(por ejemplo, un tiempo negativo o una raíz de un número negativo).")
        return
    SIM = {k: C(k, VARS[k][0]) for k in VARS}
    for i, s in enumerate(sols, 1):
        vals, (u1, u2) = s["vals"], s["orden"]
        if len(sols) > 1:
            st.markdown(f'<div class="sh">Solución {i} de {len(sols)}</div>', unsafe_allow_html=True)
            box("sign", "¿Por qué dos?", "Las dos son matemáticamente válidas. Elegí según el contexto "
                "(por ejemplo, el cuerpo pasa dos veces por la misma altura: una subiendo y otra bajando).")
        st.markdown('<div class="sh">1. Datos e incógnitas</div>', unsafe_allow_html=True)
        st.markdown("".join(chip(num_txt(k, vals[k]), VARS[k][4]) if k in datos else
                            chip(f"{VARS[k][1]} = ?  ({VARS[k][2]})", VARS[k][4]) for k in VARS), unsafe_allow_html=True)
        st.markdown('<div class="sh">2. Elegí la ecuación y reemplazá</div>', unsafe_allow_html=True)
        for n, (u, falta) in enumerate(((u1, u2), (u2, u1))):
            st.markdown(f"**{'Primero' if n == 0 else 'Después'}, hallá {VARS[u][1]} ({VARS[u][2]})**: usá una ecuación "
                        f"**sin {VARS[falta][1]}**, que es la que todavía no conocés. Es la {EQ[falta][0]}.")
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
        resp = " · ".join(f"<b>{VARS[k][2]}</b>: {num_txt(k, vals[k])}"
                          for k in (u1, u2))
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
            g1.plotly_chart(lin(ts, v0f * ts + af * ts**2 / 2, "Posición recorrida", "dx",
                                (T, float(vals["dx"]))), use_container_width=True, config={"displaylogo": False})
            g2.plotly_chart(lin(ts, v0f + af * ts, "Velocidad", "v", (T, float(vals["v"]))),
                            use_container_width=True, config={"displaylogo": False})


# ---------- IA: solo identifica y explica el enunciado ----------
SISTEMA = """Sos profesor de Física de Bachillerato en Uruguay. Analizá el ejercicio y respondé SOLO con JSON válido, sin texto extra ni ```:
{"tipo":"mru|mrua|caida_libre|tiro_vertical|otro","tema":"nombre del tema si es otro","datos":{"dx":n|null,"v0":n|null,"v":n|null,"a":n|null,"t":n|null},
"frases":[{"frase":"texto literal del enunciado","clave":"dx|v0|v|a|t","valor":n,"por_que":"explicación corta"}],
"incognita":"dx|v0|v|a|t","cuidados":["errores típicos a evitar en este ejercicio"]}
Reglas: todo en unidades SI (convertí km/h a m/s y explicalo). Elegí el eje positivo en el sentido del movimiento inicial o hacia arriba en vertical; g = 9,8 m/s² (a = -9,8 si el eje positivo es hacia arriba). Incluí los datos implícitos: «reposo»/«se suelta» → v0=0; «se detiene»/«punto más alto» → v=0; «caída libre» → a=±9,8. Si el ejercicio no es de cinemática en una dimensión, tipo=otro, datos vacíos y explicá en cuidados qué teoría aplicar. No resuelvas el ejercicio."""


def pedir_ia(texto):
    try:
        clave = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None, "Falta configurar la clave de la IA (ANTHROPIC_API_KEY) en los Secrets de Streamlit."
    if st.session_state.get("n_ia", 0) >= MAX_IA:
        return None, "Llegaste al límite de consultas de esta visita. Probá más tarde o usá «Resolver con datos»."
    try:
        import anthropic
        r = anthropic.Anthropic(api_key=clave).messages.create(
            model=MODEL, max_tokens=1500, system=SISTEMA, messages=[{"role": "user", "content": texto}])
        st.session_state.n_ia = st.session_state.get("n_ia", 0) + 1
        crudo = re.sub(r"^```(?:json)?|```$", "", r.content[0].text.strip()).strip()
        return json.loads(crudo), None
    except Exception as e:
        return None, f"No pude analizar el ejercicio ({type(e).__name__}). Probá de nuevo o reescribilo más corto."


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
    st.markdown(f'<div class="credit">Desarrollador de la App<br><b>Leonardo Olivera</b><br>Bachiller en Agronomía<br>'
                f'<a href="{NOTION_URL}" target="_blank">Ver mi sitio</a></div>', unsafe_allow_html=True)


def datos_validos(d):
    out = {}
    for k in VARS:
        x = (d or {}).get(k)
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            out[k] = x
    return out


# ---------- Páginas ----------
def home():
    st.markdown('<div class="hero"><h1>Física paso a paso</h1><p>Pegá un ejercicio y lo desmenuzo: qué datos tiene, '
                'qué teoría usar y cómo resolverlo sin perderte. Las cuentas las hace un motor exacto, no la IA.</p></div>',
                unsafe_allow_html=True)
    with st.container(key="pegar"):
        st.markdown("#### 1. Pegá tu ejercicio")
        texto = st.text_area("Enunciado", height=120, label_visibility="collapsed", key="enun",
                             placeholder="Ej: Una piedra se deja caer desde un puente y tarda 3 s en llegar al agua. ¿Qué altura tiene el puente?")
        if st.button("Desmenuzar ejercicio", type="primary", disabled=len(texto.strip()) < 15):
            with st.spinner("Leyendo el enunciado…"):
                st.session_state.analisis = pedir_ia(texto)
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
                        st.markdown(f'<div class="frase">{chip(num_txt(k, nsimplify(str(f.get("valor", 0)), rational=True)), VARS[k][4])} '
                                    f'<i>«{f.get("frase", "")}»</i><br>{f.get("por_que", "")}</div>', unsafe_allow_html=True)
                d = datos_validos(info.get("datos"))
                inc = info.get("incognita")
                if inc in VARS:
                    st.markdown(f"**Qué te piden:** {chip(VARS[inc][1] + ' · ' + VARS[inc][2], VARS[inc][4])}", unsafe_allow_html=True)
                for c_ in info.get("cuidados", []):
                    box("warn", "Cuidado", c_)
                if info.get("tipo") == "otro":
                    box("sign", "Tema fuera de esta versión", f"Parece de <b>{info.get('tema', 'otro tema')}</b>. "
                        "Ese módulo está en desarrollo; arriba te dejé la teoría que conviene aplicar.")
                elif len(d) == 3:
                    st.markdown("#### 3. Resolución")
                    mostrar(d)
                    st.button("Editar estos datos", on_click=cargar, args=(d,), key="ed")
                else:
                    box("sign", "Revisá los datos", f"Detecté {len(d)} datos y hacen falta exactamente 3. "
                        "Corregilos en «Resolver con datos».")
                    st.button("Abrir con estos datos", on_click=cargar, args=(d,), key="ed")
    st.markdown("#### O elegí un tema")
    cols = st.columns(3, gap="large")
    for col_, (anio, temas) in zip(cols, PLAN.items()):
        with col_:
            st.markdown(f'<div class="plan-h">{anio}</div>', unsafe_allow_html=True)
            for nombre, resumen in temas:
                listo = nombre == "Cinemática"
                st.button(("▶ " if listo else "") + nombre + ("" if listo else " · pronto"), disabled=not listo,
                          on_click=ir, args=("cinematica",), use_container_width=True, key=f"t_{nombre}")
                st.markdown(f'<div class="cap">{resumen}</div>', unsafe_allow_html=True)
    pie()


def preset(**kw):
    for k in VARS:
        st.session_state[f"s_{k}"] = k in kw
        st.session_state[f"n_{k}"] = float(kw.get(k, 0.0))


def cinematica():
    st.button("← Volver al inicio", on_click=volver, key="back")
    st.markdown('<div class="hero"><h1>Cinemática</h1><p>Movimiento en una dimensión: MRU, MRUA, caída libre y tiro vertical.</p></div>',
                unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Teoría", "Resolver con datos"])
    with tab1, st.container(key="teoria"):
        st.markdown("**1. Sistema de referencia.** Elegí un origen y un sentido positivo. Lo que va en ese sentido es **+**, lo contrario es **−**. "
                    "En vertical conviene que + sea hacia arriba.")
        st.markdown("**2. Las cinco magnitudes**")
        st.markdown("".join(chip(f"{x[1]} · {x[2]} ({x[3]})", x[4]) for x in VARS.values()), unsafe_allow_html=True)
        st.markdown("**3. ¿Qué ecuación uso?** En MRUA elegí la que **no tiene** la magnitud que no conocés ni necesitás:")
        for k in VARS:
            st.markdown(f"Sin {chip(VARS[k][1], VARS[k][4])} → *{EQ[k][0]}*", unsafe_allow_html=True)
            st.latex(eq_tex(k, {x: C(x, VARS[x][0]) for x in VARS}))
        st.markdown("**4. MRU:** velocidad constante, a = 0. Alcanza con Δx = v·t.")
        st.markdown("**5. Caída libre y tiro vertical:** a = −g = −9,8 m/s² (con + hacia arriba). «Se suelta» o «reposo» significa v₀ = 0. "
                    "En el punto más alto v = 0. Subir y bajar a la misma altura tarda lo mismo.")
        box("warn", "Errores típicos", "Olvidar el signo de g · no pasar km/h a m/s (dividí entre 3,6) · "
            "no darse cuenta de que «se detiene» es v = 0.")
    with tab2, st.container(key="solver"):
        st.markdown("Marcá **exactamente 3 datos** de los 5 y completá sus valores. Unidades: m, m/s, m/s², s.")
        pc = st.columns(4)
        pc[0].button("Caída libre (reposo, 2 s)", on_click=preset, kwargs=dict(v0=0, a=-9.8, t=2), use_container_width=True)
        pc[1].button("Altura máxima (20 m/s)", on_click=preset, kwargs=dict(v0=20, a=-9.8, v=0), use_container_width=True)
        pc[2].button("Frenado (20 m/s a −5)", on_click=preset, kwargs=dict(v0=20, v=0, a=-5), use_container_width=True)
        pc[3].button("MRU (10 m/s, 5 s)", on_click=preset, kwargs=dict(v0=10, a=0, t=5), use_container_width=True)
        datos = {}
        for col_, k in zip(st.columns(5), VARS):
            with col_.container(key=f"c{k}"):
                st.checkbox("Es dato", key=f"s_{k}")
                x = st.number_input(f"{VARS[k][1]} · {VARS[k][2]} ({VARS[k][3]})", format="%g", step=1.0, key=f"n_{k}",
                                    disabled=not st.session_state[f"s_{k}"])
                if st.session_state[f"s_{k}"]:
                    datos[k] = x
        if len(datos) != 3:
            box("sign", "Faltan o sobran datos", f"Marcaste {len(datos)}. Con exactamente 3 datos el problema queda resuelto.")
        else:
            mostrar(datos)
    pie()


home() if st.session_state.tema == "home" else cinematica()
