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
import helpers.formatting
import settings.base
import settings.static


st.set_page_config(page_title = settings.static.TITLE, page_icon = settings.static.ICON, layout = 'wide')
st.set_option('deprecation.showPyplotGlobalUse', False)

logging.basicConfig()
logger = logging.getLogger()

st_autorefresh(interval = 2 * 60000)

connection = helpers.data_loading.get_connection()
##########

main_data = helpers.data_loading.get_main_data(connection)

##########

st.title('Volby prezidenta ČR 2023')
st.info('Stránka je automaticky aktualizována každé 2 minuty')
col1, col2 = st.columns(2)
with col1:
	st.metric(
		label = 'Poslední aktualizace stránky',
		value = datetime.datetime.now().astimezone(pytz.timezone('Europe/Prague')).strftime('%Y-%m-%d %H:%M:%S'),
	)
with col2:
	st.metric(label = 'Data aktuální k', value = str(main_data['last_update'].iat[0]))

###########

st.subheader('Doplňující údaje')
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)

additional_data = helpers.data_loading.get_additional_data(connection)

with col1:
	st.metric(label = 'Kolo', value = int(additional_data['KOLO'][0]))
with col2:
	st.metric(
		label = 'Celkem okrsků',
		value = helpers.formatting.reduce_number(additional_data['OKRSKY_CELKEM'][0]),
	)
with col3:
	st.metric(
		label = 'Zpracováno okrsků',
		value = helpers.formatting.reduce_number(additional_data['OKRSKY_ZPRAC'][0]),
	)
with col4:
	st.metric(
		label = 'Zpracováno okrsků %',
		value = additional_data['OKRSKY_ZPRAC_PROC'][0],
	)
with col5:
	st.metric(
		label = 'Zapsáno voličů',
		value = helpers.formatting.reduce_number(additional_data['ZAPSANI_VOLICI'][0]),
	)
with col6:
	st.metric(
		label = 'Vydáno obálek',
		value = helpers.formatting.reduce_number(additional_data['VYDANE_OBALKY'][0]),
	)
with col7:
	st.metric(
		label = 'Účast %',
		value = additional_data['UCAST_PROC'][0],
	)
with col8:
	st.metric(
		label = 'Odevzdané obálky',
		value = helpers.formatting.reduce_number(additional_data['ODEVZDANE_OBALKY'][0]),
	)
with col9:
	st.metric(
		label = 'Platné hlasy',
		value = helpers.formatting.reduce_number(additional_data['PLATNE_HLASY'][0]),
	)
with col10:
	st.metric(
		label = 'Platné hlasy %',
		value = additional_data['PLATNE_HLASY_PROC'][0],
	)


###########

st.subheader('Celkové výsledky')
chart = px.bar(
	helpers.data_loading.get_overall_data(main_data.drop('last_update', axis = 1).iloc[0].to_frame()),
	x = '% hlasů',
	y = 'Jméno',
	color = 'Jméno',
	orientation = 'h',
	text = '% hlasů',
	color_discrete_map = settings.static.COLORS,
)
fig = go.Figure(chart)
fig.update_yaxes(showgrid = False)
st.plotly_chart(fig, use_container_width = True)

###########

st.subheader('Vývoj v čase')
line_chart = px.line(
	helpers.data_loading.get_overall_data_over_time(main_data),
	x = 'Čas',
	y = '% hlasů',
	color = 'Jméno',
	markers = 'x',
	color_discrete_map = settings.static.COLORS,
)
fig = go.Figure(line_chart, layout = {'clickmode': None})
fig.update_yaxes(showgrid = False)
st.plotly_chart(fig, use_container_width = True)

##########

st.subheader('Výsledky v krajích')
st.text('(Absolutní počet hlasů)')
raw_regions_data = helpers.data_loading.get_regions_data(connection)
regions_data_table = raw_regions_data.copy()
for col in regions_data_table.columns:
	if col in {'Kraj', 'Zpracováno %'}:
		continue
	regions_data_table[col] = regions_data_table[col].apply(lambda x: helpers.formatting.format_thousands(x))
regions_data_table['Zpracováno %'] = [f'{x:.2f}' for x in regions_data_table['Zpracováno %']]
regions_data_styled = regions_data_table.style.applymap(
	helpers.formatting.highlight_percentage,
	subset = ['Zpracováno %'],
)
st.dataframe(regions_data_styled, use_container_width = True)

########

st.subheader('Kandidát s nejvyšším počtem hlasů dle Kraje')
map_data = helpers.data_loading.get_map_data(raw_regions_data)
# chart = px.choropleth_mapbox(
# 	map_data,
# 	geojson = map_data.geometry,
# 	locations = map_data.index,
# 	color = 'Jméno',
# )
# chart.update_geos(fitbounds="locations", visible=False)
# st.plotly_chart(chart, use_container_width = True)
fig, ax = plt.subplots()
ax = map_data.plot(color = 'white', edgecolor = 'white')
# plt.margins(x=0.3)
map_data.plot(
	ax = ax,
	color = map_data['Jméno'].map(settings.static.COLORS),
	legend = True,
	edgecolor = 'white',
	linewidth = 0.2,
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
