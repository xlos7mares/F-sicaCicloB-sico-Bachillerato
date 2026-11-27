def mediciones():
    st.button("← Volver al inicio", on_click=volver, key="back_med")
    st.markdown(
        '<div class="hero"><h1>Mediciones e Incertidumbre</h1>'
        '<p>Base fundamental de Física: magnitudes, Sistema Internacional (SI), '
        'cifras significativas, exactitud vs. precisión y tratamiento de errores.</p></div>',
        unsafe_allow_html=True,
    )
    tab1, tab2, tab3 = st.tabs(["Fundamentos y SI", "Errores y Cifras Significativas", "Laboratorio Interactivo"])

    with tab1, st.container(key="teoria_tab1"):
        st.markdown("### 1. ¿Qué es medir y por qué importa en Física?")
        st.markdown(
            "Medir es **comparar** una magnitud física con un patrón o unidad de referencia aceptada. "
            "Ninguna medición humana ni de instrumento es infinitamente exacta: siempre existe una **incertidumbre** "
            "(por la mínima división del instrumento, el tiempo de reacción, las condiciones del entorno o la variabilidad del fenómeno)."
        )
        box(
            "sign",
            "Ejemplo concreto en el laboratorio / práctica",
            "Si medís una longitud con una regla graduada cada <b>1 mm</b>, el valor más fino que podés leer "
            "directamente es 1 mm. Si tomás varias mediciones repetidas de un tiempo o una masa y obtenés valores "
            "ligeramente distintos, necesitás calcular el promedio y su incertidumbre para expresar bien el resultado.",
        )

        st.markdown("### 2. Magnitudes fundamentales del Sistema Internacional (SI)")
        st.markdown(
            "| Magnitud | Símbolo | Unidad SI | Símbolo unidad | Ejemplo de uso |\n"
            "| :--- | :---: | :--- | :---: | :--- |\n"
            "| Longitud | $l, d, x$ | metro | $\\text{m}$ | Distancia recorrida, altura o espesor |\n"
            "| Masa | $m$ | kilogramo | $\\text{kg}$ | Masa de un cuerpo o muestra |\n"
            "| Tiempo | $t$ | segundo | $\\text{s}$ | Duración de un movimiento o ensayo |\n"
            "| Temperatura termodinámica | $T$ | kelvin | $\\text{K}$ | Temperatura de un sistema |\n"
            "| Corriente eléctrica | $I$ | ampere | $\\text{A}$ | Intensidad en un circuito |\n"
            "| Cantidad de sustancia | $n$ | mol | $\\text{mol}$ | Cantidad de materia |\n"
            "| Intensidad luminosa | $I_v$ | candela | $\\text{cd}$ | Flujo luminoso en una dirección |"
        )

        st.markdown("### 3. Prefijos y conversiones rápidas al SI")
        st.markdown(
            "En Física casi siempre conviene pasar todo a unidades del **SI** antes de operar en fórmulas:"
        )
        st.latex(r"1\ \text{km} = 10^3\ \text{m} \qquad 1\ \text{cm} = 10^{-2}\ \text{m} \qquad 1\ \text{mm} = 10^{-3}\ \text{m}")
        st.latex(r"1\ \text{min} = 60\ \text{s} \qquad 1\ \text{h} = 3600\ \text{s} \qquad \frac{v\ [\text{km/h}]}{3{,}6} = v\ [\text{m/s}]")
        st.latex(r"1\ \text{ha} = 10\,000\ \text{m}^2 \qquad 1\ \text{L} = 10^{-3}\ \text{m}^3 = 1\ \text{dm}^3")

    with tab2, st.container(key="teoria_tab2"):
        st.markdown("### 4. Exactitud vs. Precisión")
        st.markdown(
            "* **Precisión:** qué tan cerca están entre sí varias mediciones repetidas (poca dispersión, repetibilidad). Depende mucho del instrumento y de la técnica.\n"
            "* **Exactitud:** qué tan cerca está el valor medido del **valor verdadero** o de referencia (ausencia de errores sistemáticos, como un instrumento mal calibrado o un cero corrido)."
        )
        box(
            "warn",
            "Trampa clásica",
            "Podés tener un instrumento muy **preciso** (marca siempre `14,20 °C`, `14,21 °C`, `14,20 °C`), pero poco **exacto** si está descalibrado y el valor de referencia es `16,5 °C` (error sistemático).",
        )

        st.markdown("### 5. Cifras significativas (c.s.) — reglas prácticas")
        st.markdown(
            "Las cifras significativas de una medida incluyen todos los dígitos seguros más el primer dígito estimado:\n"
            "1. Todos los dígitos distintos de cero **son significativos** (`48,25 m` → **4 c.s.**).\n"
            "2. Los ceros **entre** cifras distintas de cero **son significativos** (`1004 s` → **4 c.s.**).\n"
            "3. Los ceros **a la izquierda** del primer dígito distinto de cero **NO son significativos** (`0,0035 kg` → solo **2 c.s.**: el `3` y el `5`).\n"
            "4. Los ceros **a la derecha** con coma decimal **SÍ son significativos** (`2,50 m` → **3 c.s.**)."
        )

        st.markdown("### 6. Error absoluto, relativo y porcentual")
        st.latex(r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i \qquad \Delta x = \max_i |x_i - \bar{x}| \quad (\text{o incerteza del instrumento})")
        st.latex(r"E_{\text{rel}} = \frac{\Delta x}{\bar{x}} \qquad E_{\text{rel\%}} = \frac{\Delta x}{\bar{x}} \cdot 100")
        st.markdown("El resultado final se expresa como: **valor medido = $(\bar{x} \pm \Delta x)\ \text{unidad}$**.")

        st.markdown("### 7. Ayuda audiovisual en YouTube (docentes de Física)")
        st.markdown(
            "Como refuerzo visual, podés repasar estos temas en canales docentes de Física en español:"
        )
        c1, c2 = st.columns(2)
        with c1:
            box(
                "sign",
                "Prof. Sergio Llanos · Mediciones, SI y errores",
                "Explicaciones directas y paso a paso de unidades, notación científica, cifras significativas y errores de medición.<br>"
                "<a href='https://www.youtube.com/results?search_query=Sergio+Llanos+cifras+significativas+errores+medicion' target='_blank'>▶ Buscar en YouTube: Sergio Llanos (Mediciones y errores)</a>",
            )
        with c2:
            box(
                "hint",
                "Física con Gustavo · Incertidumbre y propagación de errores",
                "Ideal para afianzar promedio, error absoluto, error relativo y cómo escribir bien un resultado experimental.<br>"
                "<a href='https://www.youtube.com/results?search_query=Fisica+con+Gustavo+error+absoluto+relativo+porcentual' target='_blank'>▶ Buscar en YouTube: Física con Gustavo (Errores)</a>",
            )

    with tab3, st.container(key="solver_med"):
        st.markdown("### 8. Calculadora de serie de mediciones y gráfico de dispersión")
        st.markdown("Ingresá tus mediciones separadas por coma (o usá el ejemplo rápido).")
        if st.button("Cargar ejemplo (5 mediciones)", key="btn_ej_med"):
            st.session_state["med_raw"] = "12.4, 12.6, 12.2, 12.5, 12.3"
            st.session_state["med_uni"] = "s"

        raw = st.text_input(
            "Mediciones separadas por coma",
            value=st.session_state.get("med_raw", "12.4, 12.6, 12.2, 12.5, 12.3"),
            key="med_raw_input",
        )
        unidad = st.text_input(
            "Unidad (ej: s, m, mm, kg, °C)",
            value=st.session_state.get("med_uni", "s"),
            key="med_uni_input",
        )
        try:
            vals = [float(x.strip().replace(",", ".")) for x in raw.split(",") if x.strip()]
        except ValueError:
            vals = []

        if len(vals) < 2:
            box("sign", "Ingresá al menos 2 valores", "Ejemplo: 12.4, 12.6, 12.2, 12.5, 12.3")
        else:
            arr = np.array(vals, dtype=float)
            prom = float(np.mean(arr))
            err_abs = float(np.max(np.abs(arr - prom)))
            err_pct = (err_abs / abs(prom) * 100) if prom != 0 else 0.0
            err_rel = (err_abs / abs(prom)) if prom != 0 else 0.0

            st.markdown(
                f'<div class="ok">Resultado: <b>({prom:.4g} ± {err_abs:.4g}) {unidad}</b> · '
                f'Error relativo: <b>{err_rel:.4g}</b> · Error porcentual: <b>{err_pct:.2f}%</b></div>',
                unsafe_allow_html=True,
            )

            muestras = [f"M{i+1}" for i in range(len(arr))]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=muestras,
                y=arr,
                mode="markers+lines",
                name="Medición individual",
                marker=dict(size=10, color="#22e3ff"),
                line=dict(color="#22e3ff", width=2),
            ))
            fig.add_hline(y=prom, line_dash="solid", line_color="#b8ff2c", annotation_text=f"Promedio ({prom:.4g})")
            if err_abs > 0:
                fig.add_hrect(
                    y0=prom - err_abs,
                    y1=prom + err_abs,
                    fillcolor="rgba(184, 255, 44, 0.14)",
                    line_width=0,
                    annotation_text=f"Banda ±{err_abs:.4g}",
                )
            fig.update_layout(
                title=dict(text=f"Dispersión de mediciones ({unidad})", font=dict(color="#e8ecff", size=14)),
                height=310,
                margin=dict(l=8, r=8, t=42, b=8),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,.25)",
                xaxis=dict(color="#aab3e6"),
                yaxis=dict(title=unidad, color="#aab3e6", gridcolor="rgba(255,255,255,.08)"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

    pie()
