from fastapi import FastAPI
import uvicorn
import threading

import os
import re

import hikari
import aiohttp
from hikari import Intents
bot = hikari.GatewayBot(token="MTAzNTQzNjU2Mzc2NjcwNjIwNg.Gaug-j.VWiUs-WuylVsTtExIiEIUmiAZQ8bx6KVhKsoDw", intents=Intents.ALL)

app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "봇이 실행 중입니다!"}


async def send_attachment_to_api(url: str, attachment_url: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"imageUrl": attachment_url}) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("isItAi", False)  # 응답이 True인지 확인
            return False

@bot.listen()
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:

    if not event.is_human:
        return

    api_url = "https://wasitai.com/api/images/check-is-it-ai-url"

    if event.message.attachments:
        for attachment in event.message.attachments:
            bot_message  = await event.message.respond("", attachment=attachment)

            is_robot_related = await send_attachment_to_api(api_url, attachment.url)
            if is_robot_related:
                await bot_message.add_reaction("🤖")
    else:
        await event.message.respond(event.message.content)

    await event.message.delete()

# 봇을 별도 스레드에서 실행
def run_bot():
    bot.run()

bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
