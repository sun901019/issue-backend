"""
Issue export services.
"""

import csv
from io import StringIO, BytesIO
from typing import List, Dict
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from ..models import Issue


def export_issues_csv(issues: List[Issue]) -> HttpResponse:
    """匯出 Issue 為 CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="issues.csv"'
    
    writer = csv.writer(response)
    
    # 標題行
    writer.writerow([
        'ID', '標題', '描述', '狀態', '優先級', '類別', '來源',
        '專案', '客戶', '負責人', '回報人',
        '建立時間', '更新時間', '首次回應時間', '解決時間'
    ])
    
    # 資料行
    for issue in issues:
        writer.writerow([
            issue.id,
            issue.title,
            issue.description,
            issue.status,
            issue.priority,
            issue.category,
            issue.source,
            issue.project.name if issue.project else '',
            issue.customer.name if issue.customer else '',
            issue.assignee.username if issue.assignee else '',
            issue.reporter.username if issue.reporter else '',
            issue.created_at.strftime('%Y-%m-%d %H:%M:%S') if issue.created_at else '',
            issue.updated_at.strftime('%Y-%m-%d %H:%M:%S') if issue.updated_at else '',
            issue.first_response_at.strftime('%Y-%m-%d %H:%M:%S') if issue.first_response_at else '',
            issue.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if issue.resolved_at else '',
        ])
    
    return response


def export_issues_xlsx(issues: List[Issue]) -> HttpResponse:
    """匯出 Issue 為 XLSX"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Issues"
    
    # 標題行
    headers = [
        'ID', '標題', '描述', '狀態', '優先級', '類別', '來源',
        '專案', '客戶', '負責人', '回報人',
        '建立時間', '更新時間', '首次回應時間', '解決時間'
    ]
    ws.append(headers)
    
    # 設定標題樣式
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # 資料行
    for issue in issues:
        ws.append([
            issue.id,
            issue.title,
            issue.description,
            issue.status,
            issue.priority,
            issue.category,
            issue.source,
            issue.project.name if issue.project else '',
            issue.customer.name if issue.customer else '',
            issue.assignee.username if issue.assignee else '',
            issue.reporter.username if issue.reporter else '',
            issue.created_at.strftime('%Y-%m-%d %H:%M:%S') if issue.created_at else '',
            issue.updated_at.strftime('%Y-%m-%d %H:%M:%S') if issue.updated_at else '',
            issue.first_response_at.strftime('%Y-%m-%d %H:%M:%S') if issue.first_response_at else '',
            issue.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if issue.resolved_at else '',
        ])
    
    # 自動調整欄寬
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # 儲存到 BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="issues.xlsx"'
    
    return response

