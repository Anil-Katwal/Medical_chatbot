from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

system_prompt=(
    "you are an assistant for question_answering tasks."
    "Use the following pieces of retrived context to answer"
    "the question. If you don't know the answer say that you "
    "don't know. use the three sentences maximum and keep the"
    "answer concise."
    "\n\n"
    "{context}"
)
prompt= ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human","{input}"),
    ]
)
question_answer_chain=create_stuff_documents_chain(llm, prompt)
rag_chain=create_retrieval_chain(retriever, question_answer_chain)

response=rag_chain.invoke({"input":"what is Ache?"})
print(response["answer"])