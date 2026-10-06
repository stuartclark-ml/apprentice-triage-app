import asyncio

from langchain_core.messages import HumanMessage

from apprenticeship_navigator.agents.graph import build_graph


async def main() -> None:
    graph = build_graph()
    question = HumanMessage(content="Find apprenticeships within 10 miles of SW1A 1AA.")
    result = await graph.ainvoke({"messages": [question]})

    print(f"Messages in final state: {len(result['messages'])}")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
