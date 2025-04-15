import chromadb
from chromadb.config import Settings
import time
import logging
from typing import List, Dict, Any, Optional
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChromaDBClient:
    """A wrapper class for ChromaDB operations with enhanced error handling and retries."""
    
    def __init__(
        self, 
        host: str = "chroma", 
        port: int = 8000,
        max_retries: int = 5,
        retry_delay: int = 2,
        allow_reset: bool = True,
        anonymized_telemetry: bool = False
    ):
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.settings = Settings(
            allow_reset=allow_reset,
            anonymized_telemetry=anonymized_telemetry,
            chroma_api_impl="rest"
        )
        self.client = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to ChromaDB with retries."""
        attempts = 0
        while attempts < self.max_retries:
            try:
                logger.info(f"Connecting to ChromaDB at {self.host}:{self.port} (attempt {attempts+1}/{self.max_retries})")
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=self.settings
                )
                self.client.heartbeat()
                logger.info("Successfully connected to ChromaDB")
                return
            except Exception as e:
                attempts += 1
                logger.warning(f"Connection attempt {attempts} failed: {str(e)}")
                if attempts >= self.max_retries:
                    logger.error(f"Failed to connect after {self.max_retries} attempts")
                    raise ConnectionError(f"Could not connect to ChromaDB: {str(e)}")
                time.sleep(self.retry_delay)
    
    def get_or_create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """Get or create a collection with retries."""
        attempts = 0
        while attempts < self.max_retries:
            try:
                collection = self.client.get_or_create_collection(name=name, metadata=metadata)
                logger.info(f"Collection '{name}' accessed successfully")
                return collection
            except Exception as e:
                attempts += 1
                logger.warning(f"Collection access attempt {attempts} failed: {str(e)}")
                if attempts >= self.max_retries:
                    logger.error(f"Failed to access collection after {self.max_retries} attempts")
                    raise
                time.sleep(self.retry_delay)
                
                if attempts % 2 == 0:
                    logger.info("Attempting to reconnect to ChromaDB")
                    self._connect()
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """Add documents to a collection with proper error handling."""
        collection = self.get_or_create_collection(collection_name)
        
        try:
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            logger.info(f"Successfully added {len(documents)} documents to '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise

    def query_collection(
        self,
        collection_name: str,
        query_texts: List[str] | str,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query a collection with proper error handling."""
        collection = self.get_or_create_collection(collection_name)
        
        try:
            if isinstance(query_texts, str):
                query_texts = [query_texts]
                
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            logger.info(f"Successfully queried collection '{collection_name}'")
            return results
        except Exception as e:
            logger.error(f"Failed to query collection: {str(e)}")
            raise


def load_sample_data(chroma_client: ChromaDBClient) -> None:
    """Load sample data into ChromaDB."""
    documents = [
        "Mars, often called the 'Red Planet', has captured the imagination of scientists and space enthusiasts alike.",
        "The Hubble Space Telescope has provided us with breathtaking images of distant galaxies and nebulae.",
        "The concept of a black hole, where gravity is so strong that nothing can escape it, was first theorized by Albert Einstein's theory of general relativity.",
        "The Renaissance was a pivotal period in history that saw a flourishing of art, science, and culture in Europe.",
        "The Industrial Revolution marked a significant shift in human society, leading to urbanization and technological advancements.",
        "The ancient city of Rome was once the center of a powerful empire that spanned across three continents.",
        "Dolphins are known for their high intelligence and social behavior, often displaying playful interactions with humans.",
        "The chameleon is a remarkable creature that can change its skin color to blend into its surroundings or communicate with other chameleons.",
        "The migration of monarch butterflies spans thousands of miles and involves multiple generations to complete.",
        "Christopher Nolan's 'Inception' is a mind-bending movie that explores the boundaries of reality and dreams.",
        "The 'Lord of the Rings' trilogy, directed by Peter Jackson, brought J.R.R. Tolkien's epic fantasy world to life on the big screen.",
        "Pixar's 'Toy Story' was the first feature-length film entirely animated using computer-generated imagery (CGI).",
        "Superman, known for his incredible strength and ability to fly, is one of the most iconic superheroes in comic book history.",
        "Black Widow, portrayed by Scarlett Johansson, is a skilled spy and assassin in the Marvel Cinematic Universe.",
        "The character of Iron Man, played by Robert Downey Jr., kickstarted the immensely successful Marvel movie franchise in 2008."
    ]

    metadatas = [
        {'source': "Space", 'added_date': '2025-04-15'}, 
        {'source': "Space", 'added_date': '2025-04-15'}, 
        {'source': "Space", 'added_date': '2025-04-15'}, 
        {'source': "History", 'added_date': '2025-04-15'}, 
        {'source': "History", 'added_date': '2025-04-15'}, 
        {'source': "History", 'added_date': '2025-04-15'}, 
        {'source': "Animals", 'added_date': '2025-04-15'}, 
        {'source': "Animals", 'added_date': '2025-04-15'}, 
        {'source': "Animals", 'added_date': '2025-04-15'}, 
        {'source': "Movies", 'added_date': '2025-04-15'}, 
        {'source': "Movies", 'added_date': '2025-04-15'}, 
        {'source': "Movies", 'added_date': '2025-04-15'}, 
        {'source': "Superheroes", 'added_date': '2025-04-15'}, 
        {'source': "Superheroes", 'added_date': '2025-04-15'}, 
        {'source': "Superheroes", 'added_date': '2025-04-15'}
    ]
    
    ids = [f"doc_{i+1}" for i in range(len(documents))]

    chroma_client.add_documents(
        collection_name="sample_collection",
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )


def main():
    """Main function to demonstrate ChromaDB usage."""
    host = os.environ.get("CHROMA_HOST", "chroma")
    port = int(os.environ.get("CHROMA_PORT", "8000"))
    
    try:
        chroma_client = ChromaDBClient(host=host, port=port)
        
        # Load sample data
        load_sample_data(chroma_client)

        print("\n--- Loaded the data sucessfully ---")

        results = chroma_client.query_collection(
            collection_name="sample_collection",
            query_texts="Give me some facts about space",
            n_results=3
        )
        
        print("\n--- Space Facts Query Results ---")
        for doc in results["documents"][0]:
            print(f"• {doc}")
            
        # 2. Query with category filter
        results = chroma_client.query_collection(
            collection_name="sample_collection",
            query_texts="Tell me about superheroes",
            n_results=3,
            where={"source": "Superheroes"}
        )
        
        print("\n--- Superhero Query Results ---")
        for doc in results["documents"][0]:
            print(f"• {doc}")
            
        # 3. Multi-query example
        multi_results = chroma_client.query_collection(
            collection_name="sample_collection",
            query_texts=["Tell me about animals", "Tell me about movies"],
            n_results=2
        )
        
        print("\n--- Multi-Query Results ---")
        print("Animals Query:")
        for doc in multi_results["documents"][0]:
            print(f"• {doc}")
            
        print("\nMovies Query:")
        for doc in multi_results["documents"][1]:
            print(f"• {doc}")
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()