import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Crear conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'tienda_db'),
            user=os.getenv('DB_USER', 'tienda_user'),
            password=os.getenv('DB_PASSWORD', 'Tienda2024!'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return None

def init_db():
    """Crear todas las tablas si no existen"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Tabla: categorias
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: proveedores
        cur.execute("""
            CREATE TABLE IF NOT EXISTS proveedores (
                id SERIAL PRIMARY KEY,
                nit VARCHAR(20) UNIQUE NOT NULL,
                nombre VARCHAR(200) NOT NULL,
                telefono VARCHAR(20),
                email VARCHAR(100),
                direccion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: productos (con campos para pedidos)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                codigo_barras VARCHAR(50) UNIQUE,
                nombre VARCHAR(200) NOT NULL,
                descripcion TEXT,
                categoria_id INTEGER REFERENCES categorias(id),
                proveedor_preferido_id INTEGER REFERENCES proveedores(id),
                precio_compra DECIMAL(15,2) NOT NULL DEFAULT 0,
                precio_venta DECIMAL(15,2) NOT NULL DEFAULT 0,
                stock_actual INTEGER NOT NULL DEFAULT 0,
                stock_minimo INTEGER DEFAULT 5,
                stock_maximo INTEGER DEFAULT 100,
                requiere_pedido BOOLEAN DEFAULT false,
                unidad_medida VARCHAR(20) DEFAULT 'unidad',
                ubicacion VARCHAR(50),
                activo BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: clientes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('estudiante', 'funcionario', 'externo')),
                documento VARCHAR(20) UNIQUE NOT NULL,
                nombres VARCHAR(100) NOT NULL,
                apellidos VARCHAR(100) NOT NULL,
                telefono VARCHAR(20),
                email VARCHAR(100),
                direccion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: movimientos_inventario
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id SERIAL PRIMARY KEY,
                producto_id INTEGER REFERENCES productos(id),
                tipo_movimiento VARCHAR(20) NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario DECIMAL(15,2),
                valor_total DECIMAL(15,2),
                stock_anterior INTEGER,
                stock_nuevo INTEGER,
                observaciones TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: ventas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER REFERENCES clientes(id),
                numero_factura VARCHAR(50) UNIQUE,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subtotal DECIMAL(15,2),
                iva DECIMAL(15,2),
                total DECIMAL(15,2),
                forma_pago VARCHAR(50),
                estado VARCHAR(20) DEFAULT 'completada',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: ventas_detalle
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas_detalle (
                id SERIAL PRIMARY KEY,
                venta_id INTEGER REFERENCES ventas(id),
                producto_id INTEGER REFERENCES productos(id),
                cantidad INTEGER NOT NULL,
                precio_unitario DECIMAL(15,2),
                subtotal DECIMAL(15,2)
            )
        """)
        
        # Tabla: pedidos_proveedor
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos_proveedor (
                id SERIAL PRIMARY KEY,
                venta_id INTEGER REFERENCES ventas(id),
                proveedor_id INTEGER REFERENCES proveedores(id),
                numero_pedido VARCHAR(50) UNIQUE,
                fecha_pedido DATE DEFAULT CURRENT_DATE,
                estado VARCHAR(20) DEFAULT 'pendiente',
                observaciones TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla: pedidos_proveedor_detalle
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos_proveedor_detalle (
                id SERIAL PRIMARY KEY,
                pedido_id INTEGER REFERENCES pedidos_proveedor(id),
                producto_id INTEGER REFERENCES productos(id),
                cantidad_solicitada INTEGER NOT NULL,
                cantidad_recibida INTEGER DEFAULT 0,
                precio_unitario_sugerido DECIMAL(15,2),
                subtotal DECIMAL(15,2)
            )
        """)
        
        # Insertar datos iniciales
        cur.execute("SELECT COUNT(*) FROM categorias")
        if cur.fetchone()[0] == 0:
            categorias_iniciales = [
                ('Bebidas', 'Gaseosas, jugos, aguas, energizantes'),
                ('Alimentos', 'Snacks, dulces, galletas, comestibles'),
                ('Papelería', 'Cuadernos, lapiceros, carpetas, marcadores'),
                ('Tecnología', 'USB, audífonos, cargadores, mouse'),
                ('Uniformes', 'Camisetas, sudaderas, gorras, chaquetas'),
                ('Carnets', 'Carnets estudiantiles, institucionales')
            ]
            cur.executemany("INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)", categorias_iniciales)
        
        # Proveedores iniciales
        cur.execute("SELECT COUNT(*) FROM proveedores")
        if cur.fetchone()[0] == 0:
            proveedores_iniciales = [
                ('900123456-1', 'Distribuidora de Uniformes SAS', '3101234567', 'ventas@uniformes.com'),
                ('900123456-2', 'Carnetización Express', '3107654321', 'pedidos@carnets.com'),
                ('900123456-3', 'Papelería y Más', '3119876543', 'ventas@papeleria.com')
            ]
            cur.executemany("INSERT INTO proveedores (nit, nombre, telefono, email) VALUES (%s, %s, %s, %s)", proveedores_iniciales)
        
        # Clientes iniciales
        cur.execute("SELECT COUNT(*) FROM clientes")
        if cur.fetchone()[0] == 0:
            clientes_iniciales = [
                ('estudiante', '1001', 'Juan', 'Pérez', '3001234567', 'juan@funca.edu.co'),
                ('estudiante', '1002', 'Ana', 'García', '3107654321', 'ana@funca.edu.co'),
                ('funcionario', '2001', 'María', 'Gómez', '3209876543', 'maria@funca.edu.co'),
                ('externo', '3001', 'Carlos', 'López', '3156789012', 'carlos@gmail.com'),
            ]
            cur.executemany("""
                INSERT INTO clientes (tipo, documento, nombres, apellidos, telefono, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, clientes_iniciales)
        
        # Productos iniciales
        cur.execute("SELECT COUNT(*) FROM productos")
        if cur.fetchone()[0] == 0:
            cur.execute("SELECT id FROM categorias WHERE nombre = 'Uniformes' LIMIT 1")
            cat_uniformes = cur.fetchone()[0]
            cur.execute("SELECT id FROM categorias WHERE nombre = 'Carnets' LIMIT 1")
            cat_carnets = cur.fetchone()[0]
            cur.execute("SELECT id FROM proveedores WHERE nombre ILIKE '%uniformes%' LIMIT 1")
            prov_uniformes = cur.fetchone()[0]
            cur.execute("SELECT id FROM proveedores WHERE nombre ILIKE '%carnets%' LIMIT 1")
            prov_carnets = cur.fetchone()[0]
            
            productos_iniciales = [
                ('UNIF-001', 'Uniforme Camiseta', cat_uniformes, prov_uniformes, 25000, 45000, 0, 5, True),
                ('UNIF-002', 'Uniforme Sudadera', cat_uniformes, prov_uniformes, 45000, 75000, 0, 5, True),
                ('CARN-001', 'Carnet Estudiantil', cat_carnets, prov_carnets, 3000, 8000, 0, 10, True),
                ('PROD-001', 'Gaseosa 350ml', 1, None, 2000, 3500, 50, 5, False),
                ('PROD-002', 'Cuaderno 100h', 3, None, 4000, 8000, 30, 5, False),
            ]
            for p in productos_iniciales:
                cur.execute("""
                    INSERT INTO productos (codigo_barras, nombre, categoria_id, proveedor_preferido_id,
                                           precio_compra, precio_venta, stock_actual, stock_minimo, requiere_pedido)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, p)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error inicializando BD: {e}")
        return False
