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
.hero p{color:#aab3e6;max-width:760px;margin:4px 0 14px;font-size:1.05rem}
.st-key-pegar,.st-key-teoria,.st-key-solver,.st-key-resul{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.12);border-radius:24px;padding:20px 24px;backdrop-filter:blur(14px)}
.st-key-pegar{border-color:#22e3ff88;box-shadow:0 0 40px -14px #22e3ff}
textarea{background:rgba(0,0,0,.4)!important;color:#e8ecff!important;border-radius:14px!important;font-size:1.02rem!important}
div[data-baseweb="textarea"]{border:1.5px solid #22e3ff!important;border-radius:14px!important;background:rgba(0,0,0,.4)!important}
div[data-baseweb="textarea"]:focus-within{box-shadow:0 0 0 3px #22e3ff44,0 0 28px #22e3ff}
.plan-h{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.25rem;color:#ffe14a;text-shadow:0 0 12px #ffe14a77;margin:6px 0 2px}
.cap{color:#8d97cf;font-size:.8rem;margin:-6px 0 8px;line-height:1.3}
.chip{display:inline-block;padding:1px 11px;margin:2px 3px 2px 0;border-radius:999px;color:var(--k);font-weight:700;background:color-mix(in srgb,var(--k) 14%,transparent);border:1px solid var(--k);text-shadow:0 0 10px var(--k)}
.hint,.warn,.sign,.ok{margin:10px 0 4px;padding:12px 14px;border-radius:14px;line-height:1.55}
.hint{background:rgba(255,225,74,.08);border-left:3px solid #ffe14a;color:#f3f0d0}
.warn{background:rgba(255,79,216,.09);border-left:3px solid #ff4fd8;color:#ffd6f6}.warn b{color:#ff4fd8}
.sign{background:rgba(34,227,255,.09);border-left:3px solid #22e3ff;color:#d4f8ff}.sign b{color:#22e3ff}
.ok{background:rgba(184,255,44,.1);border:1px solid #b8ff2c;color:#e6ffb3;box-shadow:0 0 24px -8px #b8ff2c;font-size:1.08rem}
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
__VARCSS__</style>""".replace("__VARCSS
