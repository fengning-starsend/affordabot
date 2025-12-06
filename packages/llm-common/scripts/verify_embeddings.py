import asyncio
import os
from llm_common.embeddings.openai import OpenAIEmbeddingService

async def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return

    print("init service...")
    # Use text-embedding-3-small
    service = OpenAIEmbeddingService(api_key=api_key)
    
    print("embedding query 'hello world'...")
    vec = await service.embed_query("hello world")
    print(f"✅ Query embedding dim: {len(vec)}")
    
    print("embedding batch...")
    vecs = await service.embed_documents(["doc1", "doc2"])
    print(f"✅ Batch embedding dims: {[len(v) for v in vecs]}")

if __name__ == "__main__":
    asyncio.run(main())
