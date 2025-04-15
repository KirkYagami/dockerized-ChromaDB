import chromadb
from chromadb.config import Settings
import argparse
import json
from typing import List, Dict, Any, Optional
import sys


def connect_to_chroma(host: str = "localhost", port: int = 8000) -> chromadb.HttpClient:
    """Connect to ChromaDB running in Docker"""
    print(f"Connecting to ChromaDB at http://{host}:{port}")
    
    try:
        client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(anonymized_telemetry=False)
        )
        client.heartbeat()
        print("Successfully connected to ChromaDB")
        return client
    except Exception as e:
        print(f"Failed to connect to ChromaDB: {str(e)}")
        sys.exit(1)


def list_collections(client: chromadb.HttpClient) -> List[str]:
    """List all collections in ChromaDB"""
    collections = client.list_collections()
    if not collections:
        print("No collections found in ChromaDB")
        return []
    
    print(f"Found {len(collections)} collections:")
    collection_names = []
    for idx, collection in enumerate(collections, 1):
        name = collection.name
        collection_names.append(name)
        print(f"  {idx}. {name}")
    
    return collection_names


def get_collection_info(client: chromadb.HttpClient, collection_name: str) -> Dict[str, Any]:
    """Get information about a specific collection"""
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        print(f"Collection: {collection_name}")
        print(f"Number of documents: {count}")
        
        if count > 0:
            sample = collection.peek(limit=3)
            print(f"Sample documents:")
            for idx, (doc_id, doc, metadata) in enumerate(zip(sample['ids'], sample['documents'], sample['metadatas']), 1):
                print(f"  {idx}. ID: {doc_id}")
                print(f"     Content: {doc[:100]}{'...' if len(doc) > 100 else ''}")
                print(f"     Metadata: {metadata}")
        
        return {
            "name": collection_name,
            "count": count
        }
    except Exception as e:
        print(f"Error getting collection info: {str(e)}")
        return {}


def run_basic_query(client: chromadb.HttpClient, collection_name: str, query_text: str, n_results: int = 3) -> None:
    """Run a basic query against a collection"""
    try:
        collection = client.get_collection(name=collection_name)
        results = collection.query(
            query_texts=query_text,
            n_results=n_results
        )
        
        print(f"\nQuery: '{query_text}'")
        print(f"Top {n_results} results:")
        
        for idx, (doc, metadata, distance) in enumerate(
            zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1
        ):
            print(f"\n{idx}. Document (similarity: {1-distance:.4f}):")
            print(f"   {doc}")
            print(f"   Metadata: {metadata}")
        
        return results
    except Exception as e:
        print(f"Error running query: {str(e)}")
        return None


def run_filtered_query(
    client: chromadb.HttpClient, 
    collection_name: str, 
    query_text: str, 
    filter_key: str,
    filter_value: str,
    n_results: int = 3
) -> None:
    """Run a filtered query against a collection"""
    try:
        collection = client.get_collection(name=collection_name)
        where_filter = {filter_key: filter_value}
        
        results = collection.query(
            query_texts=query_text,
            n_results=n_results,
            where=where_filter
        )
        
        print(f"\nFiltered Query: '{query_text}' where {filter_key}='{filter_value}'")
        print(f"Top {n_results} results:")
        
        if not results['documents'][0]:
            print("No matching documents found")
            return
            
        for idx, (doc, metadata, distance) in enumerate(
            zip(results['documents'][0], results['metadatas'][0], results['distances'][0]), 1
        ):
            print(f"\n{idx}. Document (similarity: {1-distance:.4f}):")
            print(f"   {doc}")
            print(f"   Metadata: {metadata}")
        
        return results
    except Exception as e:
        print(f"Error running filtered query: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(description="ChromaDB Client")
    parser.add_argument("--host", default="localhost", help="ChromaDB host")
    parser.add_argument("--port", default=8000, type=int, help="ChromaDB port")
    parser.add_argument("--collection", default="sample_collection", help="Collection name to query")
    parser.add_argument("--query", default="space", help="Query text")
    args = parser.parse_args()
    
    client = connect_to_chroma(host=args.host, port=args.port)
    
    collections = list_collections(client)
    
    if not collections:
        print("No collections found. Has the database been initialized with data?")
        sys.exit(1)
    
    collection_name = args.collection if args.collection in collections else collections[0]
    
    collection_info = get_collection_info(client, collection_name)
    
    if not collection_info:
        print(f"Could not access collection '{collection_name}'")
        sys.exit(1)
    

    run_basic_query(client, collection_name, args.query)
    
    # Run filtered queries for different categories
    # categories = ["Space", "Movies", "History", "Animals", "Superheroes"]
    # for category in categories:
    #     run_filtered_query(client, collection_name, args.query, "source", category, n_results=1)


if __name__ == "__main__":
    main()