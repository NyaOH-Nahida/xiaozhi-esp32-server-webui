from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from collections.abc import MutableMapping, MutableSequence

class ConfigCommentParser:
    def __init__(self):
        self.yaml = YAML(typ='rt')
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def parse_comments(self, file_path):
        """主解析方法，包含完整异常处理"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = self.yaml.load(f)
                comments = {}
                self._walk(config, comments)
                return comments
        except Exception as e:
            print(f"解析失败: {type(e).__name__} - {str(e)}")
            return {}

    def _walk(self, node, comments, path=''):
        """增强型递归遍历方法"""
        try:
            if isinstance(node, CommentedMap):
                self._process_mapping(node, comments, path)
            elif isinstance(node, CommentedSeq):
                self._process_sequence(node, comments, path)
        except Exception as e:
            print(f"遍历失败 @ {path}: {type(e).__name__} - {str(e)}")

    def _process_mapping(self, node, comments, path):
        """处理字典结构的完整方案"""
        try:
            # 处理当前层级的注释
            self._process_current_level_comments(node, path, comments)
            
            for key in node:
                current_path = f"{path}.{key}" if path else key
                
                # 处理键的注释
                self._process_key_comments(node, key, current_path, comments)
                
                # 递归处理子节点
                self._walk(node[key], comments, current_path)
        except Exception as e:
            print(f"字典处理失败 @ {path}: {str(e)}")

    def _process_sequence(self, node, comments, path):
        """处理数组结构的完整方案"""
        try:
            # 处理当前层级的注释
            self._process_current_level_comments(node, path, comments)
            
            for idx, item in enumerate(node):
                current_path = f"{path}[{idx}]"
                
                # 处理数组项注释
                self._process_item_comments(node, idx, current_path, comments)
                
                # 递归处理子节点
                self._walk(item, comments, current_path)
        except Exception as e:
            print(f"数组处理失败 @ {path}: {str(e)}")

    def _process_current_level_comments(self, node, path, comments):
        """处理节点自身注释"""
        try:
            if hasattr(node, 'ca') and node.ca.comment:
                for comment in node.ca.comment:
                    if comment and hasattr(comment, 'value'):
                        lines = [c.strip() for c in comment.value.split('\n') if c.strip()]
                        if lines:
                            comments.setdefault(path, []).extend(lines)
        except Exception as e:
            print(f"层级注释处理失败 @ {path}: {str(e)}")

    def _process_key_comments(self, node, key, current_path, comments):
        """处理字典键的注释"""
        try:
            if key in node.ca.items:
                item = node.ca.items[key]
                # 块注释（键上方）
                if len(item) >= 3 and item[2]:
                    self._add_comment(item[2], current_path, comments)
                # 行尾注释
                if len(item) >= 4 and item[3]:
                    self._add_comment(item[3], current_path, comments)
        except Exception as e:
            print(f"键注释处理失败 @ {current_path}: {str(e)}")

    def _process_item_comments(self, node, idx, current_path, comments):
        """处理数组项的注释"""
        try:
            if hasattr(node, 'ca') and node.ca.items:
                # 处理数组项前的块注释
                if idx < len(node.ca.items):
                    item = node.ca.items[idx]
                    if item and len(item) >= 1 and item[0]:
                        self._add_comment(item[0], current_path, comments)
                
                # 处理行尾注释
                if idx < len(node.ca.items):
                    item = node.ca.items[idx]
                    if item and len(item) >= 4 and item[3]:
                        self._add_comment(item[3], current_path, comments)
        except Exception as e:
            print(f"数组项注释处理失败 @ {current_path}: {str(e)}")

    def _add_comment(self, comment, path, comments):
        """安全注释添加方法"""
        try:
            if not comment:
                return
                
            lines = []
            # 处理不同注释类型
            if isinstance(comment, list):
                for c in comment:
                    if hasattr(c, 'value'):
                        lines.extend(c.value.splitlines())
            elif hasattr(comment, 'value'):
                lines = comment.value.splitlines()
            
            # 清洗注释内容
            cleaned = [line.strip().lstrip('#').strip() for line in lines if line.strip()]
            if cleaned:
                comments.setdefault(path, []).extend(cleaned)
        except Exception as e:
            print(f"注释添加失败 @ {path}: {str(e)}")

