import streamlit as st
import pulp
import pandas as pd

st.set_page_config(page_title="American Steel Optimizer", layout="centered")
st.title("🧮 American Steel Company - Optimización de Costos")

# =======================
# DATOS POR DEFECTO
# =======================

# Minas con tipo, costo y límites

with open("Manual_Usuario.pdf.pdf", "rb") as f:
    st.download_button("📖 Abrir Manual de Usuario", f, file_name="Manual_Usuario.pdf.pdf")
minas = {
    "Butte": {"tipo": "A", "compra": 130, "envio": {"Pittsburg": 10, "Youngstown": 13}, "limite": 1000},
    "Cheyenne": {"tipo": "B", "compra": 110, "envio": {"Pittsburg": 14, "Youngstown": 17}, "limite": 2000}
}

# Plantas con capacidad y costos
plantas = {
    "Pittsburg": {"capacidad": 700, "proceso": {"alto": 32, "bajo": 27}},
    "Youngstown": {"capacidad": 1500, "proceso": {"alto": 39, "bajo": 32}}
}

# Mezclas para tipos de acero
mezclas = {
    "alto": {"A": 1, "B": 2},
    "bajo": {"A": 1, "B": 3}
}

# Demanda y costos de envío del producto terminado
paises = {
    "Japón":    {"alto": 400, "bajo": 200, "envio": {"Pittsburg": {"alto": 110, "bajo": 100}, "Youngstown": {"alto": 115, "bajo": 110}}},
    "Corea":    {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 140, "bajo": 130}, "Youngstown": {"alto": 150, "bajo": 145}}},
    "Taiwán":   {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 130, "bajo": 125}, "Youngstown": {"alto": 135, "bajo": 127}}},
    "México":   {"alto": 150, "bajo": 50,  "envio": {"Pittsburg": {"alto": 80, "bajo": 80},   "Youngstown": {"alto": 90, "bajo": 85}}}
}

# =======================
# ENTRADAS DINÁMICAS
# =======================

def init_session_state():
    if "minas" not in st.session_state:
        st.session_state["minas"] = {
            "Butte": {"tipo": "A", "compra": 130, "envio": {"Pittsburg": 10, "Youngstown": 13}, "limite": 1000},
            "Cheyenne": {"tipo": "B", "compra": 110, "envio": {"Pittsburg": 14, "Youngstown": 17}, "limite": 2000}
        }
    if "plantas" not in st.session_state:
        st.session_state["plantas"] = {
            "Pittsburg": {"capacidad": 700, "proceso": {"alto": 32, "bajo": 27}},
            "Youngstown": {"capacidad": 1500, "proceso": {"alto": 39, "bajo": 32}}
        }
    if "mezclas" not in st.session_state:
        st.session_state["mezclas"] = {
            "alto": {"A": 1, "B": 2},
            "bajo": {"A": 1, "B": 3}
        }
    if "paises" not in st.session_state:
        st.session_state["paises"] = {
            "Japón":    {"alto": 400, "bajo": 200, "envio": {"Pittsburg": {"alto": 110, "bajo": 100}, "Youngstown": {"alto": 115, "bajo": 110}}},
            "Corea":    {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 140, "bajo": 130}, "Youngstown": {"alto": 150, "bajo": 145}}},
            "Taiwán":   {"alto": 200, "bajo": 100, "envio": {"Pittsburg": {"alto": 130, "bajo": 125}, "Youngstown": {"alto": 135, "bajo": 127}}},
            "México":   {"alto": 150, "bajo": 50,  "envio": {"Pittsburg": {"alto": 80, "bajo": 80},   "Youngstown": {"alto": 90, "bajo": 85}}}
        }

init_session_state()

# Formulario para editar minas
def minas_form():
    st.subheader("Minas")
    minas = st.session_state["minas"]
    to_delete = []
    for nombre, datos in minas.items():
        with st.expander(f"{nombre}"):
            new_nombre = st.text_input(f"Nombre mina", value=nombre, key=f"minaname_{nombre}")
            tipo = st.selectbox(f"Tipo", ["A", "B"], index=["A", "B"].index(datos["tipo"]), key=f"minatipo_{nombre}")
            compra = st.number_input(f"Costo compra", value=datos["compra"], key=f"minacompra_{nombre}")
            limite = st.number_input(f"Límite", value=datos["limite"], key=f"minalimite_{nombre}")
            envio = {}
            for planta in st.session_state["plantas"]:
                envio[planta] = st.number_input(f"Envío a {planta}", value=datos["envio"].get(planta, 0), key=f"minaenvio_{nombre}_{planta}")
            if st.button(f"Eliminar mina {nombre}"):
                to_delete.append(nombre)
            # Actualizar datos
            minas[new_nombre] = {"tipo": tipo, "compra": compra, "envio": envio, "limite": limite}
            if new_nombre != nombre:
                to_delete.append(nombre)
    for nombre in to_delete:
        if nombre in minas:
            del minas[nombre]
    if st.button("Agregar mina"):
        minas[f"Mina{len(minas)+1}"] = {"tipo": "A", "compra": 0, "envio": {pl: 0 for pl in st.session_state["plantas"]}, "limite": 0}
    st.session_state["minas"] = minas

# Formulario para editar plantas
def plantas_form():
    st.subheader("Plantas")
    plantas = st.session_state["plantas"]
    to_delete = []
    for nombre, datos in plantas.items():
        with st.expander(f"{nombre}"):
            new_nombre = st.text_input(f"Nombre planta", value=nombre, key=f"plantaname_{nombre}")
            capacidad = st.number_input(f"Capacidad", value=datos["capacidad"], key=f"plantacap_{nombre}")
            proceso = {}
            for t in ["alto", "bajo"]:
                proceso[t] = st.number_input(f"Costo proceso {t}", value=datos["proceso"].get(t, 0), key=f"plantaproc_{nombre}_{t}")
            if st.button(f"Eliminar planta {nombre}"):
                to_delete.append(nombre)
            plantas[new_nombre] = {"capacidad": capacidad, "proceso": proceso}
            if new_nombre != nombre:
                to_delete.append(nombre)
    for nombre in to_delete:
        if nombre in plantas:
            del plantas[nombre]
    if st.button("Agregar planta"):
        plantas[f"Planta{len(plantas)+1}"] = {"capacidad": 0, "proceso": {"alto": 0, "bajo": 0}}
    st.session_state["plantas"] = plantas

# Formulario para editar mezclas
def mezclas_form():
    st.subheader("Mezclas de acero")
    mezclas = st.session_state["mezclas"]
    for t in ["alto", "bajo"]:
        with st.expander(f"Mezcla {t}"):
            for tipo in ["A", "B"]:
                mezclas[t][tipo] = st.number_input(f"{t} - {tipo}", value=mezclas[t][tipo], key=f"mezcla_{t}_{tipo}")
    st.session_state["mezclas"] = mezclas

# Formulario para editar países
def paises_form():
    st.subheader("Países destino")
    paises = st.session_state["paises"]
    to_delete = []
    for nombre, datos in paises.items():
        with st.expander(f"{nombre}"):
            new_nombre = st.text_input(f"Nombre país", value=nombre, key=f"paisname_{nombre}")
            alto = st.number_input(f"Demanda alto", value=datos["alto"], key=f"paisalto_{nombre}")
            bajo = st.number_input(f"Demanda bajo", value=datos["bajo"], key=f"paisbajo_{nombre}")
            envio = {}
            for planta in st.session_state["plantas"]:
                envio[planta] = {}
                for t in ["alto", "bajo"]:
                    envio[planta][t] = st.number_input(f"Envío {planta} {t}", value=datos["envio"].get(planta, {}).get(t, 0), key=f"paisenvio_{nombre}_{planta}_{t}")
            if st.button(f"Eliminar país {nombre}"):
                to_delete.append(nombre)
            paises[new_nombre] = {"alto": alto, "bajo": bajo, "envio": envio}
            if new_nombre != nombre:
                to_delete.append(nombre)
    for nombre in to_delete:
        if nombre in paises:
            del paises[nombre]
    if st.button("Agregar país"):
        paises[f"País{len(paises)+1}"] = {"alto": 0, "bajo": 0, "envio": {pl: {"alto": 0, "bajo": 0} for pl in st.session_state["plantas"]}}
    st.session_state["paises"] = paises

# Mostrar formularios
# Quitar el expander externo para evitar anidación
minas_form()
plantas_form()
mezclas_form()
paises_form()

# Usar los datos editados
minas = st.session_state["minas"]
plantas = st.session_state["plantas"]
mezclas = st.session_state["mezclas"]
paises = st.session_state["paises"]

# =======================
# SUMAR/RESTAR VARIABLES ANTES DE RESOLVER
# =======================

st.sidebar.header("➕➖ Sumar/Restar variables")

# Minas
if st.sidebar.button("+ Agregar mina"):
    minas[f"Mina{len(minas)+1}"] = {"tipo": "A", "compra": 0, "envio": {pl: 0 for pl in plantas}, "limite": 0}
if st.sidebar.button("- Quitar mina") and len(minas) > 1:
    minas.pop(list(minas.keys())[-1])

# Plantas
if st.sidebar.button("+ Agregar planta"):
    plantas[f"Planta{len(plantas)+1}"] = {"capacidad": 0, "proceso": {"alto": 0, "bajo": 0}}
if st.sidebar.button("- Quitar planta") and len(plantas) > 1:
    plantas.pop(list(plantas.keys())[-1])

# Países
if st.sidebar.button("+ Agregar país"):
    paises[f"País{len(paises)+1}"] = {"alto": 0, "bajo": 0, "envio": {pl: {"alto": 0, "bajo": 0} for pl in plantas}}
if st.sidebar.button("- Quitar país") and len(paises) > 1:
    paises.pop(list(paises.keys())[-1])

# Mezclas (solo sumar/restar tipos si lo deseas, pero normalmente son fijos)

st.session_state["minas"] = minas
st.session_state["plantas"] = plantas
st.session_state["paises"] = paises

# =======================
# RESOLUCIÓN Y TABLAS BONITAS
# =======================

if st.button("🔍 Resolver modelo"):
    with st.spinner("Calculando solución óptima..."):
        modelo = pulp.LpProblem("American_Steel_Optimization", pulp.LpMinimize)

        # VARIABLES
        envio_mineral = pulp.LpVariable.dicts("envioMineral",
            [(m, p) for m in minas for p in plantas], lowBound=0)

        produccion = pulp.LpVariable.dicts("produccion",
            [(p, t) for p in plantas for t in ["alto", "bajo"]], lowBound=0)

        distribucion = pulp.LpVariable.dicts("distribucion",
            [(p, c, t) for p in plantas for c in paises for t in ["alto", "bajo"]], lowBound=0)

        # OBJETIVO: compra + envío mineral + procesamiento + distribución
        modelo += (
            pulp.lpSum(
                envio_mineral[m, p] * (minas[m]["compra"] + minas[m]["envio"][p])
                for m in minas for p in plantas
            ) +
            pulp.lpSum(
                produccion[p, t] * plantas[p]["proceso"][t]
                for p in plantas for t in ["alto", "bajo"]
            ) +
            pulp.lpSum(
                distribucion[p, c, t] * paises[c]["envio"][p][t]
                for p in plantas for c in paises for t in ["alto", "bajo"]
            )
        )

        # RESTRICCIONES
        for m in minas:
            modelo += pulp.lpSum(envio_mineral[m, p] for p in plantas) <= minas[m]["limite"]
        for p in plantas:
            modelo += pulp.lpSum(envio_mineral[m, p] for m in minas) <= plantas[p]["capacidad"]
        for p in plantas:
            for t in ["alto", "bajo"]:
                req_A = mezclas[t]["A"]
                req_B = mezclas[t]["B"]
                total_req = req_A + req_B
                A_disponible = pulp.lpSum(envio_mineral[m, p] for m in minas if minas[m]["tipo"] == "A")
                B_disponible = pulp.lpSum(envio_mineral[m, p] for m in minas if minas[m]["tipo"] == "B")
                modelo += A_disponible >= produccion[p, t] * (req_A / total_req)
                modelo += B_disponible >= produccion[p, t] * (req_B / total_req)
        for p in plantas:
            for t in ["alto", "bajo"]:
                modelo += pulp.lpSum(distribucion[p, c, t] for c in paises) <= produccion[p, t]
        for c in paises:
            for t in ["alto", "bajo"]:
                modelo += pulp.lpSum(distribucion[p, c, t] for p in plantas) == paises[c][t]

        modelo.solve()

        if pulp.LpStatus[modelo.status] == "Optimal":
            st.success(f"Solución óptima encontrada. Costo total: ${pulp.value(modelo.objective):,.2f}")
            # TABLAS BONITAS
            st.subheader("📦 Distribución de Acero (tabla)")
            rows = []
            for p in plantas:
                for c in paises:
                    for t in ["alto", "bajo"]:
                        val = distribucion[p, c, t].varValue
                        if val > 0:
                            rows.append({"Planta": p, "País": c, "Tipo": t, "Toneladas": val})
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay distribución positiva.")

            st.subheader("🚚 Envío de mineral (tabla)")
            rows = []
            for m in minas:
                for p in plantas:
                    val = envio_mineral[m, p].varValue
                    if val > 0:
                        rows.append({"Mina": m, "Planta": p, "Toneladas": val})
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay envío de mineral positivo.")

            st.subheader("🏭 Producción por planta (tabla)")
            rows = []
            for p in plantas:
                for t in ["alto", "bajo"]:
                    val = produccion[p, t].varValue
                    if val > 0:
                        rows.append({"Planta": p, "Tipo": t, "Toneladas": val})
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay producción positiva.")
        else:
            st.error("⚠️ No se encontró una solución óptima.")
