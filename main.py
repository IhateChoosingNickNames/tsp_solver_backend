import asyncio
import sys

import aio_pika
from fastapi import FastAPI

from adapters.ampq import AmqpEngine
from api.task import task_router
from services.consumer_service import ConsumerService
from settings import get_settings, AppSettings, RabbitMqSettings


async def create_queue() -> None:
    broker = get_settings(RabbitMqSettings)
    await AmqpEngine.create_queue(str(broker.url), broker.result_queue)


def create_app() -> FastAPI:
    app = FastAPI(debug=get_settings(AppSettings).debug)
    app.include_router(task_router)
    asyncio.create_task(create_queue())
    return app


async def start_consuming():
    amqp_url = str(get_settings(RabbitMqSettings).url)
    connection = await aio_pika.connect_robust(amqp_url)

    queue_name = get_settings(RabbitMqSettings).result_queue

    async with connection:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await ConsumerService().proceed_message(message.body)

                    if queue.name in message.body.decode():
                        break


if len(sys.argv) > 1 and sys.argv[1] == "consumer":
    asyncio.run(start_consuming())
else:
    app = create_app()
