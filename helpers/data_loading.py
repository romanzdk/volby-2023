import os

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


def get_overall_over_time_data(connection):
	df = pd.read_sql('select * from overall_over_time;', connection).set_index('last_update')
	for col in df.columns:
		df[col] = ['{:.0%}'.format(i) for i in df[col]]
	return df.reset_index().melt(id_vars = ['last_update'], var_name = 'name')


def get_last_data(connection):
	df = pd.read_sql('select * from overall_over_time order by last_update DESC limit 1;', connection)
	df = df.drop('last_update', axis = 1)
	df = df.pivot_table(columns = 'percentage').reset_index().sort_values('percentage', ascending = False)
	for col in df.columns:
		try:
			df[col] = ['{:.0%}'.format(i) for i in df[col]]
		except ValueError:
			pass
	return df


def get_last_update(connection):
	cursor = connection.cursor()
	cursor.execute('select last_update from overall_over_time order by last_update DESC limit 1;')
	try:
		return str(cursor.fetchone()[0].time())
	except TypeError:
		return None
	finally:
		cursor.close()


def get_additional_data(connection):
	return pd.read_sql('select * from additional_info ORDER BY last_update DESC LIMIT 1;', connection).to_dict()


def get_kraje(connection):
	df = pd.read_sql('select * from kraje ORDER BY last_update DESC LIMIT 14;', connection).drop(
		'last_update',
		axis = 1,
	)
	for col in df.columns:
		if col != 'zpracovano':
			try:
				df[col] = df[col].astype(int)
			except ValueError:
				pass
	df['zpracovano'] = ['{:.0%}'.format(i) for i in df['zpracovano']]
	df = df.rename({'zpracovano': 'Zpracováno'}, axis = 1)

	return df


def get_map_data(kraje):
	df = kraje.drop('Zpracováno', axis = 1).melt(id_vars = ['kraj'], var_name = 'name')
	df = df.sort_values('value').drop_duplicates(['kraj'], keep = 'last').drop('value', axis = 1)
	map_df = gpd.read_file(os.path.join(os.getcwd(), 'data/VUSC_P.shp'))
	map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace = True)
	map_df.drop(['KOD', 'REGS_KOD', 'NUTS3_KOD'], axis = 1, inplace = True)
	return map_df.set_index('NAZEV').join(df.set_index('kraj'))
