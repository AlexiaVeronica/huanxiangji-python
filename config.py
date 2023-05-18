import os

import re

import yaml
import json


class Config:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                f.write('')
            self.config = {}
        else:
            self.config = self._load_config()
            if not isinstance(self.config, dict):
                self.config = {}

    def _load_config(self) -> dict:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config

    def _save_config(self):
        with open(self.file_path, 'w') as f:
            yaml.dump(self.config, f)

    def get_value(self, key):
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k)
            if value is None:
                break
        return value

    def set_value(self, key, value):
        keys = key.split('.')
        node = self.config
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value
        self._save_config()

    def add_value(self, key, value):
        keys = key.split('.')
        node = self.config
        for k in keys[:-1]:
            node = node.setdefault(k, {})
        node[keys[-1]] = value
        self._save_config()

    def delete_value(self, key):
        keys = key.split('.')
        node = self.config
        for k in keys[:-1]:
            node = node.get(k)
            if node is None:
                return
        del node[keys[-1]]
        self._save_config()

    def get_compile_value(self, key):
        regex = re.compile(key, re.IGNORECASE)
        for k, v in self.config.items():
            if regex.search(k):
                return v
            elif isinstance(v, dict):
                value = Config(v).get_value(key)
                if value is not None:
                    return value
        return None


class Vars:
    cf = Config('config.yaml')


# if __name__ == '__main__':
#     ya = Config('config.yaml')
#     set_value = ya.set_value('common_params.user_info', {'name': 'zhangsan', 'age': 18})
