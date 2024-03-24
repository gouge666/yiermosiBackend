import csv
import os
from io import StringIO, BytesIO
import numpy as np
import pandas as pd
import pickle
from flask import Flask, request, send_file, make_response, Response, stream_with_context

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


#	测试数据
data = [
    ['ID', 'y_pred'],
    ['1', '0.5'],
    ['2', '0.88']
]


@app.route('/upload', methods=['POST'])
def upload_file():
    filename = './models/test_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    # 处理上传文件
    thresholdAndExtension = next(iter(request.files.keys()))

    threshold = thresholdAndExtension.split(".")[0]
    extension = thresholdAndExtension.split(".")[1]
    file = request.files[thresholdAndExtension]
    # 获取数据

    def readCsv(file):
        df = pd.read_csv(file, header=0, encoding='utf-8')
        return df.values[:, :80]  # 获取前80列数据
    def readXlsx(file):
        df = pd.read_excel(file, header=0)
        return df.values[:, :80]  # 获取前80列数据

    X = readCsv(file) if extension == 'csv' else readXlsx(file)
    print(threshold, file, extension,X)

    # 计算结果
    y_pred_prob = loaded_model.predict_proba(X)[:, 1]
    ids = list(range(1, len(y_pred_prob) + 1))
    ids = list(map(int, ids))
    dataa = {'ID': ids, 'y_pred': y_pred_prob}
    df = pd.DataFrame(dataa)
    # Convert DataFrame to a list of lists
    result = [['ID', 'y_pred']]
    for index, row in df.iterrows():
        result.append([int(row['ID']), str(row['y_pred'])])

    print(result)
    def generate(result):
        #	用 StringIO 在内存中写，不会生成实际文件
        io = StringIO()  # 在 io 中写 csv
        w = csv.writer(io)
        for i in result:  # 对于 data 中的每一条
            w.writerow(i)  # 传入的是一个数组 ['xxx','xxx@xxx.xxx'] csv.writer 会把它处理成逗号分隔的一行
            # 需要注意的是传入仅一个字符串 '' 时，会被逐字符分割，所以要写成 ['xxx'] 的形式
            yield io.getvalue()  # 返回写入的值
            io.seek(0)  # io流的指针回到起点
            io.truncate(0)  # 删去指针之后的部分，即清空所有写入的内容，准备下一行的写入
        #	用 generate() 构造返回值

    response = Response(stream_with_context(generate(result)), mimetype='text/csv')
    #	设置Headers: Content-Disposition: attachment 表示默认会直接下载。 指定 filename。
    response.headers.set("Content-Disposition", "attachment", filename="output.csv")
    #	将 response 返回
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5888)
