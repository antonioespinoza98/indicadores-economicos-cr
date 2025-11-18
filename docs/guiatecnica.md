# Guía Técnica del proceso de indicadores de Costa Rica

# Tabla de contenidos

1. [Prerrequisitos](#prerrequisitos)
2. [Instalación del ambiente](#instalación-del-ambiente)
3. [Configuración](#configuración)
4. [Ejemplo de ejecución](#ejemplo-de-ejecución-manual)


## Prerrequisitos

Para desarrollar la aplicación se utilizó Python en su versión 3.10, PostgreSQL y DBeaver como interfaz para interactuar con la base de datos. 
Además, debe contar con un acceso al servidor de la Comisión Económica para América Latina y el Caribe (CEPAL) para poder interactuar con la base de datos, además de un usuario y contraseña. 

## Instalación del ambiente

En un powershell ejecute la siguiente línea de código. El ambiente por default se crea bajo el nombre de `indenv` pero este puede ser ajustado al nombre que prefiera el usuario. Se instala Python en su versión 3.10 y se instalan las dependencias que están en el archivo `requirements.txt`

```bash
conda create -n indenv --file requirements.txt python=3.10
```

## Configuración 

La extracción de los datos se realiza mediante la clase de Python `BccrAPI` que se encuentra en el archivo `core.py`, esta función establece una conexión por medio de un API KEY brindado por el Banco Central de Costa Rica (BCCR) y mediante el método `get()` extrae los datos, los depura y los inserta en la base de datos en PostgreSQL. 
Para poder realizar la extracción, debe poseer un **API KEY** que puede obtener en el siguiente enlace oficial del [BCCR](https://www.bccr.fi.cr/indicadores-economicos/suscripci%C3%B3n-a-indicadores). 
Una vez que obtenga el API KEY, debe colocarlo en el archivo `conf.ini`, que es un archivo de configuración que la clase de python `BccrAPI` lee para ingresar a los indicadores. El archivo debe contener **al menos** dos parámetros. Uno principal para los indicadores y otro opcional para extraer el catálogo oficial de indicadores. 
Puede tomar la siguiente plantilla, donde **únicamente** debe cambiar el valor en **token**. 

```ini
[BCCR-CATALOGO]
url: https://apim.bccr.fi.cr/
endpoint: SDDE/api/Bccr.GE.SDDE.Publico.Indicadores.API/indicadoresEconomicos/descargar?idioma=ES
token: AQUI_INGRESE_TOKEN

[BCCR-INDICADORES]
url: https://apim.bccr.fi.cr/
token: AQUI_INGRESE_TOKEN
```

También, asegúrese de tener un archivo `.env` donde debe colocar los credenciales de PostgreSQL. Tome la siguiente plantilla para la configuración de la base de datos, debe modificar únicamente: USERNAME, PASSWORD, HOST, PORT y DATABASE. 

```env
SQL_URL="postgresql+psycopg2://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>"
```


## Ejemplo de ejecución manual

Para correr el proceso de forma manual, se debe realizar lo siguiente: Se debe abrir el puerto del PostgreSQL para que este pueda realizar cargas de datos y se puedan manipular los datos con Python. Se debe configurar el `<USUARIO>` con su usuario, luego aparece un prompt para colocar la contraseña.  


```bash
ssh -N -L 5433:127.0.0.1:5433 <USUARIO>@sgo-ub24-sea-d1
```
