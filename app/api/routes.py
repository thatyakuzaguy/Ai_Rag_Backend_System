from fastapi import APIRouter, Depends, File, Header, HTTPException, Query, UploadFile, status

from app.core.dependencies import get_app_store, get_rag_service, get_vector_store
from app.models.schemas import (
    AuthResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CollectionChatRequest,
    CollectionChatResponse,
    CollectionCreateRequest,
    CollectionDocumentRequest,
    CollectionResponse,
    DashboardMetrics,
    DeleteResponse,
    DocumentRecordResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    LoginRequest,
    RegisterRequest,
    SearchResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
    UserResponse,
)
from app.services.rag import RAGService
from app.services.app_store import AppStore
from app.services.vector_store import SQLiteVectorStore
from app.web import home_page

router = APIRouter()


def provider_error(error: Exception) -> HTTPException:
    message = str(error)
    if "api_key" in message.lower() or "authentication" in message.lower():
        message = "AI provider authentication failed. Check OPENAI_API_KEY in environment variables."
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"AI provider request failed: {message}",
    )


def current_user(
    authorization: str = Header(default=""),
    app_store: AppStore = Depends(get_app_store),
) -> dict:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    user = app_store.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    return user


def public_user_with_token(auth_result: dict) -> AuthResponse:
    token = auth_result.pop("token")
    return AuthResponse(token=token, user=UserResponse(**auth_result))


@router.get("/", include_in_schema=False)
def home():
    return home_page()


@router.get("/health", response_model=HealthResponse)
def health(store: SQLiteVectorStore = Depends(get_vector_store)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        documents=store.count_sources(),
        chunks_indexed=store.count(),
    )


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, app_store: AppStore = Depends(get_app_store)) -> AuthResponse:
    if app_store.get_user_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    app_store.create_user(payload.email, payload.password, payload.display_name)
    auth_result = app_store.authenticate(payload.email, payload.password)
    if auth_result is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")
    return public_user_with_token(auth_result)


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest, app_store: AppStore = Depends(get_app_store)) -> AuthResponse:
    auth_result = app_store.authenticate(payload.email, payload.password)
    if auth_result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return public_user_with_token(auth_result)


@router.get("/me", response_model=UserResponse)
def me(user: dict = Depends(current_user)) -> UserResponse:
    return UserResponse(**user)


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
) -> DashboardMetrics:
    return DashboardMetrics(**app_store.dashboard_metrics(user["id"]))


@router.post(
    "/collections",
    response_model=CollectionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_collection(
    payload: CollectionCreateRequest,
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
) -> CollectionResponse:
    collection = app_store.create_collection(user["id"], payload.name, payload.description)
    return CollectionResponse(**collection)


@router.get("/collections", response_model=list[CollectionResponse])
def list_collections(
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
) -> list[CollectionResponse]:
    return [CollectionResponse(**collection) for collection in app_store.list_collections(user["id"])]


@router.post(
    "/collections/{collection_id}/documents",
    response_model=DocumentRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_collection_document(
    collection_id: str,
    payload: CollectionDocumentRequest,
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
    rag: RAGService = Depends(get_rag_service),
) -> DocumentRecordResponse:
    try:
        app_store.get_collection(user["id"], collection_id)
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found") from error

    source = f"{user['id']}:{collection_id}:{payload.source}"
    try:
        chunks = rag.ingest_text(
            payload.text,
            source=source,
            metadata={
                "user_id": user["id"],
                "collection_id": collection_id,
                "source_name": payload.source,
            },
        )
    except Exception as error:
        raise provider_error(error) from error

    document = app_store.create_document(user["id"], collection_id, payload.source, chunks)
    return DocumentRecordResponse(**document)


@router.get("/collections/{collection_id}/documents", response_model=list[DocumentRecordResponse])
def list_collection_documents(
    collection_id: str,
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
) -> list[DocumentRecordResponse]:
    try:
        app_store.get_collection(user["id"], collection_id)
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found") from error
    return [
        DocumentRecordResponse(**document)
        for document in app_store.list_documents(user["id"], collection_id)
    ]


@router.post(
    "/collections/{collection_id}/chat",
    response_model=CollectionChatResponse,
)
def chat_with_collection(
    collection_id: str,
    payload: CollectionChatRequest,
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
    rag: RAGService = Depends(get_rag_service),
) -> CollectionChatResponse:
    try:
        app_store.get_collection(user["id"], collection_id)
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found") from error

    if payload.session_id:
        session = app_store.get_chat_session(user["id"], payload.session_id)
    else:
        session = app_store.create_chat_session(user["id"], collection_id, payload.question[:60])

    previous_messages = app_store.list_chat_messages(session["id"], limit=10)
    history = [
        ChatMessage(role=message["role"], content=message["content"])
        for message in previous_messages
    ]
    app_store.add_chat_message(session["id"], "user", payload.question)

    try:
        response = rag.answer(
            question=payload.question,
            top_k=payload.top_k,
            history=history,
            metadata_filter={"user_id": user["id"], "collection_id": collection_id},
        )
    except Exception as error:
        raise provider_error(error) from error

    app_store.add_chat_message(session["id"], "assistant", response.answer)
    return CollectionChatResponse(
        session_id=session["id"],
        question=response.question,
        answer=response.answer,
        citations=response.citations,
        context=response.context,
    )


@router.post(
    "/collections/{collection_id}/chats",
    response_model=ChatSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chat_session(
    collection_id: str,
    payload: ChatSessionCreateRequest,
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
) -> ChatSessionResponse:
    try:
        app_store.get_collection(user["id"], collection_id)
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found") from error
    return ChatSessionResponse(**app_store.create_chat_session(user["id"], collection_id, payload.title))


@router.get("/collections/{collection_id}/chats", response_model=list[ChatSessionResponse])
def list_collection_chats(
    collection_id: str,
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
) -> list[ChatSessionResponse]:
    try:
        app_store.get_collection(user["id"], collection_id)
    except KeyError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found") from error
    return [
        ChatSessionResponse(**session)
        for session in app_store.list_chat_sessions(user["id"], collection_id)
    ]


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    payload: FeedbackRequest,
    user: dict = Depends(current_user),
    app_store: AppStore = Depends(get_app_store),
) -> FeedbackResponse:
    if payload.rating == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be -1 or 1")
    feedback = app_store.save_feedback(user["id"], payload.session_id, payload.rating, payload.comment)
    return FeedbackResponse(**feedback)


@router.post(
    "/documents",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_document(
    payload: DocumentIngestRequest,
    rag: RAGService = Depends(get_rag_service),
) -> DocumentIngestResponse:
    try:
        chunks = rag.ingest_text(payload.text, source=payload.source, metadata=payload.metadata)
    except Exception as error:
        raise provider_error(error) from error
    return DocumentIngestResponse(source=payload.source, chunks_indexed=chunks)


@router.post(
    "/documents/file",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_file(
    file: UploadFile = File(...),
    rag: RAGService = Depends(get_rag_service),
) -> DocumentIngestResponse:
    allowed_extensions = {".txt", ".md", ".csv"}
    filename = file.filename or "uploaded-file"
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .txt, .md, and .csv uploads are supported.",
        )

    raw = await file.read()
    text = raw.decode("utf-8", errors="replace")
    try:
        chunks = rag.ingest_text(text, source=filename, metadata={"filename": filename})
    except Exception as error:
        raise provider_error(error) from error
    return DocumentIngestResponse(source=filename, chunks_indexed=chunks)


@router.get("/search", response_model=SearchResponse)
def search(
    query: str = Query(..., min_length=2),
    top_k: int = Query(4, ge=1, le=20),
    rag: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    try:
        results = rag.search(query=query, top_k=top_k)
    except Exception as error:
        raise provider_error(error) from error
    return SearchResponse(query=query, results=results)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, rag: RAGService = Depends(get_rag_service)) -> ChatResponse:
    try:
        return rag.answer(question=payload.question, top_k=payload.top_k, history=payload.history)
    except Exception as error:
        raise provider_error(error) from error


@router.delete("/documents/{source}", response_model=DeleteResponse)
def delete_source(
    source: str,
    store: SQLiteVectorStore = Depends(get_vector_store),
) -> DeleteResponse:
    deleted = store.delete_by_source(source)
    return DeleteResponse(source=source, chunks_deleted=deleted)
