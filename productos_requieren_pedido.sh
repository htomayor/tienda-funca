cd /var/www/funca/tienda
source venv/bin/activate
python3 -c "
from utils.db import get_db_connection
conn = get_db_connection()
cur = conn.cursor()
cur.execute(\"SELECT id, nombre, stock_actual, requiere_pedido FROM productos WHERE requiere_pedido = true\")
productos = cur.fetchall()
print('Productos que requieren pedido:')
for p in productos:
    print(f'  ID: {p[0]}, Nombre: {p[1]}, Stock: {p[2]}, Requiere Pedido: {p[3]}')
conn.close()
"
