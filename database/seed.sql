USE ecommerce_electronicos;

-- ROLES
INSERT INTO roles (nombre, descripcion) VALUES
 ('admin','Administrador con acceso total'),
 ('trabajador','Personal: vendedor / logística / caja'),
 ('cliente','Cliente final del e-commerce');

-- PERMISOS
INSERT INTO permisos (codigo, descripcion) VALUES
 ('productos.ver','Ver productos'),
 ('productos.crear','Crear productos'),
 ('productos.editar','Editar productos'),
 ('productos.eliminar','Eliminar productos'),
 ('pedidos.ver','Ver pedidos'),
 ('pedidos.gestionar','Cambiar estado de pedidos'),
 ('usuarios.gestionar','Gestionar usuarios'),
 ('personal.gestionar','Gestionar personal'),
 ('reportes.ver','Ver reportes'),
 ('logistica.gestionar','Gestionar envíos');

-- ASIGNACIÓN: admin = todo
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT 1, id FROM permisos;

-- trabajador
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT 2, id FROM permisos
WHERE codigo IN ('productos.ver','pedidos.ver','pedidos.gestionar','logistica.gestionar');

-- cliente
INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT 3, id FROM permisos
WHERE codigo IN ('productos.ver');

-- USUARIOS DE PRUEBA
-- password_hash generado con werkzeug.security (pbkdf2:sha256)
-- admin123, trabajo123, cliente123
INSERT INTO usuarios (nombre, apellido, email, password_hash, rol_id, area) VALUES
 ('Admin','Principal','admin@tienda.com',
  'pbkdf2:sha256:600000$PgQQpjHCNvKJtVqs$0d9d20de1bf66a5cc5ec0cf8b4e2ea8e8b0b0c8a1b8e7f7c4a8d4b5b2c1a3d2e',
  1, NULL),
 ('Juan','Vendedor','trabajador@tienda.com',
  'pbkdf2:sha256:600000$rTzKqhDLvVnYsXtA$1e8d20de2cf66b5cc5ed1cf9b4f3eb8e8c0c0d8a2b9e8f8c5a9d5b6b2c2a4d3f',
  2, 'caja'),
 ('Ana','Cliente','cliente@tienda.com',
  'pbkdf2:sha256:600000$LpYZqfCKuUmXrWzB$2f9e30df3df77c6dd6fe2dfac5g4fc9f9d1d1e9b3cae9f9d6bae6c7c3d3b5e4g',
  3, NULL);

-- NOTA: estos hashes son placeholders. Al iniciar la app por primera vez,
-- ejecuta `python -m app.bootstrap` para regenerarlos correctamente, o
-- regístrate desde la web y promueve el rol manualmente.

-- CATEGORÍAS
INSERT INTO categorias (nombre, slug, descripcion) VALUES
 ('Smartphones','smartphones','Teléfonos inteligentes de última generación'),
 ('Laptops','laptops','Computadoras portátiles'),
 ('Audio','audio','Audífonos, parlantes y más'),
 ('Televisores','televisores','Smart TVs y monitores'),
 ('Accesorios','accesorios','Cables, cargadores, fundas');

-- MARCAS
INSERT INTO marcas (nombre) VALUES
 ('Samsung'),('Apple'),('Xiaomi'),('Sony'),('LG'),('HP'),('Lenovo'),('JBL');

-- PRODUCTOS
INSERT INTO productos (sku, nombre, descripcion, especificaciones, precio, precio_oferta, stock, imagen, destacado, categoria_id, marca_id) VALUES
 ('SMG-S24','Samsung Galaxy S24','Smartphone flagship con cámara 200MP','Pantalla 6.8" AMOLED, 12GB RAM, 256GB',3499.00,2999.00,15,'galaxy-s24.jpg',TRUE,1,1),
 ('APL-15','iPhone 15 Pro','Chip A17 Pro, titanio','6.1", 8GB RAM, 256GB',5499.00,NULL,8,'iphone15.jpg',TRUE,1,2),
 ('XMI-13','Xiaomi 13T','Cámara Leica',  '6.67", 12GB RAM, 256GB',1899.00,1699.00,25,'xiaomi-13t.jpg',TRUE,1,3),
 ('HP-PAV','HP Pavilion 15','Laptop para productividad','i5-1335U, 16GB, 512GB SSD',2799.00,NULL,12,'hp-pavilion.jpg',TRUE,2,6),
 ('LNV-LOQ','Lenovo LOQ Gaming','Laptop gamer','RTX 4050, i7, 16GB, 1TB SSD',4999.00,4499.00,6,'lenovo-loq.jpg',TRUE,2,7),
 ('SNY-WH1000','Sony WH-1000XM5','Audífonos NC premium','Bluetooth 5.2, 30h batería',1299.00,NULL,20,'sony-wh1000.jpg',FALSE,3,4),
 ('JBL-FLP6','JBL Flip 6','Parlante portátil','IP67, 12h batería',499.00,399.00,30,'jbl-flip6.jpg',FALSE,3,8),
 ('LG-OLED','LG OLED C3 55"','Smart TV OLED 4K','webOS, 120Hz, HDMI 2.1',5999.00,NULL,4,'lg-oled.jpg',TRUE,4,5),
 ('SMG-TV','Samsung Crystal UHD 50"','TV 4K','Tizen, HDR10+',2199.00,NULL,10,'samsung-tv.jpg',FALSE,4,1),
 ('ACC-CRG','Cargador USB-C 65W','Carga rápida GaN','Compatible PD 3.0',149.00,99.00,50,'cargador.jpg',FALSE,5,3);

-- DIRECCIÓN del cliente de prueba
INSERT INTO direcciones (usuario_id, etiqueta, destinatario, calle, ciudad, region, codigo_postal, predeterminada)
VALUES (3,'Casa','Ana Cliente','Av. Siempre Viva 742','Lima','Lima','15001',TRUE);
