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
        completion_rate = round((closed_count / total_count * 100), 1) if total_count > 0 else 0
        open_rate = round((open_count / total_count * 100), 1) if total_count > 0 else 0
        in_progress_rate = round((in_progress_count / total_count * 100), 1) if total_count > 0 else 0
        pending_rate = round((pending_count / total_count * 100), 1) if total_count > 0 else 0
        
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
            'open_rate': open_rate,
            'in_progress_rate': in_progress_rate,
            'pending_rate': pending_rate,
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
        """
        依照 period 取得趨勢資料：
        - month：指定年份的 1~12 月建立數
        - week：指定年月的每週建立數（週區間限制在該月）
        - day：指定年月的每日建立數
        """
        import pendulum
        from django.utils import timezone

        period = request.query_params.get('period', 'month')  # month/week/day
        now = pendulum.instance(timezone.now())

        # 取得查詢的年份／月份（若未指定則使用目前時間）
        year = int(request.query_params.get('year', now.year))
        month = int(request.query_params.get('month', now.month))

        tz = now.timezone
        trend_data = []

        if period == 'month':
            # 1 ~ 12 月
            for m in range(1, 13):
                month_start = pendulum.datetime(year, m, 1, tz=tz)
                next_month = month_start.add(months=1)
                created_count = Issue.objects.filter(
                    created_at__gte=month_start,
                    created_at__lt=next_month
                ).count()
                trend_data.append({
                    'period': f'{m}月',
                    'created': created_count,
                })
        elif period == 'week':
            # 指定月份的每週
            month_start = pendulum.datetime(year, month, 1, tz=tz)
            month_end = month_start.end_of('month')
            current_start = month_start
            week_index = 1

            while current_start <= month_end:
                next_start = current_start.add(days=7)
                if next_start > month_end.add(days=1):
                    next_start = month_end.add(days=1)

                created_count = Issue.objects.filter(
                    created_at__gte=current_start,
                    created_at__lt=next_start
                ).count()

                trend_data.append({
                    'period': f'第{week_index}週',
                    'created': created_count,
                })

                week_index += 1
                current_start = next_start
        else:  # day
            month_start = pendulum.datetime(year, month, 1, tz=tz)
            month_end = month_start.end_of('month')
            current_day = month_start

            while current_day <= month_end:
                next_day = current_day.add(days=1)
                created_count = Issue.objects.filter(
                    created_at__gte=current_day,
                    created_at__lt=next_day
                ).count()

                trend_data.append({
                    'period': current_day.format('MM/DD'),
                    'created': created_count,
                })

                current_day = next_day

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

