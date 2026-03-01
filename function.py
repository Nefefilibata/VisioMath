# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from PIL import Image
import json
import base64

from torchvision import message
from tqdm import tqdm
import re
#%%
from openai import OpenAI
prompt_with_order = "Please solve a single-choice math question. The last four pictures are respectively the pictures for options A, B, C, and D. Select the correct answer from A, B, C, and D based on the question description and all relevant pictures."
prompt_with_order_cn = "请你做一道数学单项选择题。最后四张图片分别为选项A、B、C、D的图片。根据题目描述和所有相关图片从A、B、C和D中选择正确答案。"

extract_answer_client = OpenAI(api_key='sk-')

eval_model_client= OpenAI(api_key='sk-')
eval_model_name = ''
def extract_choice_answer(model_output, question_type='single_choice', answer_lenth=None):
    """
    从模型输出中提取选择题答案
    :param model_output: 模型输出字符串
    :param question_type: 题目类型，'single_choice' 或 'multi_choice'
    :param answer_lenth: 答案长度（可选）
    :return: 提取的答案字符串
    """
    if question_type == 'single_choice':
        model_answer = ['']
        temp = re.findall(r'[A-D]', model_output[::-1])
        if temp:
            model_answer.append(temp[0])

    elif question_type == 'multi_choice':
        model_answer = ['']
        answer = ''
        content = re.sub(r'\s+', '', model_output)
        answer_index = content.find('【答案】')
        if answer_index > 0:
            temp = content[answer_index:]
            for letter in re.findall(r'[A-D]', temp):
                answer += letter
        else:
            temp = content[-10:]
            for letter in re.findall(r'[A-D]', temp):
                answer += letter
        if answer:
            model_answer.append(answer)

    return model_answer[-1]


def re_order_list(imgs, mode):
    """
    调整图片顺序
    :param imgs: 图片路径列表
    :param mode: 调整模式 'BCDA', 'CDAB', 'DABC'
    :return: 调整后的图片路径列表
    """
    if mode == 'BCDA':
        # BCDA模式：将最后四个元素循环左移一位
        imgs[-4:] = imgs[-3:], imgs[-4]
    elif mode == 'CDAB':
        # CDAB模式：交换元素，确保保存原始值
        imgs[-4], imgs[-3], imgs[-2], imgs[-1] = imgs[-2], imgs[-1], imgs[-4], imgs[-3]
    elif mode == 'DABC':
        # DABC模式：将最后四个元素循环右移一位
        imgs[-4:] = imgs[-1:], imgs[-4:-1]
    return imgs


def remove_question_numbers(text):
    """
    移除题目中的编号
    :param text: 原始文本
    :return: 清理后的文本
    """
    pattern = r'\(\d+\)|\d+\.|\d+\、|\d+\,'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text.strip()


def map_letter(letter,mode):
    # 定义字母映射表
    if mode == 'BCDA':
        mapping = {
            'A': 'D', 'B': 'A', 'C': 'B', 'D': 'C'
        }
    elif mode == 'CDAB':
        mapping = {
            'A': 'C', 'B': 'D', 'C': 'A', 'D': 'B'
        }
    elif mode == 'DABC':
        mapping = {
            'A': 'B', 'B': 'C', 'C': 'D', 'D': 'A'
        }
    return mapping.get(letter, letter)

#正方形拼接图像
# 需要四张图片
def stitch_images_in_grid(image_paths, spacing=50):
    if len(image_paths) != 4:
        print("Exactly four image paths are required.")
        return None

    images = []
    for image_path in image_paths:
        try:
            img = Image.open('bench_images/' + image_path)
            images.append(img)
        except IOError:
            print(f"Error reading {image_path}")
            return None

    # 获取所有图像的最大宽度和高度
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    max_height = max(heights)

    # 计算总宽度和总高度（包括间距）
    total_width = 2 * max_width + spacing
    total_height = 2 * max_height + spacing

    # 创建一个新的空白图像用于存放拼接结果
    stitched_image = Image.new('RGB', (total_width, total_height), color=(255, 255, 255))

    # 定义每个子图像的位置
    positions = [
        (0, 0),
        (max_width + spacing, 0),
        (0, max_height + spacing),
        (max_width + spacing, max_height + spacing)
    ]

    # 将每个图像粘贴到相应位置
    for img, pos in zip(images, positions):
        w, h = img.size
        offset_x = pos[0] + (max_width - w) // 2
        offset_y = pos[1] + (max_height - h) // 2
        stitched_image.paste(img, (offset_x, offset_y))

    return stitched_image


#竖着拼接图像
def stitch_images_vertically_with_spacing(image_paths, spacing=50):
    images = []
    for image_path in image_paths:
        try:
            img = Image.open('bench_images/' + image_path)
            images.append(img)
        except IOError:
            print(f"Error reading {image_path}")
            return None

    # 获取所有图像的高度和宽度
    widths, heights = zip(*(i.size for i in images))

    # 计算最大宽度和总高度
    max_width = max(widths)
    total_height = sum(heights) + (len(images) - 1) * spacing

    # 创建一个新的空白图像用于存放拼接结果
    stitched_image = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))

    y_offset = 0
    for im in images:
        w, h = im.size
        stitched_image.paste(im, ((max_width - w) // 2, y_offset))
        y_offset += h + spacing

    return stitched_image
#水平拼接图像
def stitch_images_horizontally_with_spacing(image_paths, spacing=50):
    images = []
    for image_path in image_paths:
        try:
            img = Image.open('bench_images/'+image_path)
            images.append(img)
        except IOError:
            print(f"Error reading {image_path}")
            return None

    # 获取所有图像的高度和宽度
    widths, heights = zip(*(i.size for i in images))

    # 计算总宽度和最大高度
    total_width = sum(widths) + (len(images) - 1) * spacing
    max_height = max(heights)

    # 创建一个新的空白图像用于存放拼接结果
    stitched_image = Image.new('RGB', (total_width, max_height), color=(255, 255, 255))

    x_offset = 0
    for im in images:
        w, h = im.size
        stitched_image.paste(im, (x_offset, (max_height - h) // 2))
        x_offset += w + spacing

    return stitched_image


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_num(text):
    return len(text)


def read_json(file_path):
    with open(file_path, 'r',encoding='utf-8') as file:
        data = json.load(file)
    return data
def get_llm_answer(prompt):
    score_info = {
        'model_name': "glm-4-flash",
        'api_key': "",
        'base_url': 'https://open.bigmodel.cn/api/paas/v4/'
    }

    model_output = eval_model_client.chat(
                                message = [
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.0,
                                model = 'glm-4-flash'
                            )['choices'][0]['message']['content']
    return model_output
def label_by_llm(sample,num_workers=32):
    def process_item(i):
        prompt ='''
        你是一个帮我提取单选题答案的AI助手
        你会被提供一个答案。你的任务是找到模型的最终的选项。
        如果模型的回答没有意义，则输出 Z。
        你应该输出一个单个的大写字母，例如 A, B, C, D（如果它们是有效选项），或 Z。
        例 1:
        答案: 根据题目描述和所有相关图片，选项A是正确答案。\n\n选项A是中心对称图形，因为它的四个顶点都是对称的，而选项B、C和D的顶点不是对称的。
        输出: A
        例 2:
        答案:  \nA. 球体\nB. 圆\nC. 圆盘\nD. 圆
        输出: Z
        例 3:
        答案:{}
        输出:
        '''.format(sample[i])
        # 获取模型响应
        try:
            answer = get_llm_answer(prompt)
        except:
            answer = 'error'
        return i, answer  # 返回索引和评分结果

    # 使用ThreadPoolExecutor进行并行处理，并添加进度条
    max_workers = num_workers # 根据您的需求调整线程数量
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_item, i): i for i in range(len(sample))}
        # 使用tqdm创建进度条
        with tqdm(total=len(sample)) as pbar:
            predict_labels = [None] * len(sample)
            for future in as_completed(futures):
                index, result = future.result()
                predict_labels[index] = result
                pbar.update(1)  # 更新进度条
    return predict_labels

# from function import extract_choice_answer
def calculate_accuracy(results,data_path):
    bench_data = read_json(data_path)
    bench_data = pd.DataFrame(bench_data)
    results = dict(sorted(results.items(), key=lambda item: int(item[0])))
    # bench_data['pred'] = [extract_choice_answer(list(results.values())[i]['response']) for i in range(len(bench_data))]
    responses = [results[str(i)]['response'] for i in range(len(results))]
    bench_data['pred'] = label_by_llm(responses)
    bench_data['number'] = bench_data['images'].apply(lambda x: get_num(x))
    # import random
    # random.seed(2025)
    # bench_data['pred'] = [random.choice(['A', 'B', 'C', 'D']) for _ in range(len(bench_data))]
    # bench_data['daan']=bench_data['daan'].apply(lambda x: map_letter(x,'BCDA'))
    bench_data['flag'] = (bench_data['pred'] == bench_data['answer'])
    bench_data4 = bench_data[bench_data['number']==4]
    bench_data5 = bench_data[bench_data['number']>4]
    print(f"准确率为: {bench_data['flag'].mean()*100:.5f}%")
    print(f"准确率为: {bench_data4['flag'].mean()*100:.5f}%")
    print(f"准确率为: {bench_data5['flag'].mean()*100:.5f}%")
# calculate_accuracy(results)

def process_question(item):

    content = []
    messages = [{"role": "user", "content": ""}]
    pictures, question = item['images'], item['problem']
    pictures = ['data/images/' + path for path in pictures]
    content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}"}} for path in pictures]
    content.append({
        "type": "text",
        "text": prompt_with_order+ question,
    })
    # 执行模型预测
    messages[0]['content'] = content
    try:
        completion = eval_model_client.chat.completions.create(
              model=eval_model_name, messages=messages,temperature=0.0)
        answer = json.loads(completion.model_dump_json())
        ret = answer['choices'][0]['message']['content']
        # return 'A', question, item['answer']
    except Exception as e:
        # ret = 'refuse to answer'
        ret = 'A'
    return ret, question, item['answer']


def load_existing_results(path):
    """加载已有的结果文件"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_results(new_data, path):
    """保存或更新结果文件"""
    existing_data = load_existing_results(path)
    existing_data.update(new_data)  # 合并新旧数据
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

