from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import APIRouter
import time

REGISTRY = CollectorRegistry(auto_describe=True)
REQUEST_COUNT = Counter("voicelegacy_requests_total","Total HTTP requests",["method","path","status"],registry=REGISTRY)
REQUEST_TIME = Histogram("voicelegacy_request_seconds","Latency",["method","path"],registry=REGISTRY)
ACTIVE_WS = Gauge("voicelegacy_active_ws","Active WebSockets",registry=REGISTRY)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        method=request.method; path=request.url.path; start=time.perf_counter(); status="500"
        try:
            resp = await call_next(request); status=str(resp.status_code); return resp
        finally:
            REQUEST_TIME.labels(method, path).observe(time.perf_counter()-start)
            REQUEST_COUNT.labels(method, path, status).inc()

metrics_router = APIRouter()
@metrics_router.get("/metrics")
async def metrics(): return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

from contextlib import asynccontextmanager
@asynccontextmanager
async def track_ws():
    ACTIVE_WS.inc()
    try: yield
    finally: ACTIVE_WS.dec()
