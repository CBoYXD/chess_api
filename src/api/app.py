import json
import logging
from logging.config import dictConfig

import betterlogging as bl
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.api import routers

app = FastAPI(root_path="/api/v1")
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)

with open("logging.json", "r") as f:
	json_config = json.load(f)
	dictConfig(json_config)


# Add CORS middleware
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


for router in routers:
	app.include_router(router)


@app.get("/")
async def root():
	return HTMLResponse(content="Root page")


if __name__ == "__main__":
	pass
