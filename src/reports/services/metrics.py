"""
Metrics calculation services.
"""

from typing import Optional
from django.db.models import QuerySet
from issues.models import Issue
import pendulum


def calculate_frt(issue: Issue) -> Optional[float]:
    """
    計算 First Response Time (小時)
    FRT = first_response_at - created_at
    無 first_response_at 時，以首次活動時間估算
    """
    if not issue.first_response_at:
        # 使用首次活動時間（狀態歷史或評論）
        first_activity = None
        if issue.status_history.exists():
            first_activity = issue.status_history.order_by('changed_at').first().changed_at
        elif issue.comments.exists():
            first_activity = issue.comments.order_by('created_at').first().created_at
        
        if not first_activity:
            return None
        
        created = pendulum.instance(issue.created_at)
        activity = pendulum.instance(first_activity)
        return (activity - created).total_hours()
    
    created = pendulum.instance(issue.created_at)
    first_response = pendulum.instance(issue.first_response_at)
    return (first_response - created).total_hours()


def calculate_mttr(issue: Issue) -> Optional[float]:
    """
    計算 Mean Time To Resolve (小時)
    MTTR = resolved_at - created_at（僅 Closed 計入）
    """
    if issue.status != 'Closed' or not issue.resolved_at:
        return None
    
    created = pendulum.instance(issue.created_at)
    resolved = pendulum.instance(issue.resolved_at)
    
    hours = (resolved - created).total_hours()
    
    # 負時間視為異常值
    if hours < 0:
        return None
    
    return hours


def calculate_avg_frt(queryset: QuerySet[Issue]) -> Optional[float]:
    """計算平均 FRT"""
    frt_values = []
    for issue in queryset:
        frt = calculate_frt(issue)
        if frt is not None:
            frt_values.append(frt)
    
    if not frt_values:
        return None
    
    return sum(frt_values) / len(frt_values)


def calculate_avg_mttr(queryset: QuerySet[Issue]) -> Optional[float]:
    """計算平均 MTTR"""
    mttr_values = []
    for issue in queryset:
        mttr = calculate_mttr(issue)
        if mttr is not None:
            mttr_values.append(mttr)
    
    if not mttr_values:
        return None
    
    return sum(mttr_values) / len(mttr_values)

