import streamlit as st
import numpy as np
import nashpy as nash
import pandas as pd

st.set_page_config(page_title="Calculadora de Nash", layout="centered")

# Encabezado principal con imagen y autoría
col_img, col_tit = st.columns([1, 4])
with col_img:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/John_Forbes_Nash%2C_Jr._by_Peter_Badge.jpg/360px-John_Forbes_Nash%2C_Jr._by_Peter_Badge.jpg",
        caption="John F. Nash Jr.",
        width=100
    )
with col_tit:
    st.title("Calculadora de Equilibrios de Nash")
    st.caption("Microeconomía III — Teoría de Juegos | Desarrollado por Santiago Agüero")

st.markdown("Herramienta interactiva para resolver juegos estáticos en forma normal y determinar equilibrios en estrategias puras y mixtas.")

# Configuración de dimensiones
col_dim1, col_dim2 = st.columns(2)
with col_dim1:
    filas = st.number_input("Filas (Estrategias Jugador 1)", min_value=2, max_value=6, value=3, step=1)
with col_dim2:
    cols = st.number_input("Columnas (Estrategias Jugador 2)", min_value=2, max_value=6, value=3, step=1)

st.subheader("Matriz de Pagos")
st.caption("Formato de entrada por celda: `pago1, pago2` (ej. `0, 4` o `6, 6`).")

# Valores por defecto para matriz 3x3 de ejemplo
default_vals = [
    ["0, 4", "4, 0", "5, 3"],
    ["4, 0", "0, 4", "5, 3"],
    ["3, 5", "3, 5", "6, 6"]
]

# Crear grilla de inputs
grid_inputs = []
for i in range(filas):
    cols_ui = st.columns(cols)
    row_vals = []
    for j in range(cols):
        with cols_ui[j]:
            def_val = default_vals[i][j] if i < 3 and j < 3 else "0, 0"
            val = st.text_input(f"F{i+1}, C{j+1}", value=def_val, key=f"cell_{i}_{j}")
            row_vals.append(val)
    grid_inputs.append(row_vals)

if st.button("Calcular Equilibrios", type="primary", use_container_width=True):
    try:
        A = np.zeros((filas, cols), dtype=float)
        B = np.zeros((filas, cols), dtype=float)
        
        for i in range(filas):
            for j in range(cols):
                raw = grid_inputs[i][j].strip()
                partes = [p.strip() for p in raw.split(",") if p.strip()]
                if len(partes) != 2:
                    st.error(f"Error en casilla F{i+1}, C{j+1}: formato inválido. Use dos números separados por coma.")
                    st.stop()
                A[i, j] = float(partes[0])
                B[i, j] = float(partes[1])
        
        juego = nash.Game(A, B)
        equilibrios = list(juego.support_enumeration())
        
        st.divider()
        st.subheader("Resultados")
        
        if not equilibrios:
            st.warning("No se encontraron equilibrios con el algoritmo estándar.")
        else:
            puros = []
            mixtos = []
            
            for s_r, s_c in equilibrios:
                es_pura_r = np.any(np.isclose(s_r, 1.0))
                es_pura_c = np.any(np.isclose(s_c, 1.0))
                
                if es_pura_r and es_pura_c:
                    f = int(np.argmax(s_r))
                    c = int(np.argmax(s_c))
                    puros.append((f + 1, c + 1, A[f, c], B[f, c]))
                else:
                    eu1 = s_r @ A @ s_c
                    eu2 = s_r @ B @ s_c
                    mixtos.append((s_r, s_c, eu1, eu2))
            
            # Mostrar equilibrios puros
            if puros:
                st.write("**Equilibrio(s) de Nash en Estrategias Puras:**")
                for f, c, u1, u2 in puros:
                    st.success(f"Estrategia: **(Fila {f}, Columna {c})** | Pagos: **({u1:g}, {u2:g})**")
            else:
                st.info("No existen equilibrios de Nash en estrategias puras.")
                
            # Mostrar equilibrios mixtos
            if mixtos:
                st.write("**Equilibrio(s) en Estrategias Mixtas:**")
                for idx, (s_r, s_c, eu1, eu2) in enumerate(mixtos, 1):
                    with st.expander(f"Equilibrio Mixto #{idx}", expanded=True):
                        col_m1, col_m2 = st.columns(2)
                        with col_m1:
                            st.write("**Probabilidades Jugador 1:**")
                            df_j1 = pd.DataFrame({"Estrategia": [f"Fila {k+1}" for k in range(filas)], "Probabilidad": s_r})
                            st.dataframe(df_j1, hide_index=True)
                            st.write(f"Pago esperado J1: **{eu1:.2f}**")
                        with col_m2:
                            st.write("**Probabilidades Jugador 2:**")
                            df_j2 = pd.DataFrame({"Estrategia": [f"Columna {k+1}" for k in range(cols)], "Probabilidad": s_c})
                            st.dataframe(df_j2, hide_index=True)
                            st.write(f"Pago esperado J2: **{eu2:.2f}**")
                            
    except Exception as e:
        st.error(f"Error en el cálculo: {e}")

# Pie de página
st.markdown("---")
st.caption("Desarrollado para Microeconomía III · Facultad de Ciencias Económicas")