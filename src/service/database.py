import mysql.connector
from config.env import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

class Database:
    def __init__(self):
        self.conn = None

    def open_conn(self):
        """Abre a conexão com o banco de dados."""
        if self.conn is None:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        else:
            print("Conexão já está aberta.")

    def insert(self, table_name, columns, data):
        """Insere dados na tabela especificada."""
        if self.conn is None:
            raise Exception("Conexão não está aberta. Use open_conn() para abrir a conexão.")
        
        placeholders = ", ".join(["%s"] * len(columns))
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        if isinstance(data[0], dict):
            data = [tuple(item[col.lower()] for col in columns) for item in data]
        
        cursor = self.conn.cursor()
        cursor.executemany(query, data)
        self.conn.commit()
        cursor.close()

    def search(self, table_name, columns="*", where=None, where_params=None, join=None):
        """Faz buscas no banco de dados e retorna os resultados."""
        if self.conn is None:
            raise Exception("Conexão não está aberta. Use open_conn() para abrir a conexão.")
        
        query = f"SELECT {', '.join(columns) if isinstance(columns, list) else columns} FROM {table_name}"
        
        if join:
            query += f" {join}"
        
        if where:
            if isinstance(where_params, (list, tuple)):
                placeholders = ', '.join(['%s'] * len(where_params))
                where = where.replace('%s', placeholders)
            
            query += f" WHERE {where}"

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query, where_params or ())
        result = cursor.fetchall()
        cursor.close()
        return result

    def close_conn(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        else:
            print("Conexão já está fechada.")