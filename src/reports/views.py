"""
Reports views.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from issues.models import Issue
from .services.metrics import calculate_avg_frt, calculate_avg_mttr
import pendulum


class DashboardSummaryView(APIView):
    """Dashboard 摘要（KPI）"""
    
    def get(self, request):
        from django.db.models import Count
        from datetime import timedelta
        
        # 取得所有 Issue
        all_issues = Issue.objects.all()
        
        # 基本統計
        total_count = all_issues.count()
        open_count = all_issues.filter(status='Open').count()
        in_progress_count = all_issues.filter(status='In Progress').count()
        closed_count = all_issues.filter(status='Closed').count()
        pending_count = all_issues.filter(status='Pending').count()
        
        # 計算平均 FRT 和 MTTR
        avg_frt = calculate_avg_frt(all_issues)
        avg_mttr = calculate_avg_mttr(all_issues.filter(status='Closed'))
        
        # 計算完成率
        completion_rate = round((closed_count / total_count * 100) if total_count > 0 else 0, 1)
        
        # 計算7天趨勢（用於迷你圖表）
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        
        # 過去7天每天的新增 Issue 數量
        trend_data = []
        for i in range(7):
            day_start = (seven_days_ago + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_count = Issue.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            trend_data.append(day_count)
        
        # 計算與上週同期對比（過去7天 vs 再往前7天）
        fourteen_days_ago = now - timedelta(days=14)
        last_week_count = Issue.objects.filter(
            created_at__gte=seven_days_ago,
            created_at__lt=now
        ).count()
        previous_week_count = Issue.objects.filter(
            created_at__gte=fourteen_days_ago,
            created_at__lt=seven_days_ago
        ).count()
        
        # 計算變化百分比
        if previous_week_count > 0:
            change_percentage = round(((last_week_count - previous_week_count) / previous_week_count) * 100, 1)
        else:
            change_percentage = 100.0 if last_week_count > 0 else 0.0
        
        return Response({
            'total': total_count,
            'open': open_count,
            'in_progress': in_progress_count,
            'closed': closed_count,
            'pending': pending_count,
            'avg_frt': round(avg_frt, 2) if avg_frt else None,
            'avg_mttr': round(avg_mttr, 2) if avg_mttr else None,
            'completion_rate': completion_rate,
            'trend_7days': trend_data,
            'change_percentage': change_percentage,
        })


class ReportSummaryView(APIView):
    """年度累計報表"""
    
    def get(self, request):
        year = int(request.query_params.get('year', timezone.now().year))
        
        start_date = pendulum.datetime(year, 1, 1)
        end_date = pendulum.datetime(year, 12, 31, 23, 59, 59)
        
        issues = Issue.objects.filter(
            created_at__gte=start_date.to_datetime_string(),
            created_at__lte=end_date.to_datetime_string(),
        )
        
        total_count = issues.count()
        closed_count = issues.filter(status='Closed').count()
        
        # FRT 計算（平均）
        avg_frt = calculate_avg_frt(issues)
        
        # MTTR 計算（平均）
        avg_mttr = calculate_avg_mttr(issues.filter(status='Closed'))
        
        return Response({
            'year': year,
            'total_count': total_count,
            'closed_count': closed_count,
            'avg_frt': round(avg_frt, 2) if avg_frt else None,
            'avg_mttr': round(avg_mttr, 2) if avg_mttr else None,
            'reopen_rate': 0,  # TODO
        })


class ReportTrendView(APIView):
    """趨勢報表"""
    
    def get(self, request):
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        import pendulum
        
        period = request.query_params.get('period', 'month')  # month/week/day
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        
        # 設定日期範圍
        if date_from:
            start_date = pendulum.parse(date_from)
        else:
            start_date = pendulum.now().subtract(months=6)
        
        if date_to:
            end_date = pendulum.parse(date_to)
        else:
            end_date = pendulum.now()
        
        # 根據期間類型生成時間點
        data_points = []
        current = start_date
        
        if period == 'day':
            while current <= end_date:
                data_points.append(current.format('YYYY-MM-DD'))
                current = current.add(days=1)
        elif period == 'week':
            while current <= end_date:
                week_start = current.start_of('week')
                data_points.append(week_start.format('YYYY-MM-DD'))
                current = current.add(weeks=1)
        else:  # month
            while current <= end_date:
                month_start = current.start_of('month')
                data_points.append(month_start.format('YYYY-MM'))
                current = current.add(months=1)
        
        # 查詢每個時間點的 Issue 數量
        trend_data = []
        for point in data_points:
            if period == 'day':
                date_obj = pendulum.parse(point)
                day_start = date_obj.start_of('day').to_datetime_string()
                day_end = date_obj.end_of('day').to_datetime_string()
                created_count = Issue.objects.filter(
                    created_at__gte=day_start,
                    created_at__lte=day_end
                ).count()
                closed_count = Issue.objects.filter(
                    status='Closed',
                    resolved_at__gte=day_start,
                    resolved_at__lte=day_end
                ).count()
            elif period == 'week':
                date_obj = pendulum.parse(point)
                week_start = date_obj.start_of('week').to_datetime_string()
                week_end = date_obj.end_of('week').to_datetime_string()
                created_count = Issue.objects.filter(
                    created_at__gte=week_start,
                    created_at__lte=week_end
                ).count()
                closed_count = Issue.objects.filter(
                    status='Closed',
                    resolved_at__gte=week_start,
                    resolved_at__lte=week_end
                ).count()
            else:  # month
                date_obj = pendulum.parse(point + '-01')
                month_start = date_obj.start_of('month').to_datetime_string()
                month_end = date_obj.end_of('month').to_datetime_string()
                created_count = Issue.objects.filter(
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).count()
                closed_count = Issue.objects.filter(
                    status='Closed',
                    resolved_at__gte=month_start,
                    resolved_at__lte=month_end
                ).count()
            
            trend_data.append({
                'period': point,
                'created': created_count,
                'closed': closed_count,
            })
        
        return Response({
            'period': period,
            'data': trend_data,
        })


class ReportDimensionsView(APIView):
    """維度分析報表"""
    
    def get(self, request):
        from django.db.models import Count, Avg, Q
        from .services.metrics import calculate_avg_frt, calculate_avg_mttr
        
        dim = request.query_params.get('dim', 'customer')  # customer/assignee/source/category
        metric = request.query_params.get('metric', 'count')  # count/mttr/frt
        top = int(request.query_params.get('top', 10))
        
        top_n = []
        
        if dim == 'customer':
            queryset = Issue.objects.filter(customer__isnull=False).values('customer__name').annotate(
                count=Count('id')
            ).order_by('-count')[:top]
            
            for item in queryset:
                customer_name = item['customer__name']
                customer_issues = Issue.objects.filter(customer__name=customer_name)
                
                result = {
                    'name': customer_name,
                    'count': item['count'],
                }
                
                if metric == 'mttr':
                    avg_mttr = calculate_avg_mttr(customer_issues.filter(status='Closed'))
                    result['value'] = round(avg_mttr, 2) if avg_mttr else None
                elif metric == 'frt':
                    avg_frt = calculate_avg_frt(customer_issues)
                    result['value'] = round(avg_frt, 2) if avg_frt else None
                else:
                    result['value'] = item['count']
                
                top_n.append(result)
        
        elif dim == 'assignee':
            queryset = Issue.objects.filter(assignee__isnull=False).values('assignee__username').annotate(
                count=Count('id')
            ).order_by('-count')[:top]
            
            for item in queryset:
                username = item['assignee__username']
                assignee_issues = Issue.objects.filter(assignee__username=username)
                
                result = {
                    'name': username,
                    'count': item['count'],
                }
                
                if metric == 'mttr':
                    avg_mttr = calculate_avg_mttr(assignee_issues.filter(status='Closed'))
                    result['value'] = round(avg_mttr, 2) if avg_mttr else None
                elif metric == 'frt':
                    avg_frt = calculate_avg_frt(assignee_issues)
                    result['value'] = round(avg_frt, 2) if avg_frt else None
                else:
                    result['value'] = item['count']
                
                top_n.append(result)
        
        elif dim == 'source':
            queryset = Issue.objects.values('source').annotate(
                count=Count('id')
            ).order_by('-count')[:top]
            
            for item in queryset:
                source = item['source']
                source_issues = Issue.objects.filter(source=source)
                
                result = {
                    'name': source,
                    'count': item['count'],
                }
                
                if metric == 'mttr':
                    avg_mttr = calculate_avg_mttr(source_issues.filter(status='Closed'))
                    result['value'] = round(avg_mttr, 2) if avg_mttr else None
                elif metric == 'frt':
                    avg_frt = calculate_avg_frt(source_issues)
                    result['value'] = round(avg_frt, 2) if avg_frt else None
                else:
                    result['value'] = item['count']
                
                top_n.append(result)
        
        elif dim == 'category':
            queryset = Issue.objects.values('category').annotate(
                count=Count('id')
            ).order_by('-count')[:top]
            
            for item in queryset:
                category = item['category']
                category_issues = Issue.objects.filter(category=category)
                
                result = {
                    'name': category,
                    'count': item['count'],
                }
                
                if metric == 'mttr':
                    avg_mttr = calculate_avg_mttr(category_issues.filter(status='Closed'))
                    result['value'] = round(avg_mttr, 2) if avg_mttr else None
                elif metric == 'frt':
                    avg_frt = calculate_avg_frt(category_issues)
                    result['value'] = round(avg_frt, 2) if avg_frt else None
                else:
                    result['value'] = item['count']
                
                top_n.append(result)
        
        return Response({
            'dimension': dim,
            'metric': metric,
            'top_n': top_n,
        })

