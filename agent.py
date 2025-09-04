from dotenv import load_dotenv
load_dotenv(".env.local")

import os
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, WorkerOptions, ChatContext
from livekit.plugins import noise_cancellation, google
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email 
from mem0 import AsyncMemoryClient
import json
import logging 


LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Fallback overrides (if needed)
if LIVEKIT_API_KEY:
    os.environ["LIVEKIT_API_KEY"] = LIVEKIT_API_KEY
if LIVEKIT_API_SECRET:
    os.environ["LIVEKIT_API_SECRET"] = LIVEKIT_API_SECRET


REALTIME_MODEL = "gemini-2.0-flash-live-001"

class Assistant(Agent):
    def __init__(self, chat_ctx=None) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                api_key=GOOGLE_API_KEY,
                model=REALTIME_MODEL,
                voice="charon",
                temperature=0.8,
                  
            ),
            tools=[
                get_weather,  
                search_web,    
                send_email     
            ],
            chat_ctx=chat_ctx
        )

async def entrypoint(ctx: agents.JobContext):

    async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str):
        logging.info("Shutting down, saving chat context to memory...")

        message_formatted=[
        ]

        logging.info(f"Chat context message: {chat_ctx.items}")

        for item in chat_ctx.items:
            content_str=''.join(item.content) if isinstance(item.content, list) else str(item.content)

            if memory_str and memory_str in content_str:
                continue

            if item.role in ['user', 'assistant']:
                message_formatted.append({
                    "role": item.role,
                    "content": content_str.strip()
                })
        logging.info(f"Formatted messages to add to memory: {message_formatted}")
        await mem0.add(message_formatted, user_id="Nishant")
        logging.info("Chat context save to memory.")

    session = AgentSession(

    )

    

    mem0= AsyncMemoryClient()
    user_name = 'Nishant'
    results = await mem0.get_all(user_id=user_name)
    initial_ctx = ChatContext()
    memory_str =''

    if results:
        memories = [
            {
                "memory": result["memory"],
                "updated_at": result["updated_at"]
            }
            for result in results
        ]
        memory_str = json.dumps(memories)
        logging.info(f"Memories: {memory_str}")
        initial_ctx.add_message(
            role = "assistant",
            content=f"The user's name is {user_name}, and this is relevent context about him: {memory_str}",
        )

    

    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=initial_ctx),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
            audio_enabled=True,
        ),
    )

    await ctx.connect()
    
    await session.generate_reply(instructions=SESSION_INSTRUCTION)
    ctx.add_shutdown_callback(lambda: shutdown_hook(session._agent.chat_ctx, mem0, memory_str))

if __name__ == "__main__":
    agents.cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
    )
        