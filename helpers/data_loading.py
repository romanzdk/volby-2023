import geopandas as gpd
import pandas as pd
import psycopg2
import pyproj

import settings.base


def get_connection():
	return psycopg2.connect(
		database = settings.base.DATABASE,
		host = settings.base.DB_HOST,
		port = settings.base.DB_PORT,
		user = settings.base.DB_USER,
		password = settings.base.DB_PASSWORD,
	)


def get_main_data(connection):
	return pd.read_sql(
		f'''
			SELECT 
				last_update, 
				{settings.static.CANDIDATES_STRING}
			FROM overall_over_time
			ORDER BY last_update DESC;
		''',
		connection,
	)


def get_additional_data(connection):
	return pd.read_sql(
		'''
			SELECT * 
			FROM additional_info 
			ORDER BY last_update DESC 
			LIMIT 1;
		''',
		connection,
	).to_dict()


def get_overall_data(df):
	df = df.sort_values(by = 0, ascending = False)
	df[0] = df[0].apply(lambda x: f'{x:.2%}')
	df = df.reset_index()
	df.columns = ['Jméno', '% hlasů']
	return df


def get_overall_data_over_time(df):
	df.set_index('last_update')
	df = df.melt(id_vars = ['last_update'], var_name = 'name')
	df['value'] = df['value'].apply(lambda x: f'{x:.2%}')
	df.columns = ['Čas', 'Jméno', '% hlasů']
	return df


def get_regions_data(connection):
	return pd.read_sql(
		f'''
			SELECT 
				kraj as "Kraj",
				{settings.static.CANDIDATES_STRING},
				ROUND("zpracovano" * 100, 2) as "Zpracováno %"
			FROM kraje
			ORDER BY last_update DESC, kraj
			LIMIT 14;
		''',
		connection,
	)


def get_map_data(regions_data):
	df = (
		regions_data.drop('Zpracováno %', axis = 1)
		.melt(
			id_vars = ['Kraj'],
			var_name = 'Jméno',
			value_name = 'hlasů',
		)
		.sort_values('hlasů')
		.drop_duplicates(['Kraj'], keep = 'last')
		.drop('hlasů', axis = 1)
	)
	return (
		gpd.read_file('data/VUSC_P.shp')
		.to_crs(pyproj.CRS.from_epsg(4326))
		.drop(['KOD', 'REGS_KOD', 'NUTS3_KOD'], axis = 1)
		.set_index('NAZEV')
		.join(df.set_index('Kraj'))
	)
