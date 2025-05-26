# app/socket.py
import os
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
)

# Mount to an ASGI app (FastAPI)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# your existing FastAPI routers/imports
from app.main import router  # if you have a router
app.include_router(router)

# mount socket.io
asgi_app = socketio.ASGIApp(sio, other_asgi_app=app)

@sio.event
async def connect(sid, environ):
    print("Socket connected:", sid)

@sio.event
async def disconnect(sid):
    print("Socket disconnected:", sid)

# Example — broadcast new problem to all clients:
async def broadcast_problem(problem_data):
    await sio.emit("new_problem", problem_data)
