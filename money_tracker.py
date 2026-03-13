import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="MoneyTracker", page_icon="💸", layout="wide")

def cargar_datos():
    if os.path.exists('finanzas.json'):
        try:
            with open('finanzas.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_datos(datos):
    with open('finanzas.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def color_cantidad(valor):
    if isinstance(valor, (int, float)):
        if valor < 0: return 'color: #ff4b4b;' # Rojo Streamlit
        if valor > 0: return 'color: #29b09d;' # Verde Streamlit
    return ''

# Inicialización
if 'movimientos' not in st.session_state:
    st.session_state.movimientos = cargar_datos()

# --- 2. INTERFAZ DE USUARIO (Sidebar y Título) ---
st.title("💸 MoneyTracker: Tu Gestión Financiera")

with st.expander("➕ Registrar Nuevo Movimiento", expanded=False):
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            concepto = st.text_input("Concepto", placeholder="Ej: Compra Mercadona")
            cantidad = st.number_input("Cantidad (€)", min_value=0.01, step=0.01)
        with col2:
            tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
            cat_opciones = ["Comida", "Vivienda", "Transporte", "Ocio", "Sueldo", "Otros"]
            categoria = st.selectbox("Categoría", cat_opciones)
        
        fecha = st.date_input("Fecha", datetime.now(), format="DD/MM/YYYY")
        
        if st.form_submit_button("Añadir Movimiento"):
            valor_final = cantidad if tipo == "Ingreso" else -cantidad
            nuevo = {
                "Fecha": fecha.strftime("%d/%m/%Y"),
                "Concepto": concepto,
                "Tipo": tipo,
                "Cantidad": valor_final,
                "Categoria": categoria
            }
            st.session_state.movimientos.append(nuevo)
            guardar_datos(st.session_state.movimientos)
            st.success("✅ Registro guardado")
            st.rerun()

# --- 3. LÓGICA DE NEGOCIO Y DASHBOARD ---
if st.session_state.movimientos:
    df = pd.DataFrame(st.session_state.movimientos)
    
    # Métricas principales
    ingresos = df[df["Cantidad"] > 0]["Cantidad"].sum()
    gastos = df[df["Cantidad"] < 0]["Cantidad"].sum()
    balance = ingresos + gastos

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Totales", f"{ingresos:.2f} €")
    c2.metric("Gastos Totales", f"{abs(gastos):.2f} €", delta_color="inverse")
    c3.metric("Balance Neto", f"{balance:.2f} €")

    st.divider()

    # --- 4. VISUALIZACIÓN ---
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.subheader("📋 Historial")
        st.dataframe(
            df.style.map(color_cantidad, subset=["Cantidad"])
                    .format({"Cantidad": "{:.2f} €"}),
            use_container_width=True,
            hide_index=True
        )
        
        # Sección de borrado dentro de la columna para optimizar espacio
        with st.popover("🗑️ Eliminar Registros"):
            opciones = [f"{i}: {m['Concepto']} ({m['Fecha']})" for i, m in enumerate(st.session_state.movimientos)]
            seleccion = st.selectbox("Selecciona para eliminar:", opciones)
            if st.button("Confirmar Borrado", type="primary"):
                idx = int(seleccion.split(":")[0])
                st.session_state.movimientos.pop(idx)
                guardar_datos(st.session_state.movimientos)
                st.rerun()

    with col_der:
        st.subheader("📊 Gastos por Categoría")
        df_gastos = df[df["Cantidad"] < 0]
        if not df_gastos.empty:
            resumen = df_gastos.groupby("Categoria")["Cantidad"].sum().abs()
            st.bar_chart(resumen)
        else:
            st.info("No hay gastos registrados.")
else:
    st.info("👋 ¡Bienvenido! Registra tu primer movimiento para empezar.")