import chromadb
from chromadb.config import Settings
import json
import csv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings


class MyDatabase:
    def __init__(self):
        # Settings(persist_directory="./chroma_db")
        self.chroma_client = chromadb.Client()
        self.initialize()

    def get_collection(self):
        return self.chroma_client.get_or_create_collection(name="bhagavat_gita")

    def initialize(self):
        print("Adding Data ...")
        collection = self.get_collection()
        # Read CSV data into a list of dictionaries
        print("Loading Bhagavat Gita ...")
        with open(
            "./data/gita_data.csv", mode="r", newline="", encoding="utf-8"
        ) as csvfile:
            documents = list(csv.DictReader(csvfile))
            # with open("./gita_data.json", "r") as f:
            # documents = json.load(f)
            with open("./data/gita_data_new.json", "w") as f:
                json.dump(documents, f, indent=1)
            collection.add(
                documents=[document["translation"] for document in documents],
                metadatas=[
                    {
                        "source": "bhagavat_gita",
                        "chapter_number": document["chapter_number"],
                        "verse_number": document["chapter_verse"],
                    }
                    for document in documents
                ],
                # [
                #     {"source": "article1"},
                #     {"source": "article2"},
                #     {"source": "article3"},
                # ],
                # ids=["doc1", "doc2", "doc3"],
                ids=[f"doc{i}" for i, document in enumerate(documents)],
            )

        # print("Loading Vishnu Puranam ...")
        # loader = PyPDFLoader("./data/vishnu_puranam.pdf")
        # pdfDocument = loader.load()
        # print("pdfDocument", pdfDocument)
        # with open("./data/vishnu_puranam.json","w") as f:
        #         json.dump([doc.model_dump_json() for doc in pdfDocument], f, indent=1)

        # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        # chunked_documents = text_splitter.split_documents([pdfDocument])
        # print(chunked_documents)
        print("Added data ...")

    def get_data(self, query: str = "is knowledge superior to action?"):
        print("Querying data ...")
        collection = self.get_collection()
        results = collection.query(
            query_texts=[
                query,
            ],  # Chroma will embed this for you
            n_results=5,  # how many results to return
        )
        print(json.dumps(results, indent=2))
        return results


# mydb = MyDatabase()
# mydb.initialize()
# mydb.get_data("What is karma?")
