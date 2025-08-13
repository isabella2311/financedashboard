import streamlit as st, pandas as pd
from db import SessionLocal
from models import Debt

st.set_page_config(page_title="Deudas", page_icon="💳", layout="wide")
sess = SessionLocal()
st.title("💳 Deudas")

with st.form("debt_form"):
    col1, col2, col3, col4, col5 = st.columns(5)
    name = col1.text_input("Nombre", "Tarjeta Visa")
    principal = col2.number_input("Capital", min_value=0.0, step=50.0)
    rate = col3.number_input("Tasa anual efectiva (%)", min_value=0.0, step=0.1)
    min_payment = col4.number_input("Pago mínimo", min_value=0.0, step=10.0)
    due_day = col5.number_input("Día de vencimiento", min_value=1, max_value=28, value=5)
    if st.form_submit_button("Guardar deuda"):
        d = Debt(name=name, principal=float(principal), rate_apy=float(rate), min_payment=float(min_payment), due_day=int(due_day))
        sess.add(d); sess.commit(); st.success("Deuda guardada")

st.markdown("---")
rows = sess.query(Debt).all()
df = pd.DataFrame([{"id":r.id,"name":r.name,"principal":r.principal,"rate_apy":r.rate_apy,"min_payment":r.min_payment,"due_day":r.due_day} for r in rows])
st.dataframe(df, use_container_width=True, hide_index=True)
