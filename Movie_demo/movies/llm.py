# movies/llm.py
import logging
import requests
from django.conf import settings
from django.core.cache import cache
import hashlib
import re

logger = logging.getLogger(__name__)


class LLMRecommendation:
    # 修正API端点配置
    BASE_URL = "https://api.deepseek.com/v1"  # 使用兼容OpenAI的v1路径
    CHAT_ENDPOINT = "/chat/completions"  # 添加完整端点路径

    @classmethod
    def generate_recommend_reasons(cls, user, movie_ids):
        try:
            # 生成包含电影ID的缓存键
            cache_key = f"llm_recommend_{user.id}_{hashlib.md5(str(sorted(movie_ids)).encode()).hexdigest()}"

            if cached := cache.get(cache_key):
                logger.debug(f"缓存命中: {cache_key}")
                return cached

            # 获取用户数据（添加异常处理）
            try:
                from .models import Review, UserFavorite
                history = Review.objects.filter(user=user).select_related('movie')[:5]
                fav_count = UserFavorite.objects.filter(user=user).count()
            except Exception as e:
                logger.error(f"数据库查询失败: {str(e)}")
                return {"default": "推荐数据生成失败"}

            # 构建提示词模板
            prompt_template = """
            你是一个专业的电影推荐助手，请根据以下信息生成个性化推荐理由：

            用户特征：
            - 用户名：{username}
            - 收藏电影数：{fav_count}
            - 最近观看：{recent_watched}

            推荐要求：
            1. 每个理由不超过20个字
            2. 使用口语化中文
            3. 结合电影特征和用户兴趣
            4. 避免剧透

            待推荐电影ID：{movie_ids}
            """

            # 填充模板内容
            prompt = prompt_template.format(
                username=user.username,
                fav_count=fav_count,
                recent_watched=", ".join([r.movie.title for r in history]),
                movie_ids=", ".join(map(str, movie_ids))
            )[:2000]  # 限制提示词长度

            # 构建完整请求URL
            full_url = f"{cls.BASE_URL}{cls.CHAT_ENDPOINT}"

            # 配置请求参数
            headers = {
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip, deflate"
            }

            payload = {
                "model": "deepseek-reasoner",  # 使用V3模型
                "messages": [
                    {"role": "system", "content": "你是一个电影推荐专家"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "top_p": 0.9,
                "stream": False
            }

            # 添加详细日志
            logger.debug(f"API请求详情:\nURL: {full_url}\nHeaders: {headers}\nPayload: {payload}")

            # 发送请求（添加重试机制）
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('https://', adapter)

            response = session.post(
                full_url,
                json=payload,
                headers=headers,
                timeout=(3.05, 10)  # 连接超时3秒，读取超时10秒
            )

            # 验证响应状态
            response.raise_for_status()

            # 解析响应数据
            result = response.json()
            logger.debug(f"原始API响应: {result}")

            # 校验响应结构
            if not all(key in result for key in ['choices', 'usage']):
                raise ValueError("无效的API响应结构")

            recommendations = cls.parse_llm_response(
                result['choices'][0]['message']['content'],
                movie_ids  # 传递原始电影ID用于校验
            )

            # 缓存结果（1小时）
            cache.set(cache_key, recommendations, 3600)
            return recommendations

        except requests.exceptions.RequestException as e:
            logger.error(f"API请求异常: {str(e)}")
            return {"default": "推荐服务暂时不可用"}
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"响应解析失败: {str(e)}")
            return {"default": "推荐理由生成异常"}
        except Exception as e:
            logger.exception("未处理的异常")
            return {"default": "系统繁忙，请稍后再试"}

    @staticmethod
    def parse_llm_response(text, original_ids):
        """
        增强型响应解析方法
        :param text: LLM返回的原始文本
        :param original_ids: 原始电影ID列表用于校验
        :return: 结构化推荐理由字典
        """
        reasons = {}
        valid_ids = set(map(str, original_ids))

        # 使用正则表达式匹配更灵活的格式
        pattern = re.compile(
            r"(?:\d+[\.、]?)?\s*"  # 可选的编号前缀
            r"(?P<title>.+?)[:：]\s*"  # 电影标题
            r"(?P<reason>.+)"  # 推荐理由
        )

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            match = pattern.match(line)
            if match:
                title = match.group('title').strip()
                reason = match.group('reason').strip()

                # 简单的标题校验（可根据需要扩展）
                if any(char in title for char in ['#', '>', '<']):
                    continue

                reasons[title] = reason[:50]  # 限制理由长度

        # 保底逻辑：如果没有解析到有效结果
        if not reasons:
            return {"default": "精选热门电影推荐"}

        return reasons