from typing import List, Tuple, Dict, Any, Optional
from app.log import logger
from app.plugins import _PluginBase
import xml.etree.ElementTree as ET
import os
from app.modules.emby import Emby

class EmbyNfoReader(_PluginBase):
    # 插件信息
    plugin_name = "Emby NFO 读取器"
    plugin_desc = "读取Emby媒体库中视频文件的NFO信息，包括地区、名称、年份、格式等信息"
    plugin_icon = "图标URL"
    plugin_version = "1.0"
    plugin_author = "作者名"
    author_url = "作者URL"
    plugin_config_prefix = "embynforeader_"
    plugin_order = 31
    auth_level = 1

    # 私有变量
    _host: str = None
    _api_key: str = None
    _onlyonce: bool = False
    _emby_client: Optional[Emby] = None

    def init_plugin(self, config: dict = None):
        if config:
            self._host = config.get('host')
            self._api_key = config.get('api_key')
            self._onlyonce = config.get('onlyonce')

        if self._onlyonce:
            self._task()
            self._onlyonce = False
        
        self.__update_config()

    def _task(self):
        """执行NFO读取任务"""
        if not self._emby_client:
            self._emby_client = Emby(host=self._host, api_key=self._api_key)

        # 获取媒体库所有项目
        items = self._emby_client.get_all_items()
        if not items:
            logger.error("未能获取到Emby媒体库项目")
            return

        for item in items:
            nfo_path = self._get_nfo_path(item)
            if not nfo_path or not os.path.exists(nfo_path):
                continue

            # 解析NFO文件
            media_info = self._parse_nfo(nfo_path)
            if media_info:
                logger.info(f"媒体信息: {media_info}")

    def _get_nfo_path(self, item: dict) -> Optional[str]:
        """获取NFO文件路径"""
        if 'Path' not in item:
            return None
        
        base_path = os.path.dirname(item['Path'])
        nfo_name = os.path.splitext(os.path.basename(item['Path']))[0] + '.nfo'
        return os.path.join(base_path, nfo_name)

    def _parse_nfo(self, nfo_path: str) -> Optional[Dict]:
        """解析NFO文件内容"""
        try:
            tree = ET.parse(nfo_path)
            root = tree.getroot()

            info = {
                'title': self._get_element_text(root, 'title'),
                'original_title': self._get_element_text(root, 'originaltitle'),
                'year': self._get_element_text(root, 'year'),
                'country': [c.text for c in root.findall('country')],
                'resolution': self._parse_resolution(root),
                'video_codec': self._parse_video_codec(root),
                'source': self._parse_source(root),
                'release_group': self._parse_release_group(root)
            }
            return info
        except Exception as e:
            logger.error(f"解析NFO文件出错: {str(e)}")
            return None

    @staticmethod
    def _get_element_text(root, tag: str) -> str:
        """获取XML元素文本"""
        element = root.find(tag)
        return element.text if element is not None else ""

    @staticmethod
    def _parse_resolution(root) -> str:
        """解析分辨率信息"""
        # 实际实现需要根据具体NFO文件格式来解析
        return ""

    @staticmethod
    def _parse_video_codec(root) -> str:
        """解析视频编码信息"""
        # 实际实现需要根据具体NFO文件格式来解析
        return ""

    @staticmethod
    def _parse_source(root) -> str:
        """解析来源格式信息"""
        # 实际实现需要根据具体NFO文件格式来解析
        return ""

    @staticmethod
    def _parse_release_group(root) -> str:
        """解析制作组信息"""
        # 实际实现需要根据具体NFO文件格式来解析
        return ""

    def __update_config(self):
        self.update_config({
            'host': self._host,
            'api_key': self._api_key,
            'onlyonce': self._onlyonce
        })

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        return [{
            'component': 'VForm',
            'content': [
                {
                    'component': 'VRow',
                    'content': [
                        {
                            'component': 'VCol',
                            'props': {
                                'cols': 12,
                                'md': 6
                            },
                            'content': [
                                {
                                    'component': 'VTextField',
                                    'props': {
                                        'model': 'host',
                                        'label': 'Emby服务器地址',
                                        'placeholder': 'http://localhost:8096'
                                    }
                                }
                            ]
                        },
                        {
                            'component': 'VCol',
                            'props': {
                                'cols': 12,
                                'md': 6
                            },
                            'content': [
                                {
                                    'component': 'VTextField',
                                    'props': {
                                        'model': 'api_key',
                                        'label': 'API密钥',
                                        'placeholder': '输入Emby API密钥'
                                    }
                                }
                            ]
                        }
                    ]
                },
                {
                    'component': 'VRow',
                    'content': [
                        {
                            'component': 'VCol',
                            'props': {
                                'cols': 12
                            },
                            'content': [
                                {
                                    'component': 'VSwitch',
                                    'props': {
                                        'model': 'onlyonce',
                                        'label': '立即运行一次'
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }], {
            'host': 'http://localhost:8096',
            'api_key': '',
            'onlyonce': False
        }

    # 必要的接口实现
    def get_state(self) -> bool:
        return self._onlyonce

    def get_command(self) -> List[Dict[str, Any]]:
        pass

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        pass 