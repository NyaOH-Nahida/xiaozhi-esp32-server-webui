import os
import threading
import webbrowser
import time
from flask import Flask, request, render_template
from ruamel.yaml import YAML
from config_hints import CONFIG_HINTS  # 配置提示数据

# 初始化配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.preserve_quotes = True

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
    """保存配置"""
    with open(get_config_path(), 'w', encoding='utf-8') as f:
        yaml.dump(config, f)

def parse_form_data(form_data):
    """转换表单数据"""
    config = {}
    for key in form_data:
        parts = key.split('.')
        current = config
        for i, part in enumerate(parts):
            if part.endswith(']'):
                name, index = part[:-1].split('[')
                index = int(index)
                if name not in current:
                    current[name] = []
                while len(current[name]) <= index:
                    current[name].append({} if i < len(parts)-1 else '')
                if i == len(parts)-1:
                    current[name][index] = request.form[key]
                else:
                    current = current[name][index]
                    if not isinstance(current, dict):
                        current = {}
            else:
                if i == len(parts)-1:
                    current[part] = request.form[key]
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
    return config

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def config_editor():
    config = load_config()
    if request.method == 'POST':
        new_config = parse_form_data(request.form)
        save_config(new_config)
    return render_template('editor.html', 
                         config=config,
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