#!/usr/bin/env python
"""
离线评估推荐模型（不涉及训练）
评估口径：
- 留一法（per-user 留出最近一次 Review 作为正例）
- Top-K 排序指标：Hit@K、NDCG@K、Precision@K、Recall@K

使用现有 RecommendationService.recommend_for_user 确保与线上推荐口径一致。
"""
import os
import sys
import math
from datetime import datetime
from collections import defaultdict

import django
from django.db.models import Count
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Movie_demo.settings')
django.setup()

from movies.models import Review  # noqa: E402
from movies.recommendations import RecommendationService  # noqa: E402


def dcg_at_k(rank_index: int) -> float:
    """基于命中位置的 DCG 贡献，rank 从 1 开始"""
    if rank_index <= 0:
        return 0.0
    # IDCG 对于单一正例为 1.0（rank=1 => 1/log2(2)=1），因此 nDCG 等于此 DCG 值
    return 1.0 / math.log2(rank_index + 1)


def evaluate_topk(top_k_list=(5, 10), min_reviews_per_user=2, max_users=None):
    """
    执行留一法离线评估：
    - 对有至少 min_reviews_per_user 条评论的用户，按 created_at 排序，取“最近一条”作为正例
    - 使用推荐服务生成 Top-K 列表，计算命中位置与指标
    """
    service = RecommendationService(force_retrain=False)

    # 选取有效用户：至少 n 条评论
    user_ids = (
        Review.objects.values('user_id')
        .annotate(n=Count('id'))
        .filter(n__gte=min_reviews_per_user)
        .values_list('user_id', flat=True)
    )
    user_ids = list(user_ids)
    if max_users is not None:
        user_ids = user_ids[:max_users]

    # 收集每个用户的留出正例（最近一次）
    user_to_holdout = {}
    for uid in user_ids:
        last = (
            Review.objects.filter(user_id=uid)
            .order_by('-created_at')
            .values_list('movie__tmdb_id', flat=True)
            .first()
        )
        if last:
            user_to_holdout[uid] = int(last)

    if not user_to_holdout:
        print("没有可评估的用户（请确认有 Review 数据）。")
        return {}

    metrics = {k: defaultdict(float) for k in top_k_list}
    # 记录命中排名分布（用于诊断）
    rank_hist = {k: defaultdict(int) for k in top_k_list}

    total_users = 0
    for uid, pos_item in user_to_holdout.items():
        total_users += 1

        # 留一法：把“留出的正例”从已看集合中移除，保证推荐候选集里包含该正例
        # （避免因为线上/服务端默认过滤已看电影，导致离线 Hit@K 永远为 0）
        watched_tmdb_ids = set(
            Review.objects.filter(user_id=uid).values_list('movie__tmdb_id', flat=True)
        )
        watched_tmdb_ids.discard(int(pos_item))

        # 为当前用户生成推荐
        for k in top_k_list:
            try:
                rec_ids = service.recommend_for_user(
                    uid,
                    top_n=k,
                    watched_tmdb_ids=watched_tmdb_ids
                )
            except Exception as e:
                # 失败按未命中处理
                rec_ids = []
                print(f"[WARN] 用户 {uid} 生成推荐失败: {e}")

            if not rec_ids:
                continue

            # 命中检测
            hit = 1.0 if pos_item in rec_ids else 0.0
            metrics[k]['hit'] += hit

            # 若命中，计算排名相关
            if hit:
                rank = rec_ids.index(pos_item) + 1  # 1-based
                rank_hist[k][rank] += 1
                metrics[k]['ndcg'] += dcg_at_k(rank)
                # 单正例时：
                # Precision@K = 1/K 若命中，否则 0
                # Recall@K = 1 若命中，否则 0
                metrics[k]['precision'] += 1.0 / float(k)
                metrics[k]['recall'] += 1.0
            else:
                # 未命中
                # Precision@K = 0, Recall@K = 0, NDCG@K = 0
                pass

    # 汇总
    report = {}
    for k in top_k_list:
        if total_users == 0:
            agg = {'users': 0, 'hit@k': 0.0, 'ndcg@k': 0.0, 'precision@k': 0.0, 'recall@k': 0.0}
        else:
            agg = {
                'users': total_users,
                'hit@k': metrics[k]['hit'] / total_users,
                'ndcg@k': metrics[k]['ndcg'] / total_users,
                'precision@k': metrics[k]['precision'] / total_users,
                'recall@k': metrics[k]['recall'] / total_users,
            }
        report[k] = {
            'aggregate': agg,
            'rank_histogram': dict(sorted(rank_hist[k].items(), key=lambda x: x[0])),
        }
    return report


def main():
    print("========== 推荐模型离线评估 ==========")
    print(f"时间: {datetime.now().isoformat()}")
    top_k_list = (5, 10)
    report = evaluate_topk(top_k_list=top_k_list, min_reviews_per_user=2, max_users=None)

    if not report:
        return

    for k in top_k_list:
        agg = report[k]['aggregate']
        print(f"\n--- Top-{k} ---")
        print(f"Users: {agg['users']}")
        print(f"Hit@{k}: {agg['hit@k']:.4f}")
        print(f"NDCG@{k}: {agg['ndcg@k']:.4f}")
        print(f"Precision@{k}: {agg['precision@k']:.4f}")
        print(f"Recall@{k}: {agg['recall@k']:.4f}")
        ranks = report[k]['rank_histogram']
        if ranks:
            ranks_str = ', '.join([f"r{r}:{c}" for r, c in ranks.items()])
            print(f"Hit Rank Histogram: {ranks_str}")
        else:
            print("Hit Rank Histogram: {}")


if __name__ == "__main__":
    main()








