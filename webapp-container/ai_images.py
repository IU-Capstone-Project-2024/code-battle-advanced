import replicate
from dotenv import load_dotenv
import requests


def process_text(text, filename):
    load_dotenv()

    input = {
        "prompt": text
    }

    output = replicate.run(
        "bytedance/sdxl-lightning-4step:5f24084160c9089501c1b3545d9be3c27883ae2239b6f412990e82d4a6210f8f",
        input=input
    )
    print(output[0])
    response = requests.get(output[0])
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed opening image: {response.status_code}")


if __name__ == '__main__':
    process_text(input('text:'), 'test.png')
