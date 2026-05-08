-- =====================================================================
-- Sistema E-commerce Productos Electrónicos
-- Base de datos MySQL 8.x
-- =====================================================================

DROP DATABASE IF EXISTS ecommerce_electronicos;
CREATE DATABASE ecommerce_electronicos
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE ecommerce_electronicos;

-- ---------------------------------------------------------------------
-- ROLES Y PERMISOS (RBAC)
-- ---------------------------------------------------------------------
CREATE TABLE roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL UNIQUE,
  descripcion VARCHAR(255),
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE permisos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(80) NOT NULL UNIQUE,         -- ej: 'productos.crear'
  descripcion VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE rol_permiso (
  rol_id INT NOT NULL,
  permiso_id INT NOT NULL,
  PRIMARY KEY (rol_id, permiso_id),
  FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- USUARIOS
-- ---------------------------------------------------------------------
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  apellido VARCHAR(100),
  email VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  telefono VARCHAR(30),
  rol_id INT NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  area VARCHAR(80),                            -- p/ trabajadores: 'caja', 'logistica'
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  ultimo_login DATETIME NULL,
  FOREIGN KEY (rol_id) REFERENCES roles(id),
  INDEX idx_usuarios_rol (rol_id),
  INDEX idx_usuarios_email (email)
) ENGINE=InnoDB;

CREATE TABLE direcciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  etiqueta VARCHAR(50),
  destinatario VARCHAR(120),
  calle VARCHAR(200) NOT NULL,
  ciudad VARCHAR(100) NOT NULL,
  region VARCHAR(100),
  codigo_postal VARCHAR(20),
  pais VARCHAR(80) DEFAULT 'Perú',
  predeterminada BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- CATÁLOGO
-- ---------------------------------------------------------------------
CREATE TABLE categorias (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL UNIQUE,
  slug VARCHAR(120) NOT NULL UNIQUE,
  descripcion TEXT,
  imagen VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE marcas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(50) UNIQUE,
  nombre VARCHAR(200) NOT NULL,
  descripcion TEXT,
  especificaciones TEXT,                       -- JSON o texto libre
  precio DECIMAL(10,2) NOT NULL,
  precio_oferta DECIMAL(10,2) NULL,
  stock INT NOT NULL DEFAULT 0,
  stock_minimo INT NOT NULL DEFAULT 5,
  imagen VARCHAR(255),
  destacado BOOLEAN DEFAULT FALSE,
  activo BOOLEAN DEFAULT TRUE,
  categoria_id INT,
  marca_id INT,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
  FOREIGN KEY (marca_id) REFERENCES marcas(id) ON DELETE SET NULL,
  INDEX idx_productos_cat (categoria_id),
  INDEX idx_productos_marca (marca_id),
  INDEX idx_productos_destacado (destacado)
) ENGINE=InnoDB;

CREATE TABLE producto_imagenes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  producto_id INT NOT NULL,
  url VARCHAR(255) NOT NULL,
  orden INT DEFAULT 0,
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE opiniones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  producto_id INT NOT NULL,
  usuario_id INT NOT NULL,
  puntuacion TINYINT NOT NULL,                 -- 1..5
  comentario TEXT,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- PEDIDOS
-- ---------------------------------------------------------------------
CREATE TABLE pedidos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  numero VARCHAR(20) UNIQUE,                   -- p/ mostrar al cliente
  usuario_id INT NOT NULL,
  trabajador_id INT NULL,                      -- caja/vendedor que registra
  direccion_id INT,
  subtotal DECIMAL(10,2) NOT NULL DEFAULT 0,
  descuento DECIMAL(10,2) NOT NULL DEFAULT 0,
  envio DECIMAL(10,2) NOT NULL DEFAULT 0,
  total DECIMAL(10,2) NOT NULL DEFAULT 0,
  estado ENUM('pendiente','pagado','en_preparacion','enviado','entregado','cancelado')
         NOT NULL DEFAULT 'pendiente',
  metodo_pago VARCHAR(40),
  notas TEXT,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
  FOREIGN KEY (trabajador_id) REFERENCES usuarios(id),
  FOREIGN KEY (direccion_id) REFERENCES direcciones(id) ON DELETE SET NULL,
  INDEX idx_pedidos_estado (estado),
  INDEX idx_pedidos_fecha (creado_en)
) ENGINE=InnoDB;

CREATE TABLE pedido_detalles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id INT NOT NULL,
  producto_id INT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
  FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- PAGOS Y ENVÍOS
-- ---------------------------------------------------------------------
CREATE TABLE pagos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id INT NOT NULL,
  metodo VARCHAR(40) NOT NULL,                 -- tarjeta, yape, efectivo...
  monto DECIMAL(10,2) NOT NULL,
  estado ENUM('aprobado','rechazado','pendiente') DEFAULT 'pendiente',
  referencia VARCHAR(80),
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE envios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id INT NOT NULL,
  trabajador_id INT NULL,
  estado ENUM('pendiente','en_preparacion','en_camino','entregado') DEFAULT 'pendiente',
  tracking VARCHAR(80),
  fecha_envio DATETIME NULL,
  fecha_entrega DATETIME NULL,
  notas TEXT,
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
  FOREIGN KEY (trabajador_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- INVENTARIO (movimientos)
-- ---------------------------------------------------------------------
CREATE TABLE inventario_movimientos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  producto_id INT NOT NULL,
  tipo ENUM('entrada','salida','ajuste') NOT NULL,
  cantidad INT NOT NULL,
  motivo VARCHAR(200),
  usuario_id INT,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- NOTIFICACIONES
-- ---------------------------------------------------------------------
CREATE TABLE notificaciones (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  titulo VARCHAR(150) NOT NULL,
  mensaje TEXT,
  tipo VARCHAR(40) DEFAULT 'info',
  leida BOOLEAN DEFAULT FALSE,
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
  INDEX idx_notif_usuario (usuario_id, leida)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- LOG DE ACTIVIDAD (auditoría)
-- ---------------------------------------------------------------------
CREATE TABLE actividad_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT,
  accion VARCHAR(120) NOT NULL,
  detalle TEXT,
  ip VARCHAR(45),
  creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- TRIGGER: descontar stock al insertar detalle de pedido pagado
-- (también lo controla la app, esto es seguridad de DB)
-- ---------------------------------------------------------------------
DELIMITER $$
CREATE TRIGGER trg_descuento_stock
AFTER INSERT ON pedido_detalles
FOR EACH ROW
BEGIN
  UPDATE productos
     SET stock = stock - NEW.cantidad
   WHERE id = NEW.producto_id;
END$$
DELIMITER ;
