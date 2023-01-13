import pandas as pd
import streamlit as st
import psycopg2
import logging
import settings.base
import plotly.express as px
import time
import datetime
from streamlit_autorefresh import st_autorefresh

logging.basicConfig()
logger = logging.getLogger()

st_autorefresh(interval=60000)

connection = psycopg2.connect(
	database = settings.base.DATABASE,
	host=settings.base.DB_HOST,
	port=settings.base.DB_PORT,
	user=settings.base.DB_USER,
	password=settings.base.DB_PASSWORD
)

def get_overall_over_time_data():
	return pd.read_sql('select * from overall_over_time;', connection).set_index('last_update')

def get_last_data():
	df = pd.read_sql('select "Babiš", "Nerudová", "Pavel" from overall_over_time order by last_update DESC limit 1;', connection)
	return df.pivot_table(columns='percentage').reset_index().sort_values('percentage', ascending=False)

def get_last_update():
	cursor = connection.cursor()
	cursor.execute('select last_update from overall_over_time order by last_update DESC limit 1;')
	return str(cursor.fetchone()[0].time())

st.title('Volby prezidenta ČR 2023')
st.info("Stránka je automaticky aktualizována každou minutu")
col1, col2 = st.columns(2)
with col1:
	st.metric(label="Poslední aktualizace stránky", value=str(datetime.datetime.now().time()))
with col2:
	st.metric(label="Data aktuální k", value=get_last_update())

st.subheader('Celkové výsledky')
overall_over_time_data = get_overall_over_time_data()
chart = px.bar(get_last_data(), x='index', y='percentage', color='index', labels={'index':'Jméno', 'percentage':'% hlasů'})
st.plotly_chart(chart)

st.subheader('Vývoj v čase')
st.line_chart(overall_over_time_data)
st.write(overall_over_time_data)