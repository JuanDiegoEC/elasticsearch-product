# app/ingestion.py
import pandas as pd
from elasticsearch import helpers
from client import connect_elasticsearch
from sentence_transformers import SentenceTransformer

# Inicializa el modelo (uno ligero para pruebas)
model = SentenceTransformer('all-MiniLM-L6-v2')


INDEX_NAME = "amazon_products"

# Define el mapping del índice
MAPPING = {
    "mappings": {
        "properties": {
            "name": {"type": "text"},
            "main_category": {"type": "keyword"},
            "sub_category": {"type": "keyword"},
            "ratings": {"type": "float"},
            "no_of_ratings": {"type": "integer"},
            "discount_price": {"type": "float"},
            "actual_price": {"type": "float"},
            "image": {"type": "keyword"},
            "link": {"type": "keyword"},
            "embedding": {"type": "dense_vector", "dims": 384}
        }
    }
}


def create_index(es):
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=MAPPING)
        print(f"Índice '{INDEX_NAME}' creado.")
    else:
        print(f"El índice '{INDEX_NAME}' ya existe.")

def load_data(es):
    df = pd.read_csv("data/All_Electronics.csv")
    df = df.fillna("")

    # Crear descripción combinada y generar embeddings
    df["text_for_embedding"] = df["name"].astype(str) + " " + df["main_category"].astype(str) + " " + df["sub_category"].astype(str)
    df["embedding"] = df["text_for_embedding"].apply(lambda x: model.encode(x).tolist())


    # Eliminar comillas y símbolos de moneda
    df["discount_price"] = df["discount_price"].astype(str).replace('[₹,"]', '', regex=True).replace('', 0).astype(float)
    df["actual_price"] = df["actual_price"].astype(str).replace('[₹,"]', '', regex=True).replace('', 0).astype(float)

    # ratings y no_of_ratings a numéricos seguros
    df["ratings"] = pd.to_numeric(df["ratings"], errors='coerce').fillna(0).astype(float)
    df["no_of_ratings"] = pd.to_numeric(df["no_of_ratings"], errors='coerce').fillna(0).astype(int)

    actions = [
        {
            "_index": INDEX_NAME,
            "_source": row.to_dict()
        }
        for _, row in df.iterrows()
    ]

    print(f"🔄 Cargando {len(actions)} documentos...")
    success, errors = helpers.bulk(es, actions, stats_only=False, raise_on_error=False)
    print(f"✅ {success} documentos cargados.")
    if errors:
        print(f"⚠️ {len(errors)} documentos fallaron.")


if __name__ == "__main__":
    es = connect_elasticsearch()
    # Justo antes de crear el índice, borra si ya existe
    if es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        print(f"🗑 Índice '{INDEX_NAME}' eliminado.")

    create_index(es)
    load_data(es)
