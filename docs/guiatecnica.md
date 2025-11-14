# Guía Técnica del proceso de indicadores de Costa Rica




## Ejemplo de ejecución

Para correr el proceso de forma manual, se debe realizar lo siguiente: Se debe abrir el puerto del PostgreSQL para que este pueda realizar cargas de datos y se puedan manipular los datos con Python. Se debe configurar el `<USUARIO>` con su usuario, luego aparece un prompt para colocar la contraseña.  


```bash
ssh -N -L 5433:127.0.0.1:5433 <USUARIO>@sgo-ub24-sea-d1
```
