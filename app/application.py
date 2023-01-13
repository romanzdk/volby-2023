import datetime
import logging
import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import settings.base
import settings.static

st.set_page_config(
    page_title=settings.static.TITLE, page_icon=settings.static.ICON, layout="wide"
)

logging.basicConfig()
logger = logging.getLogger()

st_autorefresh(interval=2 * 60000)


connection = psycopg2.connect(
    database=settings.base.DATABASE,
    host=settings.base.DB_HOST,
    port=settings.base.DB_PORT,
    user=settings.base.DB_USER,
    password=settings.base.DB_PASSWORD,
)


def get_overall_over_time_data():
    df = pd.read_sql("select * from overall_over_time;", connection).set_index(
        "last_update"
    )
    for col in df.columns:
        df[col] = ["{:.0%}".format(i) for i in df[col]]
    return df


def get_last_data():
    df = pd.read_sql(
        "select * from overall_over_time order by last_update DESC limit 1;", connection
    )
    df = df.drop("last_update", axis=1)
    df = (
        df.pivot_table(columns="percentage")
        .reset_index()
        .sort_values("percentage", ascending=False)
    )
    for col in df.columns:
        try:
            df[col] = ["{:.0%}".format(i) for i in df[col]]
        except ValueError:
            pass
    return df


def get_last_update():
    cursor = connection.cursor()
    cursor.execute(
        "select last_update from overall_over_time order by last_update DESC limit 1;"
    )
    return str(cursor.fetchone()[0].time())


st.title("Volby prezidenta ČR 2023")
st.info("Stránka je automaticky aktualizována každé 2 minuty")
col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Poslední aktualizace stránky",
        value=datetime.datetime.now()
        .astimezone(pytz.timezone("Europe/Prague"))
        .strftime("%H:%M:%S"),
    )
with col2:
    st.metric(label="Data aktuální k", value=get_last_update())

###########

st.subheader("Celkové výsledky")
chart = px.bar(
    get_last_data(),
    x="percentage",
    y="index",
    color="index",
    labels={"index": "Jméno", "percentage": "% hlasů"},
    orientation="h",
    text="percentage",
)
fig = go.Figure(chart)
fig.update_yaxes(showgrid=False)
st.plotly_chart(fig, use_container_width=True)

###########
st.subheader("Vývoj v čase")
overall_over_time_data = get_overall_over_time_data()
df = overall_over_time_data.reset_index().melt(id_vars=["last_update"], var_name="name")

line_chart = px.line(
    df,
    x="last_update",
    y="value",
    color="name",
    labels={"name": "Jméno", "value": "% hlasů", "last_update": "Čas"},
    markers="x",
)
fig = go.Figure(line_chart)
fig.update_yaxes(showgrid=False)
st.plotly_chart(fig, use_container_width=True)

st.write(overall_over_time_data)
