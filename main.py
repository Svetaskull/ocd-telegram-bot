from openai import OpenAI

client = OpenAI()

post = input("Вставь текст поста: ")

with open("mark_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

try:
    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=system_prompt,
        input=f"Пост канала:\n{post}\n\nНапиши один комментарий Марка."
    )

    print("\nКомментарий Марка:")
    print(response.output_text)

except Exception as e:
    print("\nОШИБКА API:")
    print(type(e).__name__)
    print(e)