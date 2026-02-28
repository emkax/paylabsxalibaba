import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()



try:
    client = OpenAI(
        # API keys for the Singapore, US (Virginia), and China (Beijing) regions are not interchangeable. Get API Key: https://www.alibabacloud.com/help/model-studio/get-api-key
        # If the environment variable is not configured, replace the following line with: api_key="sk-xxx", using your Model Studio API key.
        api_key = os.getenv("DASHSCOPE_API_KEY"),
        # Note: The base_url is different for each region. The example below uses the base_url for the Singapore region.
        # - Singapore: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
        # - US (Virginia): https://dashscope-us.aliyuncs.com/compatible-mode/v1
        # - China (Beijing): https://dashscope.aliyuncs.com/compatible-mode/v1
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen-plus",  
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Who are you?'}
            ]
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Error message: {e}")
    print("For more information, see the documentation: https://www.alibabacloud.com/help/model-studio/developer-reference/error-code")