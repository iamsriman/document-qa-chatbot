from collections import defaultdict

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()


class EmbeddingService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = "./chroma_db"

    def create_vector_store(self, chunks: list, document_id: str):
        metadatas = [
            {
                "document_id": document_id,
                "chunk_id": index,
            }
            for index in range(len(chunks))
        ]

        return Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory,
            collection_name=f"doc_{document_id}",
        )

    def get_vector_store(self, document_id: str):
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"doc_{document_id}",
        )

    def create_multi_doc_vector_store(self, all_chunks: list, session_id: str):
        texts = []
        metadatas = []

        for chunks, document_id in all_chunks:
            for chunk_index, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append(
                    {
                        "document_id": str(document_id),
                        "chunk_id": chunk_index,
                    }
                )

        return Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory,
            collection_name=f"session_{session_id}",
        )

    def get_session_vector_store(self, session_id: str):
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"session_{session_id}",
        )

    def list_document_ids(self, vector_store) -> list[str]:
        collection = vector_store.get(include=["metadatas"])
        metadatas = collection.get("metadatas", [])
        document_ids = {
            str(metadata.get("document_id"))
            for metadata in metadatas
            if metadata and metadata.get("document_id") is not None
        }
        return sorted(document_ids, key=lambda value: (len(value), value))

    def retrieve_balanced_chunks(self, vector_store, query: str, per_document_k: int = 3) -> list[dict]:
        document_ids = self.list_document_ids(vector_store)
        if not document_ids:
            return []

        results_by_document = defaultdict(list)

        for document_id in document_ids:
            matches = vector_store.similarity_search_with_score(
                query,
                k=per_document_k,
                filter={"document_id": document_id},
            )

            for rank, (doc, distance) in enumerate(matches):
                metadata = doc.metadata or {}
                score = 1.0 / (1.0 + float(distance))
                results_by_document[document_id].append(
                    {
                        "document_id": document_id,
                        "chunk_id": metadata.get("chunk_id"),
                        "content": doc.page_content,
                        "distance": float(distance),
                        "score": round(score, 4),
                        "rank": rank,
                    }
                )

            results_by_document[document_id].sort(key=lambda item: item["score"], reverse=True)

        if not any(results_by_document.values()):
            return []

        interleaved_results = []
        max_rank = max(len(items) for items in results_by_document.values())
        for rank in range(max_rank):
            for document_id in document_ids:
                document_results = results_by_document.get(document_id, [])
                if rank < len(document_results):
                    interleaved_results.append(document_results[rank])

        print("Retrieved chunks:")
        for chunk in interleaved_results:
            print(
                f"  doc={chunk['document_id']} chunk={chunk['chunk_id']} "
                f"distance={chunk['distance']:.4f} score={chunk['score']:.4f}"
            )

        return interleaved_results
