from openai import OpenAI
import json
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
from function import encode_image
client = OpenAI(
        timeout=2400
    )
# from zhipuai im
caption_style_cot = '''
I have multiple images and a question that I want you to answer. I need you to strictly follow the format with four specific sections: SUMMARY, CAPTION, and REASONING. 
To explain further:

In SUMMARY, briefly explain what steps you’ll take to solve the problem.

In CAPTION, describe the contents of all the images, wrapping each image description inside tags like <image1></image1>, <image2></image2>, etc., focusing only on details relevant to the question.

In REASONING, outline a step-by-step thought process you would use to solve the problem based on the images.

Here’s how the format should look:
<SUMMARY>
[Summarize how you will approach the problem and explain the steps you will take to reach the answer.]
</SUMMARY>

<CAPTION>
<image1>
[Description of Image 1, focusing on details relevant to the question.]
</image1>
<image2>
[Description of Image 2, focusing on details relevant to the question.]
</image2>
...
</CAPTION>

<REASONING>
[Provide a chain-of-thought, logical explanation of the problem. This should outline step-by-step reasoning based on all the images.]
</REASONING>
'''
solve_prompt = '''Please do a math multiple-choice question. The last four pictures are the pictures for options A, B, C, and D respectively. Based on the question description and all relevant pictures, choose the correct answer from A, B, C, and D.'''
bench_data = json.load(open(r"train_data.json", 'r', encoding='utf-8'))
train_data = bench_data

def shuffing_option_prompt(mode=0):
    abcd_derangements = [
        "BADC",
        "BCDA",
        "BDAC",
        "CADB",
        "CDAB",
        "CDBA",
        "DABC",
        "DCAB",
        "DCBA"
    ]
    item = abcd_derangements[mode]
    return f'''Please do a math multiple-choice question. The last four pictures are the pictures for options {item[0]}, {item[1]}, {item[2]}, and {item[3]} respectively. Based on the question description and all relevant pictures, choose the correct answer from A, B, C, and D.'''

def process_question(i):
    content = []
    messages = [{"role": "user", "content": ""}]
    path_text, question = train_data[i]['images'], train_data[i]['input']
    pictures = ['train_images/train_images/' + path for path in train_data[i]['images']]
    content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}"}} for path in pictures]
    content.append({
        "type": "text",
        "text": caption_style_cot+ question,
    })
    # 执行模型预测
    messages[0]['content'] = content
    try:
    # if 1:
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=messages,
        )
        answer = json.loads(completion.model_dump_json())
        ret = answer['choices'][0]['message']['content']
    except Exception as e:
         return i, 'error', question, train_data[i]['answer']
    return i, ret, question, train_data[i]['answer']
def solve_question(i,caption):
    content = []
    messages = [{"role": "user", "content": caption[str(i)]['response']+solve_prompt+'\n'+ caption[str(i)]['question']}]
    try:
    # if 1:
        completion = client.chat.completions.create(
            model="deepseek-v3.1",
            messages=messages,
            max_tokens=8012 )
        answer = json.loads(completion.model_dump_json())
        # return answer
        # ret = '<think/>'+completion.choices[0].message.reasoning_content+'<think>'+completion.choices[0].message.reasoning_content
        ret = answer['choices'][0]['message']['content']
    except Exception as e:
         return i, 'error', caption[str(i)]['question'], caption[str(i)]['answer']
    return i, ret, caption[str(i)]['question'], caption[str(i)]['answer']