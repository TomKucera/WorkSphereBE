from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Napiš krátký pracovní email s pozdravem."
)

print(response.output[0].content[0].text)
