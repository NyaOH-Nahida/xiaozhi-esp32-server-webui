CONFIG_HINTS = {
    # 服务器配置
    "server.ip": "服务器监听地址（0.0.0.0表示所有网络接口）",
    "server.port": "服务运行端口号（建议8000以上）",
    "server.auth.enabled": "是否启用设备连接认证",
    "server.auth.tokens": "设备认证令牌列表（需与固件token匹配）",
    "server.auth.allowed_devices": "设备白名单MAC地址列表（优先级高于token）",
    
    # 日志配置
    "log.log_format": "控制台日志格式（使用{time}等占位符）",
    "log.log_format_file": "文件日志格式",
    "log.log_level": "日志级别：DEBUG/INFO/WARNING/ERROR",
    "log.log_dir": "日志存储目录",
    "log.log_file": "日志文件名",
    "log.data_dir": "数据存储目录",
    
    # 运行时配置
    "delete_audio": "处理完成后是否自动删除音频文件",
    "close_connection_no_voice_time": "无语音输入自动断开时间（秒）",
    "tts_timeout": "语音合成超时时间（秒）",
    "enable_wakeup_words_response_cache": "是否启用唤醒词缓存加速",
    "enable_greeting": "开场是否回复唤醒词",
    "enable_stop_tts_notify": "说完话是否播放提示音",
    "stop_tts_notify_voice": "提示音文件路径",
    
    # 交互配置
    "exit_commands": "退出指令列表（触发后结束对话）",
    "xiaozhi.audio_params": "音频编解码参数配置",
    "module_test.test_sentences": "模块测试用例",
    "wakeup_words": "唤醒词列表",
    
    # 插件配置
    "plugins.get_weather": "天气插件配置（需API Key）",
    "plugins.get_news": "新闻插件配置（RSS源设置）",
    "plugins.home_assistant": "智能家居控制配置",
    "plugins.play_music": "本地音乐播放配置",
    
    # 模型配置
    "prompt": "角色设定提示词（控制对话风格）",
    "selected_module.VAD": "语音活动检测模块选择",
    "selected_module.ASR": "语音识别模块选择",
    "selected_module.LLM": "大语言模型选择",
    "selected_module.TTS": "语音合成模块选择",
    "selected_module.Memory": "记忆模块选择",
    "selected_module.Intent": "意图识别模块选择",
    
    # 高级配置
    "Intent.function_call.functions": "启用的功能插件列表",
    "Memory.mem0ai.api_key": "Mem0AI服务密钥（长期记忆功能）",
    "ASR.DoubaoASR.appid": "火山引擎语音识别APPID",
    "TTS.DoubaoTTS.cluster": "火山引擎语音合成集群配置"
}