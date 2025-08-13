import streamlit as st, pandas as pd
from db import SessionLocal
from models import Investment

st.set_page_config(page_title="Inversiones", page_icon="📈", layout="wide")
sess = SessionLocal()
st.title("📈 Inversiones")

with st.form("inv_form"):
    col1, col2, col3, col4 = st.columns(4)
    asset = col1.text_input("Activo", "ETF MSCI World")
    broker = col2.text_input("Bróker", "DEGIRO")
    invested = col3.number_input("Invertido (€)", min_value=0.0, step=50.0)
    curr = col4.number_input("Valor actual (€)", min_value=0.0, step=50.0)
    if st.form_submit_button("Guardar inversión"):
        inv = Investment(asset=asset, broker=broker, invested=float(invested), current_value=float(curr))
        sess.add(inv); sess.commit(); st.success("Guardado")

st.markdown("---")
rows = sess.query(Investment).all()
df = pd.DataFrame([{"id":r.id,"asset":r.asset,"broker":r.broker,"invested":r.invested,"current_value":r.current_value,"updated_at":r.updated_at} for r in rows])
st.dataframe(df, use_container_width=True, hide_index=True)

if not df.empty:
    df["retorno_%"] = (df["current_value"] - df["invested"]) / df["invest
