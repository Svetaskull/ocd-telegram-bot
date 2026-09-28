import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from openai import OpenAI
import os


bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

client = OpenAI()

with open("mark_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()


# Здесь будем хранить сообщения, которые написал Марк.
# Ключ — message_id сообщения Марка.
# Значение — текст поста, к которому относится комментарий.
mark_messages = {}


async def generate_mark_comment(post, extra_context=None):
    if extra_context:
        user_input = f"""
Пост канала:
{post}

Контекст диалога:
{extra_context}

Напиши короткий ответ Марка.
"""
    else:
        user_input = f"""
Пост канала:
{post}

Напиши один комментарий Марка.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=system_prompt,
        input=user_input
    )

    return response.output_text


# Новая публикация канала
@dp.message(lambda message: message.is_automatic_forward)
async def channel_post_handler(message: Message):
    post = message.text or message.caption or ""

    if not post:
        return

    try:
        comment = await generate_mark_comment(post)

        sent_message = await message.reply(comment)

        # Запоминаем сообщение Марка.
        mark_messages[sent_message.message_id] = {
            "post": post,
            "comment": comment
        }

    except Exception as e:
        print("Ошибка OpenAI:", e)


# Ответ пользователю, если он отвечает непосредственно Марку
@dp.message(lambda message: message.reply_to_message is not None)
async def reply_to_mark_handler(message: Message):
    replied_message = message.reply_to_message

    # Проверяем, действительно ли пользователь отвечает
    # на сообщение, которое написал Марк.
    if replied_message.message_id not in mark_messages:
        return

    post = mark_messages[replied_message.message_id]["post"]
    mark_comment = mark_messages[replied_message.message_id]["comment"]

    user_reply = message.text or message.caption or ""

    if not user_reply:
        return

    try:
        context = f"""
Комментарий Марка:
{mark_comment}

Ответ пользователя:
{user_reply}
"""

        answer = await generate_mark_comment(post, context)

        sent_message = await message.reply(answer)

        # Теперь этот новый ответ тоже считается сообщением Марка.
        mark_messages[sent_message.message_id] = {
            "post": post,
            "comment": answer
        }

    except Exception as e:
        print("Ошибка OpenAI:", e)


async def main():
    print("Марк запущен в Telegram.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())