from fastapi import FastAPI,APIRouter,Depends,Request
import os
from helpers.config import get_settings,Settings
from controllers.NLPController import NLPController

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],


)

@base_router.get('/')
async def welcome(app_settings: Settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        'app_name':app_name,
        'app_version':app_version
    }

@base_router.get('/test')
async def test_endpoint(request: Request):
    nlp_contrller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )
    return nlp_contrller.test_method()

@base_router.get('/show list of collections')
async def show(request: Request):
    vectordb_client=request.app.vectordb_client    
    return vectordb_client.list_all_collections()

@base_router.post('/insert_one/{collection_name}')
async def insert_one_vector(request: Request,collection_name: str):
    vectordb_client=request.app.vectordb_client
    embedding_client=request.app.embedding_client
    
    vector=embedding_client.embed_text(
            text="This is a test text",
            document_type="document"
        )

    is_inserted = vectordb_client.insert_one(
        collection_name=collection_name,
        text="This is a test text",
        vector=vector,
        metadata={"source":"unit_test"},
        record_id=100
    )
    return {
        "is_inserted": is_inserted
    }

        #  def insert_one(self, collection_name: str, text: str, vector: list,
        #                  metadata: dict = None, 
        #                  record_id: str = None):