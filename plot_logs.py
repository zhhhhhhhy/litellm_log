import json
import matplotlib.pyplot as plt
import pandas as pd
import re
from datetime import datetime

# 读取日志文件
def read_logs(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 解析日志数据
def parse_logs(logs):
    data = []
    for log in logs:
        # 提取模型信息
        model = log.get('model', 'unknown')
        
        # 提取消息内容
        messages = log.get('messages', [])
        user_message = ''
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content')
                if isinstance(content, str):
                    user_message = content
                elif isinstance(content, list):
                    # 处理多部分内容
                    parts = []
                    for part in content:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            parts.append(part.get('text', ''))
                    user_message = ' '.join(parts)
        
        # 提取响应内容
        response = log.get('response', '')
        
        # 提取 token 使用情况
        completion_tokens = 0
        prompt_tokens = 0
        total_tokens = 0
        
        # 从响应字符串中提取 token 信息
        token_match = re.search(r'completion_tokens=(\d+)', response)
        if token_match:
            completion_tokens = int(token_match.group(1))
        
        token_match = re.search(r'prompt_tokens=(\d+)', response)
        if token_match:
            prompt_tokens = int(token_match.group(1))
        
        token_match = re.search(r'total_tokens=(\d+)', response)
        if token_match:
            total_tokens = int(token_match.group(1))
        
        # 提取时间戳
        timestamp = None
        time_match = re.search(r'created=(\d+)', response)
        if time_match:
            try:
                timestamp = datetime.fromtimestamp(int(time_match.group(1)))
            except:
                pass
        
        data.append({
            'model': model,
            'user_message': user_message,
            'response': response,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'timestamp': timestamp
        })
    return data

# 生成流程图
def generate_flowchart(data):
    """生成主 Agent 分配任务给 Subagent 的流程图"""
    import matplotlib.pyplot as plt
    import numpy as np
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    # 根据数据量调整图表大小
    num_tasks = len(data)
    fig_height = max(8, 6 + num_tasks * 1.5)
    plt.figure(figsize=(16, fig_height))
    
    # 绘制主流程
    # 1. 用户节点
    plt.text(0.1, 0.9, '用户', ha='center', va='center', 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', edgecolor='blue', alpha=0.8))
    
    # 2. 主 Agent 节点
    plt.text(0.3, 0.9, '主 Agent\n(任务分配)', ha='center', va='center', 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='orange', alpha=0.8))
    
    # 3. 绘制每个 Subagent 任务
    y_base = 0.7
    y_step = 0.6 / max(1, num_tasks)
    
    for i, item in enumerate(data):
        y = y_base - i * y_step
        
        # 任务描述
        task_text = item['user_message'][:60] + ('...' if len(item['user_message']) > 60 else '')
        
        # Subagent 节点
        plt.text(0.5, y, f'Subagent\n任务: {task_text}', ha='center', va='center', 
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', edgecolor='green', alpha=0.8))
        
        # 响应节点（只显示部分内容）
        response_text = item['response'][:40] + ('...' if len(item['response']) > 40 else '')
        plt.text(0.7, y, f'响应\n{response_text}', ha='center', va='center', 
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightcyan', edgecolor='cyan', alpha=0.8))
        
        # 结果返回节点
        plt.text(0.9, y, '结果\n返回用户', ha='center', va='center', 
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lightpink', edgecolor='red', alpha=0.8))
    
    # 绘制连接线
    # 用户到主 Agent
    plt.arrow(0.15, 0.9, 0.1, 0, head_width=0.02, head_length=0.02, fc='black', ec='black')
    
    # 主 Agent 到每个 Subagent
    for i in range(num_tasks):
        y = y_base - i * y_step
        plt.arrow(0.35, 0.9, 0.1, -(0.9 - y), head_width=0.02, head_length=0.02, fc='black', ec='black')
        
        # Subagent 到响应
        plt.arrow(0.55, y, 0.1, 0, head_width=0.02, head_length=0.02, fc='black', ec='black')
        
        # 响应到结果返回
        plt.arrow(0.75, y, 0.1, 0, head_width=0.02, head_length=0.02, fc='black', ec='black')
    
    # 结果返回节点连接到用户
    if num_tasks > 0:
        for i in range(num_tasks):
            y = y_base - i * y_step
            plt.arrow(0.9, y, 0, -(y - 0.1), head_width=0.02, head_length=0.02, fc='black', ec='black')
        
        # 汇总到用户
        plt.arrow(0.9, 0.1, -0.8, 0, head_width=0.02, head_length=0.02, fc='black', ec='black')
        plt.text(0.5, 0.05, '最终结果汇总', ha='center', va='center', fontsize=10)
    
    plt.axis('off')
    plt.title('主 Agent 分配任务给 Subagent 的流程图', fontsize=16)
    plt.tight_layout()
    plt.savefig('flowchart.png', dpi=150, bbox_inches='tight')
    print('流程图已保存: flowchart.png')

# 生成图表
def generate_plots(data):
    df = pd.DataFrame(data)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    # 1. Token 使用情况柱状图
    plt.figure(figsize=(10, 6))
    if not df.empty:
        plt.bar(df.index, df['total_tokens'], label='总 Tokens')
        plt.bar(df.index, df['prompt_tokens'], label='提示 Tokens')
        plt.xlabel('请求序号')
        plt.ylabel('Tokens')
        plt.title('各请求的 Token 使用情况')
        plt.legend()
        plt.tight_layout()
        plt.savefig('token_usage.png')
        print('Token 使用情况图表已保存: token_usage.png')
    
    # 2. 模型分布饼图
    plt.figure(figsize=(8, 8))
    if not df.empty:
        model_counts = df['model'].value_counts()
        plt.pie(model_counts.values, labels=model_counts.index, autopct='%1.1f%%')
        plt.title('模型使用分布')
        plt.tight_layout()
        plt.savefig('model_distribution.png')
        print('模型分布图表已保存: model_distribution.png')
    
    # 3. 消息长度分析
    plt.figure(figsize=(10, 6))
    if not df.empty:
        message_lengths = df['user_message'].apply(len)
        plt.bar(df.index, message_lengths)
        plt.xlabel('请求序号')
        plt.ylabel('消息长度')
        plt.title('用户消息长度分析')
        plt.tight_layout()
        plt.savefig('message_lengths.png')
        print('消息长度分析图表已保存: message_lengths.png')
    
    # 4. 对话交互分析（问答关系）
    plt.figure(figsize=(12, 8))
    if not df.empty:
        # 为每个对话创建一条线
        for i, row in df.iterrows():
            # 用户消息长度
            user_len = len(row['user_message'])
            # 响应长度（近似）
            response_len = len(row['response'])
            
            # 绘制用户消息（蓝色）
            plt.bar(i - 0.2, user_len, width=0.4, color='blue', label='用户消息' if i == 0 else "")
            # 绘制响应（绿色）
            plt.bar(i + 0.2, response_len, width=0.4, color='green', label='Subagent 响应' if i == 0 else "")
        
        plt.xlabel('对话序号')
        plt.ylabel('消息长度')
        plt.title('Subagent 与用户的问答交互分析')
        plt.xticks(df.index, [f'对话 {i+1}' for i in df.index])
        plt.legend()
        plt.tight_layout()
        plt.savefig('conversation_analysis.png')
        print('对话交互分析图表已保存: conversation_analysis.png')
    
    # 5. 流程图
    if not df.empty:
        generate_flowchart(data)
    
    # 6. 对话内容摘要
    if not df.empty:
        with open('conversation_summary.txt', 'w', encoding='utf-8') as f:
            f.write('=== Subagent 与用户的问答摘要 ===\n\n')
            for i, row in df.iterrows():
                f.write(f'对话 {i+1}:\n')
                f.write(f'用户: {row["user_message"][:100]}...\n')
                f.write(f'Subagent: {row["response"][:150]}...\n')
                f.write('\n' + '='*50 + '\n\n')
        print('对话内容摘要已保存: conversation_summary.txt')

# 主函数
def main():
    try:
        logs = read_logs('claude_code_logs.json')
        print(f'成功读取 {len(logs)} 条日志')
        
        parsed_data = parse_logs(logs)
        print('日志解析完成')
        
        generate_plots(parsed_data)
        print('图表生成完成')
        
    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    main()
