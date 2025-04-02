from fastapi import APIRouter

router = APIRouter(
    prefix='/bridge/ios',
    tags=['router for ios']
)


@router.get("/ping")
def ping_android():
    return "ping ios router: success~"
