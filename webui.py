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
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

# 初始化配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
yaml = YAML()
yaml.preserve_quotes = True
yaml.default_flow_style = False  # 强制块格式
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.explicit_start = True  # 添加YAML头
yaml.allow_duplicate_keys = False  # 禁止重复键

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
            logging.error(f"初始化配置失败: {str(e)}")
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
    path = get_config_path()
    temp_path = path + ".tmp"
    try:
        logging.debug(f"尝试将配置写入临时文件: {temp_path}")
        with open(temp_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        logging.debug(f"配置已成功写入临时文件: {temp_path}")

        if os.name == 'nt':  # Windows 系统处理
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logging.debug(f"已删除原配置文件: {path}")
                except Exception as e:
                    logging.error(f"删除原配置文件 {path} 失败: {str(e)}")
                    raise
        try:
            os.rename(temp_path, path)
            logging.debug(f"临时文件已重命名为正式配置文件: {path}")
        except Exception as e:
            logging.error(f"重命名临时文件 {temp_path} 到 {path} 失败: {str(e)}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        logging.error(f"保存配置失败: {str(e)}", exc_info=True)
        raise

def parse_form_data(form_data):
    """转换表单数据（修复版）"""
    config = {}
    logging.debug(f"Received form data: {dict(form_data)}")
    for key in form_data:
        current = config
        parts = key.split('.')
        try:
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
        except Exception as e:
            logging.error(f"解析表单数据 {key} 时出错: {str(e)}", exc_info=True)
    logging.debug(f"Parsed form data: {config}")
    return config

def merge_configs(old_config, new_config):
    """合并新旧配置，只应用新配置中的差异部分"""
    if isinstance(old_config, dict) and isinstance(new_config, dict):
        for key in new_config:
            if key in old_config:
                old_config[key] = merge_configs(old_config[key], new_config[key])
            else:
                old_config[key] = new_config[key]
        return old_config
    elif isinstance(old_config, list) and isinstance(new_config, list):
        max_len = max(len(old_config), len(new_config))
        result = old_config[:]
        for i in range(len(result), max_len):
            result.append(None)
        for i in range(max_len):
            if i < len(new_config):
                if i < len(result):
                    result[i] = merge_configs(result[i], new_config[i])
                else:
                    result.append(new_config[i])
        return result
    else:
        return new_config

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
            merged_config = merge_configs(config, new_config)
            save_config(merged_config)
            logging.info("保存配置成功")
            # print(new_config)
            config = load_config()  # 重新加载最新配置
            return jsonify({
                "status": "success",
                "message": "配置保存成功！",
                "config": config
            })
        except Exception as e:
            logging.error(f"保存配置时出错: {str(e)}")
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