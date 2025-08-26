from browser_use_sdk import BrowserUseSdk
sdk = BrowserUseSdk(api_key="your api key here")
task = """
You need to perform the following browser automation task:

1. Open https://www.geeksforgeeks.org in the browser.
2. Click on the 'Python' section in the menu.
3. Click on 'Python Practice'.
4. Search Python Practice problems in the search box
5. Click on 'Python Basic Practice'.
6. Click on 'Start Coding - Python'.

Make sure the steps are executed in order and provide a summary of what happened after each step.
"""
result = sdk.run(
    llm_model="o3", 
    task=task
)
print(result)