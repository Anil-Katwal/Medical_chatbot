from flask import Flask, request, jsonify, render_template
from src.helper import download_hugging_face_embeddings

from langchain.vectorstores import Pinecone  
from langchain.chat_models import ChatOpenAI  
from langchain.prompts import ChatPromptTemplate  
from langchain.chains.combine_documents import create_stuff_documents_chain  
from langchain.chains import create_retrieval_chain  

from dotenv import load_dotenv  
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

if not api_key:
    raise EnvironmentError("PINECONE_API_KEY is not set.")
if not XAI_API_KEY:
    raise EnvironmentError("XAI_API_KEY is not set.")

os.environ["PINECONE_API_KEY"] = api_key
os.environ["XAI_API_KEY"] = XAI_API_KEY

# Initialize Flask app
app = Flask(__name__)

# Get embeddings
embeddings = download_hugging_face_embeddings()

# Set up vectorstore retriever from Pinecone (this should already be created)
# Example assumes an index and namespace are available
retriever = Pinecone.from_existing_index(
    index_name="medicalchatbot",  
    embedding=embeddings,
    namespace="Anil"              
).as_retriever()

# Initialize XAI LLM
from langchain_xai import ChatXAI
llm = ChatXAI(
    model="grok-beta",
    temperature=0.4,
    max_tokens=500,
    api_key=XAI_API_KEY
)

# Prompt template
system_prompt = "You are a helpful assistant. Answer clearly and concisely."
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# Build RAG pipeline
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Routes
@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.args.get("msg")  # For GET
    if not msg and request.method == "POST":
        msg = request.form.get("msg")  # For POST

    if not msg:
        return jsonify({"error": "No input message provided."}), 400

    try:
        response = rag_chain.invoke({"input": msg})
        answer = response.get("answer", "No answer found.")
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080,debug=True)
