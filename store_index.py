from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

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


def load_pdf_file(data: str):
    print("Starting to load PDF files...")

    # Use PyMuPDFLoader instead of PyPDFLoader for faster loading
    loader = DirectoryLoader(
        data,
        glob="**/*.pdf",
        loader_cls=PyMuPDFLoader  # ← updated here
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks")

    return texts
extracted_data=load_pdf_file(data='Data/')


#load Existing Index
from langchain_pinecone import PineconeVectorStore
docsearch=PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
    
)
docsearch
retriever=docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})