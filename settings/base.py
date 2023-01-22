import decouple


DB_HOST = decouple.config('DB_HOST', default = 'localhost')
DB_PORT = decouple.config('DB_PORT', cast = int, default = '5432')
DB_USER = decouple.config('DB_USER', default = 'postgres')
DB_PASSWORD = decouple.config('DB_PASSWORD', default = 'postgres')
DATABASE = decouple.config('DATABASE', default = 'postgres')
