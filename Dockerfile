FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 5888

CMD ["python","main.py"]