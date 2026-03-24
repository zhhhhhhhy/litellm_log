# my_logging.py
import litellm
from litellm.integrations.custom_logger import CustomLogger
import json
import os

class MyCustomLogger(CustomLogger):
    # 异步回调（Proxy 默认优先使用）
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f">>>> async_log_success_event 被调用!")
        self.save_log(kwargs, response_obj)

    # 同步回调（保底使用）
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f">>>> log_success_event 被调用!")
        self.save_log(kwargs, response_obj)

    def save_log(self, kwargs, response_obj):
        try:
            log_data = {
                "model": kwargs.get("model"),
                "messages": kwargs.get("messages"),
                "response": str(response_obj)
            }
            # 使用绝对路径防止找不到文件
            file_path = os.path.join(os.getcwd(), "claude_code_logs.json")
            
            # 读取现有日志
            logs = []
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            # 添加新日志
            logs.append(log_data)
            
            # 写入标准 JSON 格式
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            print(f">>>> 日志已写入: {file_path}")
        except Exception as e:
            print(f">>>> 写入失败: {e}")
            import traceback
            traceback.print_exc()

# 这一行至关重要！config.yaml 找的就是这个变量名
my_logger = MyCustomLogger()
print(f">>>> MyCustomLogger 已初始化: {my_logger}")