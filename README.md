# FastAPI Financial Extractor – Starter Template

Este proyecto mínimo contiene todo lo necesario para desplegar en **Railway** o correr en local una API FastAPI que acepte archivos y devuelva un _stub_ de respuesta.

## Estructura

```
main.py            # Lógica de la API
requirements.txt   # Dependencias Python
Dockerfile         # Imagen para producción
```

## Despliegue rápido en Railway

1. Crea un nuevo proyecto en Railway y elige **Deploy from GitHub** o **Deploy from Zip**.
2. Sube este zip o conecta tu repo con estos mismos archivos.
3. Railway detectará el `Dockerfile` y lo construirá automáticamente.
4. Una vez desplegado, expón el puerto `8000` y visita la URL pública:
   ```
   https://<tu-subdominio>.up.railway.app
   ```
   Deberías ver:
   ```json
   { "status": "ok" }
   ```

## Ejecución local

```bash
# 1. Descomprime el zip y entra al directorio
pip install -r requirements.txt
uvicorn main:app --reload
```

Abre http://127.0.0.1:8000 en tu navegador.

---

*Generado: 2025-05-15T07:58:57.603625 UTC*
