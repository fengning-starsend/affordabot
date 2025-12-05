import asyncio
import os
import json
from openai import AsyncOpenAI

async def main():
    api_key = os.environ.get("ZAI_API_KEY")
    # Using Coding Endpoint as it's the verified one for Reader
    base_url = "https://api.z.ai/api/coding/paas/v4" 
    
    print(f"Probing Chat Web Search at {base_url}...")
    
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    tools = [{
        "type": "web_search",
        "web_search": {
             "enable": True, # Boolean in JSON
             "search_result": True,
             "search_query": "news about San Jose city council"
        }
    }]
    
    # Simple message
    messages = [{"role": "user", "content": "What is the latest news from San Jose City Council?"}]
    
    print("Sending request with web_search tool...")
    try:
        # Note: 'tools' param in OpenAI SDK usually expects strict OpenAI tool format (function calling).
        # Z.ai might expect this in 'tools' or 'extra_body'.
        # The user example showed 'tools' list with 'web_search' type, which is non-standard for OpenAI SDK.
        # We pass it as a regular param, if the SDK validates it might fail.
        # If SDK fails validation, we use extra_body.
        
        response = await client.chat.completions.create(
            model="glm-4.5",
            messages=messages,
            stream=False,
            # Pass custom tools structure via extra_body to bypass SDK validation if needed
            extra_body={"tools": tools} 
        )
        
        print("✅ Response Received!")
        print(f"Content: {response.choices[0].message.content}")
        
        # Check if we got tool calls or if the model just answered using the search
        if hasattr(response, 'web_search'):
             print(f"Web Search Data: {response.web_search}")
        
        # Dump full response for inspection
        print("\nFull Dict:")
        print(response.model_dump_json(indent=2))

    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
