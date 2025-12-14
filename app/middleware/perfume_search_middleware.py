
import os
import json
import logging
from fastapi import Request, Response

class PerfumeSearchMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith("/api/perfume-search"):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        
        # Pass the request to the new router
        await self.app(scope, receive, send)
