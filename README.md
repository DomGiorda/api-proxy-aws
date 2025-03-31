# api-proxy-aws
## Funcionalidad y Features

API Proxy desarrollado en python, disenhado para ejecutarse de manera serverless en AWS Lambda. Infraestructura desplegada con Terraform.
Tambien, posee una version local para ejecutar pruebas antes del despliegue.
Los features del API Proxy son:


* **Rate Limiting Basado en Rutas:** Implementa un sistema de limitacion de requests configurable basado en los patrones de las rutas solicitadas. Esto ayuda a proteger la API de Mercado Libre y a garantizar un uso justo del servicio.
* **Despliegue en AWS:** Disenhado para ser desplegado en la infraestructura de AWS Cloud utilizando servicios serverless: AWS Lambda y API Gateway.
* **Infraestructura como Código con Terraform:** La creacion y gestion de la infraestructura en AWS se automatiza mediante Terraform.
* **Unit Testing:** Se incluyen pruebas unitarias para verificar la correcta implementacion de la logica de rate limiting, asegurando la fiabilidad del proxy.
* **Entorno de Desarrollo Local con Docker:** Se proporciona un entorno de desarrollo local utilizando Docker, lo que facilita la prueba y el desarrollo del proxy sin necesidad de desplegarlo en AWS.
* **Escalabilidad Automática:** La escalabilidad del proxy está gestionada por AWS API Gateway, que puede ajustarse dinamicamente para manejar diferentes niveles de trafico.
* **Restricciones por IP:** Se utiliza un array de ip's para definir aquellas permitidas, utilizando el rate-limit para dichas ip's. Por otro lado, si no esta en la lista o explicitamente existe en la lista de ip's denegadas, el proxy debe retornar 403 - Forbidden
* **Configuración Flexible de Límites:** Los limites de requests para diferentes rutas se definen en un diccionario, lo que permite la modificación y adaptacion a diferentes necesidades.
* **Registro de Solicitudes:** La funcion Lambda incluye logging basico para facilitar la monitorizacion y la depuracion del proxy. 
* **Exposicion de metricas:** Las metricas son expuestas por el propio AWS API Gateway. Se pueden consumir con cloudwatch. [CloudWatch](https://docs.aws.amazon.com/apigateway/latest/developerguide/metrics_dimensions_view_in_cloud_watch.html).


### Diagrama de arquitectura
Enlace a diagrama de arquitectura en Draw.io [API-proxy](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&dark=auto#G1Z2xuJuKynGVkD0Pps90aQWFyK2bARxaA)

![Diagrama de Arquitectura](assets/api-proxy-aws.v1.jpg)

### Diagrama de clases
 
 Enlace al diagrama de clases en Draw.io [Diagram-Class](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&dark=auto#G1PZrMIHtngEEVH7ewyhYBag6lFQ5dyzc4)

![Diagrama-de-Clases](assests/diagram-class.v1.jpg)

### Uso con Docker para Pruebas locales 

El `Dockerfile` fue desarrollado para lograr una ejecucion local del API proxy. Para utilizarlo con el script `main.py` para desarrollo local:

1.  **Construye la imagen de Docker:** En la raiz, ejecuta el siguiente comando:

    ```bash
    docker build . -t proxy-api:0.0.1  
    ```



2.  **Ejecuta el contenedor de Docker:** Una vez que la imagen se haya construido, puedes ejecutar un contenedor basado en esa imagen, exponiendo el puerto donde se ejecuta `main.py` (por defecto el puerto 8080):

    ```bash
    docker run api-proxy -p 8080:8080
    ```
.

3.  **Accede al proxy localmente:** Ahora puedes enviar solicitudes HTTP al proxy localmente a través de `http://localhost:8080`. El script `main.py` actuara como un servidor web que invoca la función `lambda_handler` con la solicitud recibida. Por ejemplo:

    ```bash
    curl http://localhost:8080/sites/MLA/categories
    ```

#### Herramientas necesarias:
1. **Python:** [Python](https://wiki.python.org/moin/BeginnersGuide/Download)
2. **Terraform:** [Terraform](https://wiki.python.org/moin/BeginnersGuide/Download)
3. **AWS Cli:** [AWSCLI-V2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
4. **Docker:** [Docker-Engine](https://docs.docker.com/engine/install/)
