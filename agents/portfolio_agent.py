from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from agents.portfolio_instructions import (
    PORTFOLIO_AGENT_INSTRUCTIONS,
)


def create_portfolio_agent(
    middleware=None,
):
    """
    Creates the MAQ Portfolio Evidence Agent.
    """

    agent_kwargs = {}

    if middleware:
        agent_kwargs["middleware"] = middleware

    return Agent(
        client=OpenAIChatClient(),
        name="MAQPortfolioEvidenceAgent",
        instructions=PORTFOLIO_AGENT_INSTRUCTIONS,
        **agent_kwargs,
    )