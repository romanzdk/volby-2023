import datetime
import logging
import os

from matplotlib.lines import Line2D
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pytz
import streamlit as st

import helpers.data_loading
import settings.base
import settings.static


st.set_page_config(page_title = settings.static.TITLE, page_icon = settings.static.ICON, layout = 'wide')
st.set_option('deprecation.showPyplotGlobalUse', False)

logging.basicConfig()
logger = logging.getLogger()

st_autorefresh(interval = 2 * 60000)

connection = helpers.data_loading.get_connection()


##########

st.title('Volby prezidenta ČR 2023')
st.info('Stránka je automaticky aktualizována každé 2 minuty')
col1, col2 = st.columns(2)
with col1:
	st.metric(
		label = 'Poslední aktualizace stránky',
		value = datetime.datetime.now().astimezone(pytz.timezone('Europe/Prague')).strftime('%H:%M:%S'),
	)
with col2:
	st.metric(label = 'Data aktuální k', value = helpers.data_loading.get_last_update(connection))

###########

st.subheader('Doplňující údaje')
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)

additional_data = helpers.data_loading.get_additional_data(connection)

with col1:
	st.metric(
		label = 'Kolo',
		value = int(additional_data['KOLO'][0]),
	)
with col2:
	st.metric(
		label = 'Celkem okrsků',
		value = int(additional_data['OKRSKY_CELKEM'][0]),
	)
with col3:
	st.metric(
		label = 'Zpracováno okrsků',
		value = int(additional_data['OKRSKY_ZPRAC'][0]),
	)
with col4:
	st.metric(
		label = 'Zpracováno okrsků %',
		value = int(additional_data['OKRSKY_ZPRAC_PROC'][0]),
	)
with col5:
	st.metric(
		label = 'Zapsáno voličů',
		value = int(additional_data['ZAPSANI_VOLICI'][0]),
	)
with col6:
	st.metric(
		label = 'Vydáno obálek',
		value = int(additional_data['VYDANE_OBALKY'][0]),
	)
with col7:
	st.metric(
		label = 'Účast %',
		value = int(additional_data['UCAST_PROC'][0]),
	)
with col8:
	st.metric(
		label = 'Odevzdané obálky',
		value = int(additional_data['ODEVZDANE_OBALKY'][0]),
	)
with col9:
	st.metric(
		label = 'Platné hlasy',
		value = int(additional_data['PLATNE_HLASY'][0]),
	)
with col10:
	st.metric(
		label = 'Platné hlasy %',
		value = int(additional_data['PLATNE_HLASY_PROC'][0]),
	)


###########

st.subheader('Celkové výsledky')
chart = px.bar(
	helpers.data_loading.get_last_data(connection),
	x = 'percentage',
	y = 'index',
	color = 'index',
	labels = {'index': 'Jméno', 'percentage': '% hlasů'},
	orientation = 'h',
	text = 'percentage',
	color_discrete_map = settings.static.COLORS,
)
fig = go.Figure(chart)
fig.update_yaxes(showgrid = False)
st.plotly_chart(fig, use_container_width = True)

###########

st.subheader('Vývoj v čase')
line_chart = px.line(
	helpers.data_loading.get_overall_over_time_data(connection),
	x = 'last_update',
	y = 'value',
	color = 'name',
	labels = {'name': 'Jméno', 'value': '% hlasů', 'last_update': 'Čas'},
	markers = 'x',
	color_discrete_map = settings.static.COLORS,
)
fig = go.Figure(line_chart, layout = {'clickmode': None})
fig.update_yaxes(showgrid = False)
st.plotly_chart(fig, use_container_width = True)

##########

st.subheader('Výsledky v krajích')
st.text('(Absolutní počet hlasů)')
kraje = helpers.data_loading.get_kraje(connection)
st.dataframe(kraje, use_container_width = True)

########

st.subheader('Kandidát s nejvyšším počtem hlasů dle Kraje')
map_data = helpers.data_loading.get_map_data(kraje)
fig, ax = plt.subplots()
ax = map_data.plot(color = 'white', edgecolor = 'white')
# plt.margins(x=0.3)
map_data.plot(
	ax = ax,
	color = map_data['name'].map(settings.static.COLORS),
	legend = True,
)

lines = [
	Line2D([0], [0], color = c, linewidth = 1, linestyle = '', marker = 's')
	for c in settings.static.COLORS.values()
]
plt.legend(
	lines,
	settings.static.COLORS.keys(),
	fontsize = '5',
	frameon = False,
)
plt.box(False)
plt.axis('off')
# st.pyplot()
plt.savefig('x', dpi = 600)
st.image('x.png')
os.remove('x.png')

########

st.markdown('---')
st.markdown(
	'''<p style='text-align: center;'>Roman Žydyk, 2023, <a href="https://romanzdk.com">romanzdk.com</a></p>''',
	unsafe_allow_html = True,
)

connection.close()
