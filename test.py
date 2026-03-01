from function import *

if __name__ == '__main__':
    input_path = 'VisioMath.json'
    path = 'baseline.json'
    bench_data = read_json(input_path)
    results = {}
    predict = []  # 确保初始化predict列表
    for i in tqdm(range(0,len(bench_data))):
            ret, question, answer = process_question(bench_data[i])
            # time.sleep(5)
            predict.append(ret)
            results[str(i)] = {
                'response': ret,
                'question': question,
                'answer': answer,
            }
            # 每隔100次写入一次文件
            if (i + 1) % 100 == 0:
                save_results(results,path)
    save_results(results,path)
    calculate_accuracy(results,input_path)