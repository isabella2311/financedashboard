import streamlit as st, pandas as pd, datetime as dt
from db import SessionLocal
from models import Goal

st.set_page_config(page_title="Metas", page_icon="🎯", layout="wide")
sess = SessionLocal()
st.title("🎯 Metas financieras")

with st.form("goal_form"):
    col1, col2, col3 = st.columns(3)
    name = col1.text_input("Meta", "Fondo de emergencia")
    target = col2.number_input("Objetivo (€)", min_value=0.0, step=50.0)
    deadline = col3.date_input("Fecha objetivo", dt.date.today())
    if st.form_submit_button("Crear meta"):
        g = Goal(name=name, target_amount=float(target), deadline=deadline, current_amount=0.0)
        sess.add(g); sess.commit()
        st.success("Meta creada")

st.markdown("---")
rows = sess.query(Goal).all()
df = pd.DataFrame([{"id":r.id,"name":r.name,"target":r.target_amount,"actual":r.current_amount,"deadline":r.deadline} for r in rows])
st.dataframe(df, use_container_width=True, hide_index=True)

if not df.empty:
    st.markdown("### Actualizar progreso")
    gid = st.selectbox("Meta", df["id"].tolist())
    new_val = st.number_input("Monto actual", min_value=0.0, step=10.0)
    if st.button("Actualizar"):
        g = sess.query(Goal).get(int(gid)); g.current_amount = float(new_val); sess.commit(); st.success("Actualizado")
