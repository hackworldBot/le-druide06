import asyncio
import uvicorn
from main import main as bot_main

async def run():
    asyncio.create_task(bot_main())

    config = uvicorn.Config(
        "web:app",
        host="0.0.0.0",
        port=10000,
        log_level="info"
    )

    server = uvicorn.Server(config)
    await server.serve()

asyncio.run(run())
