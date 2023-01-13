import decouple


DB_HOST = decouple.config('DB_HOST', default = 'localhost')
DB_PORT = decouple.config('DB_PORT', cast = int, default = '5432')
DB_USER = decouple.config('DB_USER')
DB_PASSWORD = decouple.config('DB_PASSWORD')
DATABASE = decouple.config('DATABASE', default = 'postgres')
