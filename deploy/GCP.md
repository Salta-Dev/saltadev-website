# Despliegue en GCP + Neon + Upstash

Guía para migrar SaltaDev Website de Render.com a GCP (VM e2-micro free tier) con PostgreSQL en Neon y Redis en Upstash.

## Arquitectura

| Servicio | Proveedor | Tier | Costo |
|----------|-----------|------|-------|
| VM (Django/nginx) | GCP e2-micro (us-central1) | Free | $0 |
| PostgreSQL | Neon (São Paulo) | Free | $0 |
| Redis (cache + sesiones) | Upstash (São Paulo) | Free | $0 |
| Imágenes | Cloudinary | Free | $0 |
| Email | Resend | Free (3000/mes) | $0 |

**Budget de memoria (1GB RAM + 1GB swap):**
- OS + systemd: ~120MB
- Docker daemon: ~80MB
- nginx container: ~15MB
- gunicorn (2 workers): ~200MB
- Headroom: ~585MB + 1GB swap

---

## Requisitos Previos

- Cuenta en [Google Cloud](https://cloud.google.com) (requiere tarjeta, pero e2-micro es free forever)
- Cuenta en [Neon](https://neon.tech) (gratis, no requiere tarjeta)
- Cuenta en [Upstash](https://upstash.com) (gratis, no requiere tarjeta)
- `gcloud` CLI instalado localmente
- `psql` y `pg_dump` instalados localmente

---

## Fase 1: Preparación (Día 1)

### 1.1 Crear cuenta en Neon (PostgreSQL)

1. Registrarse en [neon.tech](https://neon.tech)
2. Crear proyecto `saltadev`, región **South America (São Paulo)**
3. Guardar el connection string:
   ```
   postgresql://user:pass@ep-xxx.sa-east-1.aws.neon.tech/saltadev?sslmode=require
   ```
4. Free tier: 0.5GB storage, 1 proyecto, auto-suspend tras 5 min de inactividad

### 1.2 Crear cuenta en Upstash (Redis)

1. Registrarse en [upstash.com](https://upstash.com)
2. Crear database `saltadev`, región **South America (São Paulo)**
3. Guardar el connection string (usar `rediss://` con doble s para TLS):
   ```
   rediss://default:pass@xxx.upstash.io:6379
   ```
4. Free tier: 10K comandos/día, 256MB

### 1.3 Backup de la base de datos actual (Render)

```bash
# Obtener DATABASE_URL del dashboard de Render → Web Service → Environment
pg_dump "$RENDER_DATABASE_URL" --format=custom --no-owner --no-acl -f saltadev_backup.dump

# Verificar backup
pg_restore --list saltadev_backup.dump | head -50
```

### 1.4 Restaurar en Neon

```bash
psql "$NEON_DIRECT_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT CREATE ON SCHEMA public TO neondb_owner;"                                                   

# Verificar integridad (asegurarse que $NEON_DATABASE_URL apunta a /saltadev, no /neondb)
psql "$NEON_DATABASE_URL" -c "SELECT count(*) FROM users_user;"
psql "$NEON_DATABASE_URL" -c "SELECT count(*) FROM events_event;"
psql "$NEON_DATABASE_URL" -c "SELECT count(*) FROM django_migrations;"
```

### 1.5 Bajar TTL del DNS

Cambiar el TTL del registro DNS de `salta.dev` a **300 segundos** (5 min). Esperar al menos 48 horas antes del cutover para que el TTL bajo se propague.

---

## Fase 2: Provisionar GCP VM (Día 2)

### 2.1 Crear proyecto y VM

```bash
# Crear proyecto
gcloud projects create saltadev-project
gcloud config set project saltadev-project

# Habilitar Compute Engine
gcloud services enable compute.googleapis.com

# Crear VM (free tier: e2-micro en us-central1)
gcloud compute instances create saltadev-web \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=30GB \
  --boot-disk-type=pd-standard \
  --tags=http-server,https-server
```

### 2.2 Firewall y IP estática

```bash
# Firewall HTTP/HTTPS
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 --target-tags=http-server
gcloud compute firewall-rules create allow-https \
  --allow tcp:443 --target-tags=https-server

# IP estática (necesaria para el registro DNS tipo A)
gcloud compute addresses create saltadev-ip --region=us-central1

# Asignar IP al VM
gcloud compute instances delete-access-config saltadev-web \
  --zone=us-central1-a --access-config-name="external-nat"
gcloud compute instances add-access-config saltadev-web \
  --zone=us-central1-a \
  --address=$(gcloud compute addresses describe saltadev-ip \
    --region=us-central1 --format='get(address)')

# Anotar la IP para usarla en DNS
gcloud compute addresses describe saltadev-ip --region=us-central1 --format='get(address)'
```

### 2.3 Configurar VM (via SSH)

```bash
gcloud compute ssh saltadev-web --zone=us-central1-a
```

**Swap (esencial para 1GB RAM):**
```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

**Docker:**
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
# Re-login para que el grupo docker tenga efecto
exit
gcloud compute ssh saltadev-web --zone=us-central1-a
```

---

## Fase 3: Deploy (Día 3)

### 3.1 Clonar y configurar

```bash
sudo mkdir -p /opt/saltadev && sudo chown $USER:$USER /opt/saltadev
cd /opt/saltadev
git clone https://github.com/Salta-Dev/saltadev-website.git .
```

### 3.2 Crear `.env.production`

```bash
cp saltadev/.env.production.example saltadev/.env.production
nano saltadev/.env.production
# Llenar con valores reales:
# - SECRET_KEY (generar con: python -c "import secrets; print(secrets.token_urlsafe(50))")
# - DATABASE_URL (Neon connection string)
# - REDIS_URL (Upstash connection string, con rediss://)
# - RESEND_API_KEY
# - Cloudinary, reCAPTCHA, Google OAuth
```

### 3.3 Build y test inicial

```bash
cd /opt/saltadev

# Build
docker compose -f docker/docker-compose.gcp.yml build

# Levantar solo web para verificar health
docker compose -f docker/docker-compose.gcp.yml up web

# En otra terminal, verificar health
curl http://localhost:8000/health/
# Respuesta esperada:
# {"status": "healthy", "services": {"django": "ok", "postgres": "ok", "redis": "ok"}}
```

---

## Fase 4: SSL y Nginx (Día 3-4)

El certificado SSL debe obtenerse antes de levantar nginx en modo producción, ya que `nginx/production.conf` ya referencia los archivos de letsencrypt.

### 4.1 Config temporal para obtener certificado

Crear `nginx/initial-cert.conf`:
```nginx
server {
    listen 80;
    server_name salta.dev;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 'Configurando SSL...';
        add_header Content-Type text/plain;
    }
}
```

Levantar nginx con la config temporal y obtener el certificado:
```bash
# Levantar nginx con config temporal (ajustar el volume mount)
docker run -d --name nginx-tmp \
  -p 80:80 \
  -v /opt/saltadev/nginx/initial-cert.conf:/etc/nginx/conf.d/default.conf:ro \
  -v certbot_www:/var/www/certbot \
  nginx:alpine

# Obtener certificado (el DNS ya debe apuntar al GCP VM)
docker compose -f docker/docker-compose.gcp.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email admin@salta.dev --agree-tos --no-eff-email \
  -d salta.dev

# Detener nginx temporal
docker stop nginx-tmp && docker rm nginx-tmp

# Levantar stack completo con production.conf
docker compose -f docker/docker-compose.gcp.yml up -d
```

**Nota:** Si el DNS todavía apunta a Render al momento de obtener el certificado, se puede usar el challenge DNS en modo manual:
```bash
docker compose -f docker/docker-compose.gcp.yml run --rm certbot certonly \
  --manual --preferred-challenges dns \
  --email admin@salta.dev --agree-tos --no-eff-email \
  -d salta.dev
```

### 4.2 Auto-renovación SSL

```bash
# Agregar cron para renovar certificados cada 2 semanas
(crontab -l 2>/dev/null; echo "0 3 1,15 * * cd /opt/saltadev && docker compose -f docker/docker-compose.gcp.yml run --rm certbot renew --quiet && docker compose -f docker/docker-compose.gcp.yml exec nginx nginx -s reload") | crontab -
```

---

## Fase 5: Cutover DNS (Día 4-5)

### 5.1 Transición con base de datos compartida

Antes de cambiar el DNS, apuntar Render a la misma base Neon para evitar inconsistencias durante la propagación:
1. En Render dashboard → Web Service → Environment
2. Cambiar `DATABASE_URL` al connection string de Neon
3. Redeploy Render
4. Ahora Render y GCP usan la misma DB

### 5.2 Cambiar registro DNS

En el proveedor DNS de `salta.dev`:
```
# Antes (Render)
salta.dev  CNAME  saltadev-website.onrender.com

# Después (GCP)
salta.dev  A  <GCP_STATIC_IP>
```

### 5.3 Verificar propagación y funcionalidad

```bash
# Verificar propagación DNS
dig salta.dev +short
# Debe mostrar la IP del GCP VM

# Verificar SSL y health
curl -I https://salta.dev/health/

# Verificar funcionalidad completa
# - Login/registro
# - Email de verificación (Resend)
# - Eventos
# - Imágenes (Cloudinary)
# - Sesiones (Upstash)
```

---

## Fase 6: Post-migración (Día 5-7+)

### 6.1 Monitoreo con UptimeRobot

Registrar en [UptimeRobot](https://uptimerobot.com) (gratis) para monitorear `https://salta.dev/health/` cada 5 minutos. Esto también mantiene Neon "warm", evitando los cold starts de su auto-suspend tras 5 min de inactividad.

### 6.2 Comandos de mantenimiento

```bash
# Ver logs en tiempo real
docker compose -f docker/docker-compose.gcp.yml logs -f --tail=100

# Ver uso de memoria
docker stats --no-stream
free -h

# Limpieza semanal de Docker (agregar al crontab)
# 0 4 * * 0 docker system prune -f
```

### 6.3 Actualizar deploy (pull + rebuild)

```bash
cd /opt/saltadev
git pull origin main
docker compose -f docker/docker-compose.gcp.yml build
docker compose -f docker/docker-compose.gcp.yml up -d
```

### 6.4 Descomisionar Render

Una vez que GCP lleve 1 semana estable:
1. Eliminar web service en Render
2. Eliminar PostgreSQL en Render (hacer backup final primero)
3. Eliminar Redis en Render
4. Subir TTL del DNS de 300 a 3600 segundos

---

## Limitaciones y Consideraciones

### Neon Free Tier

| Limitación | Detalle | Mitigación |
|------------|---------|------------|
| **Auto-suspend** | Compute se suspende tras 5 min sin actividad. Cold start de ~1-3s | UptimeRobot cada 5 min |
| **Storage** | 0.5GB | Monitorear con `SELECT pg_database_size('saltadev');` |
| **Conexiones** | 100 max | Con 2 workers + `conn_max_age=600`, se usan ~2 conexiones |

### Upstash Free Tier

| Limitación | Detalle | Mitigación |
|------------|---------|------------|
| **Comandos/día** | 10K comandos/día | Soporta ~2,000-3,300 views/día (3-5 cmds por request) |
| **Si se alcanza el límite** | Cache/sesiones fallan | Cambiar sesiones a DB: `SESSION_ENGINE = "django.contrib.sessions.backends.db"` en `production.py` |

### Latencia

GCP VM en us-central1 + Neon/Upstash en São Paulo ≈ 100-150ms por query. Aceptable para tráfico bajo de una comunidad. Si la latencia es un problema, considerar mover la VM a la región `southamerica-east1` (~$7/mes).

---

## Rollback

Si algo falla después del cutover DNS:

1. Cambiar DNS de vuelta al CNAME de Render: `salta.dev → saltadev-website.onrender.com`
2. En Render, revertir `DATABASE_URL` al PostgreSQL original de Render (válido 90 días después de eliminarlo)
3. Render permanece activo como fallback hasta confirmar estabilidad de GCP

---

## Verificación Final

- [ ] `curl https://salta.dev/health/` → `{"status": "healthy"}`
- [ ] Registrar usuario nuevo → recibe email de verificación (Resend)
- [ ] Login → sesión funciona (Upstash)
- [ ] Ver eventos → imágenes cargan (Cloudinary)
- [ ] `docker stats --no-stream` → memoria total bajo 800MB
- [ ] `dig salta.dev +short` → IP del GCP VM
- [ ] UptimeRobot configurado en `https://salta.dev/health/`
