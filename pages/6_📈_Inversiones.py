import streamlit as st, pandas as pd
from db import SessionLocal
from models import Investment

st.set_page_config(page_title="Inversiones", page_icon="📈", layout="wide")
sess = SessionLocal()
st.title("📈 Inversiones")

# ── Formulario: agregar inversión
with st.form("inv_form"):
    col1, col2, col3, col4 = st.columns(4)
    asset = col1.text_input("Activo", "ETF MSCI World")
    broker = col2.text_input("Bróker", "DEGIRO")
    invested = col3.number_input("Invertido (€)", min_value=0.0, step=50.0)
    curr = col4.number_input("Valor actual (€)", min_value=0.0, step=50.0)
    if st.form_submit_button("Guardar inversión"):
        inv = Investment(asset=asset, broker=broker, invested=float(invested), current_value=float(curr))
        sess.add(inv)
        sess.commit()
        st.success("Guardado")

st.markdown("---")

# ── Tabla
rows = sess.query(Investment).all()
df = pd.DataFrame([
    {
        "id": r.id,
        "asset": r.asset,
        "broker": r.broker,
        "invested": r.invested,
        "current_value": r.current_value,
        "updated_at": r.updated_at
    } for r in rows
])

st.dataframe(df, use_container_width=True, hide_index=True)

# ── Métricas
if not df.empty:
    # Evitar división por cero y valores nulos
    df["retorno_%"] = df.apply(
        lambda x: ((x["current_value"] - x["invested"]) / x["invested"] * 100.0) if x["invested"] else 0.0,
        axis=1
    )
    total_invertido = float(df["invested"].sum())
    total_valor = float(df["current_value"].sum())
    retorno_medio = float(df["retorno_%"].mean()) if not df["retorno_%"].empty else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Inversión total", f"{total_invertido:,.2f} €")
    c2.metric("Valor total", f"{total_valor:,.2f} €")
    c3.metric("Retorno medio", f"{retorno_medio:.2f}%")
else:
    st.info("Aún no hay inversiones registradas.")
