import streamlit as st, pandas as pd, datetime as dt
from db import SessionLocal
from models import Budget, Transaction

st.set_page_config(page_title="Presupuestos", page_icon="📊", layout="wide")
sess = SessionLocal()
st.title("📊 Presupuestos por categoría")

with st.form("budget_form"):
    col1, col2, col3, col4 = st.columns(4)
    category = col1.text_input("Categoría", "General")
    month = col2.number_input("Mes", 1, 12, dt.date.today().month)
    year = col3.number_input("Año", 2000, 2100, dt.date.today().year)
    amount = col4.number_input("Monto presupuestado", min_value=0.0, step=10.0)
    if st.form_submit_button("Guardar presupuesto"):
        b = Budget(category=category, month=int(month), year=int(year), amount=float(amount))
        sess.add(b); sess.commit()
        st.success("Presupuesto guardado")

st.markdown("---")
rows = sess.query(Budget).all()
dfb = pd.DataFrame([{"id":r.id,"category":r.category,"month":r.month,"year":r.year,"amount":r.amount} for r in rows])
st.dataframe(dfb, use_container_width=True, hide_index=True)

st.markdown("### Ejecución del presupuesto (gasto real vs plan)")
if not dfb.empty:
    m = dfb.iloc[-1]["month"]; y = dfb.iloc[-1]["year"]; cat = dfb.iloc[-1]["category"]; plan = dfb.iloc[-1]["amount"]
    q = sess.query(Transaction).filter(Transaction.type=="expense").filter(Transaction.category==cat)
    df = pd.DataFrame([{"date":t.date,"amount":t.amount} for t in q.all()])
    if not df.empty:
        dfm = df[pd.to_datetime(df["date"]).dt.month==m]
        dfm = dfm[pd.to_datetime(dfm["date"]).dt.year==y]
        real = dfm["amount"].sum()
        st.metric(f"{cat} {m}/{y}", f"Gasto: {real:,.2f} / Plan: {plan:,.2f}")
