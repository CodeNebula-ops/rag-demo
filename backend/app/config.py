from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://kb_user:kb_secret_2024@localhost:5432/knowledge_base"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "document_chunks"
    qdrant_embedding_dim: int = 384

    groq_api_key: str = ""
    groq_model_name: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    retrieval_top_k: int = 20
    rerank_top_n: int = 5
    chunk_size: int = 400
    chunk_overlap: int = 80
    max_conversation_history: int = 5
    confidence_threshold: float = 0.7
    llm_temperature: float = 0.1
    max_tokens: int = 512

    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()
