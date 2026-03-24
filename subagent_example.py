import requests
import json

# Subagent 示例
class SubAgent:
    def __init__(self, name, model="claude-3-5-sonnet"):
        self.name = name
        self.model = model
    
    def run(self, task):
        """运行 subagent 执行任务"""
        print(f"\n=== {self.name} 开始执行任务 ===")
        print(f"任务: {task}")
        
        # 通过 litellm proxy 发送请求
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            headers={
                "Authorization": "Bearer sk-1234",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": f"你是 {self.name}，一个专业的 AI 助手。"},
                    {"role": "user", "content": task}
                ],
                "max_tokens": 100
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"结果: {content}")
            return content
        else:
            print(f"错误: {response.status_code}")
            return None

# 示例使用
if __name__ == "__main__":
    # 创建不同的 subagent
    research_agent = SubAgent("研究助手")
    coding_agent = SubAgent("编程助手")
    math_agent = SubAgent("数学助手")
    
    # 运行任务
    research_agent.run("请简要介绍量子计算的基本原理")
    coding_agent.run("写一个 Python 函数来计算斐波那契数列")
    math_agent.run("解方程：2x + 5 = 17")
    
    print("\n=== 所有任务完成 ===")
