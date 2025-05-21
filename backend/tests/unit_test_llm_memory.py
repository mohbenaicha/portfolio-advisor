import asyncio
from datetime import date, timedelta
from app.db.memory import (
    add_user_memory,
    get_user_memory,
    get_latest_user_memory
)
from app.db.session import get_db

async def test_llm_memory_evolution():
    user_id = 1
    today = date.today()

    async for db in get_db():
        await add_user_memory(
            user_id=user_id,
            date=today - timedelta(days=3),
            short_term="Explore high-growth AI stocks",
            long_term="Build foundation in next-gen tech sectors"
        )

        await add_user_memory(
            user_id=user_id,
            date=today - timedelta(days=2),
            short_term="Evaluate defensive dividend plays",
            long_term="Preserve capital while earning steady returns"
        )

        await add_user_memory(
            user_id=user_id,
            date=today - timedelta(days=1),
            short_term="Reassess global energy market exposure",
            long_term="Pivot toward sustainable infrastructure assets"
        )

        memories = await get_user_memory(user_id)
        print(f" Memory Evolution for User {user_id}:\n")

        for mem in sorted(memories, key=lambda x: x.date):
            print(f" {mem.date}")
            print(f"    Short-term: {mem.short_term_goal}")
            print(f"    Long-term: {mem.long_term_goal}\n")


async def test_multi_user_memory_isolation():
    user1 = 1
    user2 = 2
    today = date.today()

    async for db in get_db():
        await add_user_memory(
            user_id=user1,
            date=today - timedelta(days=2),
            short_term="User 1 short-term: AI stocks",
            long_term="User 1 long-term: Next-gen tech"
        )

        await add_user_memory(
            user_id=user2,
            date=today - timedelta(days=1),
            short_term="User 2 short-term: bond yield analysis",
            long_term="User 2 long-term: preserve capital"
        )

        user1_memories = await get_user_memory(user1)
        print(f"User 1 has {len(user1_memories)} memory entry:")
        for m in user1_memories:
            print(f"    {m.short_term_goal} |  {m.long_term_goal}")

        user2_memories = await get_user_memory(user2)
        print(f"User 2 has {len(user2_memories)} memory entry:")
        for m in user2_memories:
            print(f"    {m.short_term_goal} |  {m.long_term_goal}")

        #  Test: user1 should not see user2 memory
        for m in user1_memories:
            assert "User 2" not in m.short_term_goal
            assert "User 2" not in m.long_term_goal

        for m in user2_memories:
            assert "User 1" not in m.short_term_goal
            assert "User 1" not in m.long_term_goal

        print("\n Memory isolation confirmed: No crossover between user memories.")

async def get_last_user_memory(user_id):
    async for db in get_db():
        memory = await get_latest_user_memory(user_id, portfolio_id=3)
        if memory:
            print(f"Latest memory for user {user_id}:")
            print(f"  Short-term: {memory.short_term_goal}")
            print(f"  Long-term: {memory.long_term_goal}")
        else:
            print(f"No memory found for user {user_id}")