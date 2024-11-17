import os
from dotenv import load_dotenv
import openai

load_dotenv()
client = openai.OpenAI(
    api_key=os.getenv("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

def check_hydrate_formation(confidence_score):
    try:
        response = client.chat.completions.create(
            model='Meta-Llama-3.1-8B-Instruct',
            messages=[
                {"role": "system", "content": "You are a hydrate prediction system. Respond in 5-7 words only."},
                {"role": "user", "content": f"Hydrate formation status with confidence {confidence_score:.2f}"}
            ],
            temperature=0.1,
            top_p=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Hydrate formation predicted (Confidence: {confidence_score:.2f})"