import os
import threading
import webbrowser
import json
import time
from flask import Flask, request, render_template
from flask import jsonify
from ruamel.yaml import YAML
from config_hints import CONFIG_HINTS
from comment_parser import ConfigCommentParser
# 初始化配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False  # 强制块格式
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.explicit_start = True  # 添加YAML头
yaml.allow_duplicate_keys = False  # 禁止重复键

# def save_config(config):
#     path = get_config_path()
#     temp_path = path + ".tmp"
    
#     try:
#         with open(temp_path, 'w', encoding='utf-8') as f:
#             yaml.dump(config, f)
            
#         # 原子替换文件
#         if os.name == 'nt':  # Windows需要特殊处理
#             os.remove(path)
#         os.rename(temp_path, path)
        
#     except Exception as e:
#         if os.path.exists(temp_path):
#             os.remove(temp_path)
#         raise

def get_config_path():
    """获取配置文件路径"""
    data_dir = os.path.join(PROJECT_ROOT, 'data')
    hidden_config = os.path.join(data_dir, '.config.yaml')
    default_config = os.path.join(PROJECT_ROOT, 'config.yaml')
    
    if os.path.exists(hidden_config):
        return hidden_config
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    target_config = os.path.join(data_dir, 'config.yaml')
    if os.path.exists(default_config):
        try:
            with open(default_config, 'r', encoding='utf-8') as f:
                config = yaml.load(f)
            with open(target_config, 'w', encoding='utf-8') as f:
                yaml.dump(config, f)
        except Exception as e:
            print(f"初始化配置失败: {str(e)}")
    return target_config

def load_config():
    """加载配置"""
    try:
        with open(get_config_path(), 'r', encoding='utf-8') as f:
            return yaml.load(f)
    except UnicodeDecodeError:
        with open(get_config_path(), 'r', encoding='utf-8-sig') as f:
            return yaml.load(f)

def save_config(config):
    print(config)
    path = get_config_path()
    temp_path = path + ".tmp"
    
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
            print(f)
            
        # 原子替换文件
        if os.name == 'nt':  # Windows需要特殊处理
            os.remove(path)
        os.rename(temp_path, path)
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    
def parse_form_data(form_data):
    """转换表单数据（修复版）"""
    config = {}
    for key in form_data:
        current = config
        parts = key.split('.')
        for i, part in enumerate(parts[:-1]):
            if '[' in part:
                name, index = part.split('[')
                index = int(index[:-1])
                current = current.setdefault(name, [])
                while len(current) <= index:
                    current.append({})
                current = current[index]
            else:
                current = current.setdefault(part, {})
        
        # 处理最后一级
        last_part = parts[-1]
        if '[' in last_part:
            name, index = last_part.split('[')
            index = int(index[:-1])
            current.setdefault(name, [])
            while len(current[name]) <= index:
                current[name].append('')
            current[name][index] = form_data[key]
        else:
            current[last_part] = form_data[key]
    return config

app = Flask(__name__)

@app.route('/debug')
def debug_comments():
    parser = ConfigCommentParser()
    comments = parser.parse_comments(get_config_path())
    return jsonify({
        "comments_count": len(comments),
        "sample_comments": dict(list(comments.items())[:5])
    })

@app.route('/', methods=['GET', 'POST'])
def config_editor():
    config = load_config()
    if request.method == 'POST':
        try:
            new_config = parse_form_data(request.form)
            save_config(new_config)
            print("保存配置中")
            # print(new_config)
            config = load_config()  # 重新加载最新配置
            return jsonify({
                "status": "success",
                "message": "配置保存成功！",
                "config": config
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"保存失败：{str(e)}"
            }), 500
    
    # GET请求保持原样
    return render_template('editor.html',
                         config=config,
                         comments=ConfigCommentParser().parse_comments(get_config_path()),
                         hints=CONFIG_HINTS)

def open_browser():
    time.sleep(1)
    config = load_config()
    webbrowser.open(f'http://localhost:{config.get("server",{}).get("port",8000)}')

if __name__ == '__main__':
    try:
        config = load_config()
        threading.Thread(target=open_browser).start()
        app.run(
            host=config.get('server',{}).get('ip','0.0.0.0'),
            port=config.get('server',{}).get('port',8000),
            debug=False
        )
    except Exception as e:
        print(f"启动失败: {str(e)}\n请检查配置文件：{get_config_path()}")