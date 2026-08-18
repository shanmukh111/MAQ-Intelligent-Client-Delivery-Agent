from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from agents.delivery_instructions import (
    DELIVERY_AGENT_INSTRUCTIONS,
)


def create_delivery_agent(
    middleware=None,
):
    """
    Creates the MAQ Microsoft Agent Framework agent.

    The returned Agent remains an async context manager.
    """

    agent_kwargs = {}

    if middleware:
        agent_kwargs[
            "middleware"
        ] = middleware

    return Agent(
        client=OpenAIChatClient(),
        name="MAQDeliveryAgent",
        instructions=(
            DELIVERY_AGENT_INSTRUCTIONS
        ),
        **agent_kwargs,
    )