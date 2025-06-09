import os
from autogen_ext.models.openai import OpenAIChatCompletionClient
API_KEY = os.getenv("OPENAI_API_KEY")
model_info = {
    "name": "deepseek-chat", # 模型名称，可随意填写
    "parameters": {
        "max_tokens": 2048,  # 每次输出最大token数
                             # deepseek官方数据：1个英文字符 ≈ 0.3 个 token。1 个中文字符 ≈ 0.6 个 token。
        "temperature": 0.4,  # 模型随机性参数，数字越大，生成的结果随机性越大，一般为0.7，
                             # 如果希望AI提供更多的想法，可以调大该数字
        "top_p": 0.9,  # 模型随机性参数，接近 1 时：模型几乎会考虑所有可能的词，只有概率极低的词才会被排除，随机性也越强；
                       # 接近 0 时：只有概率非常高的极少数词会被考虑，这会使模型的输出变得非常保守和确定
    },
    "family": "gpt-4o",  # 必填字段，model属于的类别
    "functions": [],  # 非必填字段，如果模型支持函数调用，可以在这里定义函数信息
    "vision": False,  # 必填字段，模型是否支持图像输入
    "json_output": True,  # 必填字段，模型是否支持json格式输出
    "function_calling": True  # 必填字段，模型是否支持函数调用，如果模型需要使用工具函数，该字段为true
}

model_client = OpenAIChatCompletionClient(model="deepseek-chat",
                                          base_url="https://api.deepseek.com",
                                          api_key=API_KEY,
                                          model_info=model_info)