
README - Buscador de Productos con ElasticSearch y Flask

Este proyecto implementa un sistema de búsqueda inteligente de productos usando ElasticSearch, Flask y embeddings generados con sentence-transformers. Incluye una interfaz gráfica donde puedes buscar por texto, por semántica o encontrar productos similares.

====================
Estructura del Proyecto
====================
ELASTICSEARCH_PROJECT/
├── app/
│   ├── static/                    # Archivos estáticos (CSS)
│   ├── templates/
│   │   └── index.html             # Interfaz HTML
│   ├── client.py                 # Conexión con ElasticSearch
│   ├── load.py                   # Carga de datos y embeddings
│   ├── main.py                   # API + interfaz Flask
│   └── mustache_template.json    # Template de búsqueda clásica
├── data/
│   └── All_Electronics.csv       # Dataset original
├── requirements.txt              # Dependencias
└── venv/                         # Entorno virtual

====================
Instalación y Ejecución
====================
1. Instala las dependencias:
    pip install -r requirements.txt

2. Genera el índice y los embeddings:
    python app/load.py

3. Corre el servidor Flask:
    python app/main.py

4. Abre tu navegador en:
    http://localhost:5000/

====================
Modos de Búsqueda en la Interfaz
====================
- Búsqueda Semántica: por significado, usando embeddings y cosineSimilarity.
- Búsqueda Tradicional: por texto exacto (match/multi-match).
- Productos Similares: ingresa el nombre de un producto y encuentra los 5 más parecidos.

====================
Endpoints disponibles
====================
- /buscar?q=... → Tradicional (match)
- /buscar_semantico?q=... → Por significado
- /similar_products?name=... → Productos similares
- / → Interfaz gráfica con selector de modo

