"""
Settings views.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from issues.models import Issue


class DictionaryListView(APIView):
    """字典表列表（讀取）"""
    
    def get(self, request):
        # 從 Issue 模型取得選項
        status_choices = Issue.STATUS_CHOICES
        priority_choices = Issue.PRIORITY_CHOICES
        
        # 預設的類別字典表
        category_choices = [
            ('設備', '設備'),
            ('系統', '系統'),
            ('系統功能', '系統功能'),
            ('網路', '網路'),
            ('其他', '其他'),
        ]
        
        # 預設的來源字典表
        source_choices = [
            ('業務回報', '業務回報'),
            ('現場發現', '現場發現'),
            ('自主發現', '自主發現'),
            ('業主回報', '業主回報'),
            ('Line', 'Line'),
            ('Email', 'Email'),
            ('電話', '電話'),
        ]
        
        # 建立字典表結構
        dictionaries = {
            'status': [
                {'value': choice[0], 'label': choice[1]}
                for choice in status_choices
            ],
            'priority': [
                {'value': choice[0], 'label': choice[1]}
                for choice in priority_choices
            ],
            'category': [
                {'value': choice[0], 'label': choice[1]}
                for choice in category_choices
            ],
            'source': [
                {'value': choice[0], 'label': choice[1]}
                for choice in source_choices
            ],
        }
        
        return Response(dictionaries)
    
    def put(self, request, dict_type):
        """更新字典表（暫時不實作，因為類別和來源是自由文字）"""
        return Response({
            'message': '字典表更新功能開發中。目前類別和來源為自由文字欄位。'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class PreferencesView(APIView):
    """用戶偏好設定"""
    
    def get(self, request):
        # TODO: 實作用戶偏好設定
        return Response({
            'theme': 'light',
            'language': 'zh-TW',
            'page_size': 50,
        })
    
    def put(self, request):
        # TODO: 實作用戶偏好設定更新
        return Response({'message': 'Preferences update coming soon'}, status=status.HTTP_501_NOT_IMPLEMENTED)
