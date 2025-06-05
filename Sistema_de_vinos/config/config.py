from dotenv import load_dotenv
import os

load_dotenv(".env")


user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("MYSQL_HOST")
database = os.getenv("MYSQL_DB_NAME") 
port = os.getenv("MYSQL_PORT", "3306")

print("\n--- VALORES DE LAS VARIABLES DE ENTORNO EN config/config.py ---")
print(f"MYSQL_USER: '{user}'")
print(f"MYSQL_PASSWORD: '{'*****' if password else 'None'}'") 
print(f"MYSQL_HOST: '{host}'")
print(f"MYSQL_PORT: '{port}'")
print(f"MYSQL_DB_NAME: '{database}'")
print("-----------------------------------------------------------------\n")

try:
    port = int(port) if port else 3306
except ValueError:
    print("Advertencia: MYSQL_PORT no es un número válido. Usando 3306 por defecto.")
    port = 3306

DATABASE_CONNECTION_URI = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

