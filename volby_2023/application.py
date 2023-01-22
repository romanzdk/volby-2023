import datetime
import logging
import os

from matplotlib.lines import Line2D
from st_pages import Page, show_pages
from streamlit_autorefresh import st_autorefresh
import folium
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pytz
import streamlit as st
import matplotlib

import helpers.data_loading
import helpers.formatting
import helpers.mapping
import settings.base
import settings.static


st.set_page_config(page_title = settings.static.TITLE, page_icon = settings.static.ICON, layout = 'wide')

# sidebar width
st.markdown(
	'''
    <style>
        .css-1vencpc {{width: 10rem!important;min-width:100px!important;}}
		.css-163ttbj {{width: 10rem!important;min-width:100px!important;}}
    </style>
''',
	unsafe_allow_html = True,
)

show_pages(
	[
		Page('volby_2023/application.py', '2.kolo', ':two:'),
		Page('volby_2023/pages/first_round.py', '1. kolo', ':one:'),
	]
)


logging.basicConfig()
logger = logging.getLogger()

st_autorefresh(interval = 2 * 60000)

connection = helpers.data_loading.get_connection()
##########

main_data = helpers.data_loading.get_main_data(connection)

##########

st.title('Volby prezidenta ČR 2023 - 2. kolo')
st.info('Stránka je automaticky aktualizována každé 2 minuty')
col1, col2 = st.columns(2)
with col1:
	st.metric(
		label = 'Poslední aktualizace stránky',
		value = datetime.datetime.now().astimezone(pytz.timezone('Europe/Prague')).strftime('%Y-%m-%d %H:%M:%S'),
	)
with col2:
	try:
		value = str(main_data['last_update'].iat[0])
	except IndexError:
		value = 'N/A'
	st.metric(label = 'Data aktuální k', value = value)

###########

st.subheader('Doplňující údaje')
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)

additional_data = helpers.data_loading.get_additional_data(connection)

with col1:
	st.metric(label = 'Kolo', value = int(additional_data['KOLO'].get(0, 0)))
with col2:
	st.metric(
		label = 'Celkem okrsků',
		value = helpers.formatting.reduce_number(additional_data['OKRSKY_CELKEM'].get(0, 0)),
	)
with col3:
	st.metric(
		label = 'Zpracováno okrsků',
		value = helpers.formatting.reduce_number(additional_data['OKRSKY_ZPRAC'].get(0, 0)),
	)
with col4:
	st.metric(
		label = 'Zpracováno okrsků %',
		value = additional_data['OKRSKY_ZPRAC_PROC'].get(0, 0),
	)
with col5:
	st.metric(
		label = 'Zapsáno voličů',
		value = helpers.formatting.reduce_number(additional_data['ZAPSANI_VOLICI'].get(0, 0)),
	)
with col6:
	st.metric(
		label = 'Vydáno obálek',
		value = helpers.formatting.reduce_number(additional_data['VYDANE_OBALKY'].get(0, 0)),
	)
with col7:
	st.metric(
		label = 'Účast %',
		value = additional_data['UCAST_PROC'].get(0, 0),
	)
with col8:
	st.metric(
		label = 'Odevzdané obálky',
		value = helpers.formatting.reduce_number(additional_data['ODEVZDANE_OBALKY'].get(0, 0)),
	)
with col9:
	st.metric(
		label = 'Platné hlasy',
		value = helpers.formatting.reduce_number(additional_data['PLATNE_HLASY'].get(0, 0)),
	)
with col10:
	st.metric(
		label = 'Platné hlasy %',
		value = additional_data['PLATNE_HLASY_PROC'].get(0, 0),
	)


###########

st.subheader('Celkové výsledky')
try:
	data = helpers.data_loading.get_overall_data(main_data.drop('last_update', axis = 1).iloc[0].to_frame())
except IndexError:
	data = helpers.data_loading.get_overall_data_over_time(main_data)

chart = px.bar(
	data,
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

st.subheader('Výsledky v obcích')
st.text('(Absolutní počet hlasů)')
try:
	cities_data = helpers.data_loading.get_cities_data(connection)
	for col in cities_data.columns:
		cities_data[col] = cities_data[col].apply(lambda x: helpers.formatting.format_thousands(x))
	options = st.multiselect('Vybraný okrsek', cities_data.index.to_list())
	if options:
		cities_data = cities_data[cities_data.index.isin(options)]
	st.dataframe(cities_data, use_container_width = True)
except:
	st.info('Data se nepodařilo získat :( Zkuste to prosím později.')

########

st.subheader('Kandidát s nejvyšším počtem hlasů dle Kraje')
map_data = helpers.data_loading.get_map_data(raw_regions_data)

# map width
make_map_responsive = '''
 <style>
 [title~="st.iframe"] { width: 100%}
 </style>
'''
st.markdown(make_map_responsive, unsafe_allow_html = True)
cmap = matplotlib.colors.ListedColormap([v for k, v in settings.static.SECOND_ROUND_COLORS.items()])

with st.spinner('Mapa se načítá...'):
	helpers.mapping.folium_static(
		map_data.explore(
			column = 'Vítěz',
			popup = True,
			tiles = 'https://romanzdk.com/wp-content/uploads/2023/01/white.png',
			zoom_control = False,
			prefer_canvas = True,
			control_scale = False,
			legend = True,
			attr = ' ',
			cmap = cmap,
			# cmap=settings.static.SECOND_ROUND_COLORS.values(),
			style_kwds = dict(color = 'white', fillOpacity = 1),
			map_kwds = dict(dragging = False, scrollWheelZoom = False),
		),
		title = 'Legenda',
		colors = settings.static.SECOND_ROUND_COLORS.values(),
		labels = settings.static.SECOND_ROUND_COLORS.keys(),
	)


########

st.markdown('---')
st.markdown(
	'''<p style='text-align: center;'>Roman Žydyk, 2023, <a href="https://romanzdk.com">romanzdk.com</a></p>''',
	unsafe_allow_html = True,
)

connection.close()
