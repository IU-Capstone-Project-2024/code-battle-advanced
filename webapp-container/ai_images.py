from replicate.client import Client
from dotenv import load_dotenv
import requests
import sys


def process_text(text, filename='test.png', filemode=True):
    load_dotenv()

    inp = {
        "prompt": text
    }
    
    replicate = Client(api_token="r8_CqKFF1UxqOLDFQlOTk3ibfnWYpCLR1Q4J2wo0")
    
    output = replicate.run(
        "bytedance/sdxl-lightning-4step:5f24084160c9089501c1b3545d9be3c27883ae2239b6f412990e82d4a6210f8f",
        input=inp
    )
    if filemode: print(output[0])
    
    response = requests.get(output[0])
    
    if response.status_code == 200:
        if filemode:
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            return response.content
    else:
        if filemode: print(f"Failed opening image: {response.status_code}")
        else: raise RuntimeError("Image could not be generated")


if __name__ == '__main__':
    print('text:')
    process_text(sys.stdin.read(), "test.png")
