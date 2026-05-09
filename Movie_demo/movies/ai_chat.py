# movies/ai_chat.py
import re


from django.conf import settings

import logging
import requests
from requests.adapters import HTTPAdapter
from tmdbsimple import Search
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class AIChatRecommender:
    SYSTEM_PROMPT = """
    你是一个专业的电影推荐助手，请根据对话历史进行自然交流并推荐电影。
    推荐时需要遵循以下规则：

    1. 每次最多推荐3部电影
    2. 推荐理由要口语化，结合用户之前的偏好
    3. 当用户询问具体信息时，展示详细资料
    4. 保持对话友好自然，避免剧透
    """

    @classmethod
    def _call_ai_api(cls, payload):
        """增强版API调用方法"""
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 总重试次数
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
            allowed_methods=["POST"],  # 只重试POST请求
            backoff_factor=1  # 指数退避因子
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        try:
            response = session.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=(3.05, 15)  # 连接超时3秒，读取超时15秒
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.warning("API请求超时，请检查网络连接")
            raise Exception("请求处理超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            raise Exception("AI服务暂时不可用")
    # 修改后的推荐生成方法
    @classmethod
    def generate_recommendation(cls, user, message, history, selected_movie_ids):
        # 构建对话上下文
        messages = [{"role": "system", "content": cls.SYSTEM_PROMPT}]
        messages += cls._format_history(history)
        messages.append({"role": "user", "content": message})

        # 获取个性化数据
        user_profile = cls._get_user_profile(user)
        logger.info(f"用户画像数据: {user_profile}")

        # 调用AI接口
        api_response = cls._call_ai_api({
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 500
        })

        # 解析推荐结果
        try:
            response_content = api_response['choices'][0]['message']['content']
            # 修改后的解析方法，返回TMDB ID
            recommended_ids = []
            search = Search()
            for title in cls._parse_recommendations(response_content):
                # 调用TMDB搜索API获取准确ID
                result = search.movie(query=title, language='zh-CN')
                if result.get('results'):
                    recommended_ids.append(result['results'][0]['id'])

            return {
                "response": response_content,
                "recommended_movies": recommended_ids,  # 返回ID列表
                "history": messages[-5:]
            }
        except KeyError:
            raise Exception("无效的API响应结构")

    @staticmethod
    def _format_history(history):
        """转换历史记录格式"""
        return [{
            "role": msg['role'],
            "content": f"{msg['content']}\n推荐电影：{msg.get('movies', [])}"
        } for msg in history[-5:]]  # 保留最近5条历史

    @staticmethod
    def _parse_recommendations(text):
        """增强版电影标题解析"""
        patterns = [
            r"《(.+?)》",  # 中文书名号
            r"\*(.+?)\*",  # 星号包裹
            r'"(.+?)"',  # 英文引号
            r'推荐(.+?)电影',  # 自然语言模式
            r'([A-Za-z0-9\s:]+)\s\(\d{4}\)'  # 英文标题+年份
        ]

        titles = set()
        for pattern in patterns:
            titles.update(re.findall(pattern, text))

        return list(titles)[:3]  # 最多返回3部

    @staticmethod
    def _get_user_profile(user):
        """获取用户画像数据"""
        from .models import UserFavorite, Review
        return {
            'favorites': list(UserFavorite.objects.filter(user=user)
                            .values_list('movie__title', flat=True)[:5]),
            'recent_reviews': list(Review.objects.filter(user=user)
                                 .order_by('-created_at')
                                 .values_list('movie__title', flat=True)[:3]),
            'total_watched': UserFavorite.objects.filter(user=user).count()
        }