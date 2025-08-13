import os, datetime as dt, pandas as pd, streamlit as st, plotly.express as px
from db import init_db, SessionLocal
from models import Transaction, Budget, Goal, Debt, Investment, Account
import streamlit_authenticator as stauth
import bcrypt

st.set_page_config(page_title="Finance Dashboard", page_icon="💼", layout="wide")
init_db()

# --- Auth (prod via env) ---
email = os.environ.get("FINANCE_EMAIL", "admin@example.com")
name = os.environ.get("FINANCE_NAME", "Admin")
password_hash = os.environ.get("FINANCE_PASSWORD_HASH", None)

if password_hash:
    hashed = password_hash  # must be a bcrypt hash string
else:
    # fallback demo password "admin123"
    hashed = stauth.Hasher(["admin123"]).generate()[0]

credentials = {"usernames": {email: {"email": email, "name": name, "password": hashed}}}
authenticator = stauth.Authenticate(credentials, "auth_cookie", "auth_key", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Iniciar sesión", "main")
if not authentication_status:
    st.stop()
authenticator.logout("Cerrar sesión", "sidebar")

st.sidebar.title("💼 Finance Dashboard")
st.sidebar.caption(f"Usuario: {name}")

# helpers
def get_session():
    return SessionLocal()

def df_transactions(sess, start=None, end=None):
    q = sess.query(Transaction)
    if start:
        q = q.filter(Transaction.date >= start)
    if end:
        q = q.filter(Transaction.date <= end)
    rows = q.all()
    if not rows:
        return pd.DataFrame(columns=["id", "date", "type", "category", "account", "amount", "description", "tags"])
    data = [{
        "id": r.id,
        "date": r.date,
        "type": r.type,
        "category": r.category,
        "account": r.account,
        "amount": r.amount,
        "description": r.description,
        "tags": r.tags,
    } for r in rows]
    return pd.DataFrame(data)

def upsert_transaction(sess, row):
    if row.get("id"):
        t = sess.query(Transaction).get(int(row["id"]))
        if not t:
            return
    else:
        t = Transaction()
    t.date = pd.to_datetime(row["date"]).date()
    t.type = row["type"]
    t.category = row["category"]
    t.account = row.get("account", "Principal")
    t.amount = float(row["amount"])
    t.description = row.get("description", "")
    t.tags = row.get("tags", "")
    sess.add(t)
    sess.commit()

def delete_transaction(sess, id_):
    t = sess.query(Transaction).get(int(id_))
    if t:
        sess.delete(t)
        sess.commit()

# Sidebar filters
with st.sidebar:
    st.subheader("Filtros")
    today = dt.date.today()
    start = st.date_input("Desde", dt.date(today.year, 1, 1))
    end = st.date_input("Hasta", today)
    category_filter = st.text_input("Categoría (contiene)", "")
    account_filter = st.text_input("Cuenta (contiene)", "")
    tag_filter = st.text_input("Etiqueta (contiene)", "")

tab1, tab2 = st.tabs(["📈 Resumen", "🧾 Transacciones"])

with tab1:
    sess = get_session()
    df = df_transactions(sess, start, end)

    if category_filter:
        df = df[df["category"].str.contains(category_filter, case=False, na=False)]
    if account_filter:
        df = df[df["account"].str.contains(account_filter, case=False, na=False)]
    if tag_filter:
        df = df[df["tags"].str.contains(tag_filter, case=False, na=False)]

    c1, c2, c3, c4 = st.columns(4)
    income = df.loc[df["type"] == "income", "amount"].sum()
    expense = df.loc[df["type"] == "expense", "amount"].sum()
    balance = income - expense
    avg_spend = df.loc[df["type"] == "expense", "amount"].mean() if not df[df["type"] == "expense"].empty else 0
    c1.metric("Ingresos", f"{income:,.2f}")
    c2.metric("Gastos", f"{expense:,.2f}")
    c3.metric("Balance", f"{balance:,.2f}")
    c4.metric("Gasto promedio", f"{avg_spend:,.2f}")

    if not df.empty:
        dfm = df.copy()
        dfm["month"] = pd.to_datetime(dfm["date"]).dt.to_period("M").astype(str)
        flow = dfm.pivot_table(index="month", columns="type", values="amount", aggfunc="sum").fillna(0)
        flow = flow.reset_index()
        fig = px.bar(flow, x="month", y=["income", "expense"], barmode="group", title="Flujo mensual")
        st.plotly_chart(fig, use_container_width=True)

        by_cat = df[df["type"] == "expense"].groupby("category")["amount"].sum().sort_values(ascending=False).reset_index()
        if not by_cat.empty:
            fig2 = px.pie(by_cat, names="category", values="amount", title="Gasto por categoría")
            st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Transacciones")
    sess = get_session()
    df = df_transactions(sess)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("### Añadir / Editar")
    with st.form("trx_form", clear_on_submit=True):
        id_edit = st.text_input("ID (solo para editar)", "")
        date = st.date_input("Fecha", dt.date.today())
        type_ = st.selectbox("Tipo", ["income", "expense"])
        category = st.text_input("Categoría", "General")
        account = st.text_input("Cuenta", "Principal")
        amount = st.number_input("Monto", step=0.01, format="%.2f")
        description = st.text_input("Descripción", "")
        tags = st.text_input("Etiquetas (coma separadas)", "")
        submitted = st.form_submit_button("Guardar")
        if submitted:
            upsert_transaction(sess, {
                "id": id_edit.strip() or None,
                "date": date,
                "type": type_,
                "category": category,
                "account": account,
                "amount": amount,
                "description": description,
                "tags": tags,
            })
            st.success("Transacción guardada. Actualiza la vista desde el menú Rerun.")

    st.markdown("---")
    del_id = st.text_input("ID a borrar", "")
    if st.button("Borrar"):
        if del_id.strip():
            delete_transaction(sess, del_id.strip())
            st.warning("Transacción eliminada.")

    st.markdown("**Exportar CSV**")
    df = df_transactions(sess)
    st.download_button("Descargar transacciones", df.to_csv(index=False).encode("utf-8"), "transacciones.csv", "text/csv")

    st.markdown("**Importar CSV** (campos: date,type,category,account,amount,description,tags)")
    up = st.file_uploader("Sube CSV", type=["csv"])
    if up is not None:
        try:
            imp = pd.read_csv(up)
            cnt = 0
            for _, r in imp.iterrows():
                upsert_transaction(sess, r.to_dict())
                cnt += 1
            st.success(f"Importadas {cnt} transacciones.")
        except Exception as e:
            st.error(f"Error al importar: {e}")
