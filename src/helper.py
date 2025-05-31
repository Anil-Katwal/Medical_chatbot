from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os

# Load Pinecone API key securely
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise EnvironmentError("PINECONE_API_KEY is not set.")
os.environ["PINECONE_API_KEY"] = api_key

# Load and split PDFs
def load_pdf_file(data: str):
    loader = DirectoryLoader(data, glob="**/*.pdf", loader_cls=PyMuPDFLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)

    # Filter empty chunks and large ones
    filtered = []
    for i, doc in enumerate(texts):
        size = len(doc.page_content.encode('utf-8'))
        if 0 < size < 4_000_000:
            # Optionally simplify metadata
            doc.metadata = {
                "source": doc.metadata.get("source", "")[:100],
                "page": doc.metadata.get("page", -1)
            }
            filtered.append(doc)
        elif size >= 4_000_000:
            print(f"⚠️ Skipping large chunk {i}: {size} bytes")
    return filtered

# Define embedding function
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')

# Load PDFs and get text chunks
data_directory = "./Data/"
text_chunks = load_pdf_file(data_directory)

# Initialize embedding model
embeddings = get_embedding_model()

# Verify embedding dimension
sample_embedding = embeddings.embed_query("test")
embedding_dim = len(sample_embedding)
print(f"Embedding dimension: {embedding_dim}")

# Initialize Pinecone
pc = Pinecone(api_key=api_key)
index_name = "medicalchatbot"

# Create or get existing index
if index_name in pc.list_indexes().names():
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    if stats['dimension'] != embedding_dim:
        raise ValueError(f"Existing index dimension {stats['dimension']} does not match embedding dimension {embedding_dim}")
else:
    pc.create_index(name=index_name, dimension=embedding_dim, metric="cosine")

# Batch upload documents to Pinecone
batch_size = 50
for i in range(0, len(text_chunks), batch_size):
    batch = text_chunks[i:i + batch_size]
    print(f"📤 Uploading batch {i // batch_size + 1} with {len(batch)} documents...")
    PineconeVectorStore.from_documents(
        documents=batch,
        index_name=index_name,
        embedding=embeddings
    )

# Test a sample query
query = "What medical topics are covered in the PDFs?"
docsearch = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
results = docsearch.similarity_search(query, k=1)
print("🔍 Top result:\n", results[0].page_content)

#load Existing Index
from langchain_pinecone import PineconeVectorStore
docsearch=PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
    
)

