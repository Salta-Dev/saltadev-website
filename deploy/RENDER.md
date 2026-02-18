# Despliegue en Render.com

Guía para desplegar SaltaDev Website en Render.com (Free Tier).

## Requisitos Previos

1. Cuenta en [Render.com](https://render.com) (gratis, no requiere tarjeta)
2. Repositorio conectado a GitHub
3. Credenciales de servicios externos:
   - **Cloudinary**: Para imágenes (gratis)
   - **Resend**: Para emails (gratis hasta 3000/mes)
   - **reCAPTCHA v2**: Para protección de formularios (gratis)

## Paso 1: Crear Cuenta en Render

1. Ir a [render.com](https://render.com)
2. Click en "Sign Up" y conectar con GitHub
3. No se requiere tarjeta de crédito

## Paso 2: Desplegar con Blueprint

1. En el Dashboard, click en **New** → **Blueprint**
2. Conectar el repositorio `saltadev-website`
3. Seleccionar el archivo `deploy/render.yaml`
4. Render creará automáticamente:
   - Web Service (Django con Gunicorn)
   - PostgreSQL database (free)
   - Redis instance (free)

## Paso 3: Configurar Variables de Entorno

En el Web Service, ir a **Environment** y agregar:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `CLOUDINARY_CLOUD_NAME` | Nombre de tu cloud en Cloudinary | `my-cloud` |
| `CLOUDINARY_API_KEY` | API Key de Cloudinary | `123456789` |
| `CLOUDINARY_API_SECRET` | API Secret de Cloudinary | `abc123xyz` |
| `RESEND_API_KEY` | API Key de Resend | `re_xxx...` |
| `DEFAULT_FROM_EMAIL` | Email de origen | `noreply@salta.dev` |
| `SITE_URL` | URL del sitio | `https://saltadev-website.onrender.com` |
| `RECAPTCHA_V2_SITE_KEY` | Site Key de reCAPTCHA v2 | `6Le...` |
| `RECAPTCHA_V2_SECRET` | Secret Key de reCAPTCHA v2 | `6Le...` |

## Paso 4: Esperar el Deploy

1. El build tarda ~5-10 minutos la primera vez
2. Render compila Tailwind CSS, collectstatic, y aplica migraciones
3. Una vez completado, la URL estará disponible en el Dashboard

## Paso 5: Verificar

- [ ] La web carga correctamente
- [ ] El healthcheck responde: `curl https://tu-app.onrender.com/health/`
- [ ] El registro de usuario funciona
- [ ] Los emails de verificación llegan (vía Resend)
- [ ] El login funciona
- [ ] Las imágenes cargan (vía Cloudinary)

## Dominio Personalizado (Opcional)

Para usar `salta.dev`:

1. En Render: **Settings** → **Custom Domains** → **Add Domain**
2. En tu DNS, crear un registro CNAME:
   ```
   salta.dev  →  saltadev-website.onrender.com
   ```
3. Render genera certificado SSL automáticamente

## Limitaciones del Free Tier

| Limitación | Descripción | Mitigación |
|------------|-------------|------------|
| **Cold starts** | App se duerme después de 15 min sin tráfico. Primera visita tarda ~30s | Usar UptimeRobot para hacer ping cada 10 min |
| **PostgreSQL expira** | La DB gratuita se borra después de 90 días | Hacer backup con `pg_dump` y recrear |
| **SMTP bloqueado** | Puertos SMTP no funcionan | Usar Resend (ya configurado) |

## Comandos Útiles

```bash
# Ver logs en tiempo real (desde tu máquina)
render logs --service saltadev-website --tail

# Conectar a la DB
render psql --service saltadev-db

# Backup de la DB
pg_dump $DATABASE_URL > backup.sql
```

## Troubleshooting

### El build falla

Revisar los logs en Render Dashboard → Web Service → Logs

### Los emails no llegan

1. Verificar que `RESEND_API_KEY` esté configurado
2. Verificar que el dominio esté verificado en Resend
3. Revisar logs de Render por errores de Anymail

### Las imágenes no cargan

1. Verificar las credenciales de Cloudinary
2. Revisar que el `CLOUDINARY_CLOUD_NAME` sea correcto

### Error 500 al cargar

1. Revisar logs de Render
2. Verificar que `ALLOWED_HOSTS` incluya el dominio de Render
3. Verificar que `SECRET_KEY` esté configurado

## Monitoreo

### Healthcheck Endpoint

Render puede usar `/health/` para verificar que la aplicación está funcionando:

```bash
curl https://saltadev-website.onrender.com/health/
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "services": {
    "django": "ok",
    "postgres": "ok",
    "redis": "ok"
  }
}
```

### Configurar Health Check en Render

1. Ir a **Web Service** → **Settings** → **Health & Alerts**
2. Configurar **Health Check Path**: `/health/`
3. Render verificará automáticamente el endpoint cada 30 segundos
