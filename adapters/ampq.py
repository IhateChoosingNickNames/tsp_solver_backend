import asyncio

import aio_pika
from aio_pika import ExchangeType


class AmqpEngine:

    @staticmethod
    async def publish(
        amqp_url: str,
        queue: str,
        message: str,
        **kwargs,
    ) -> None:
        connection = await aio_pika.connect_robust(amqp_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                queue,
                ExchangeType.DIRECT,
                durable=True,
            )
            await exchange.publish(
                aio_pika.Message(body=message.encode(), **kwargs),
                routing_key=queue,
            )

    @staticmethod
    async def create_queue(amqp_url: str, queue_name: str) -> None:
        connection = await aio_pika.connect_robust(amqp_url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            await channel.declare_exchange(
                name=queue_name,
                type=ExchangeType.DIRECT,
                durable=True,
            )
            await queue.bind(exchange=queue_name, routing_key=queue_name)
