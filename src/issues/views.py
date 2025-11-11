"""
Issue views.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Issue, IssueComment, IssueAttachment
from .serializers import IssueSerializer, IssueDetailSerializer, IssueCommentSerializer, IssueAttachmentSerializer
from .models import IssueRelation
from .serializers import IssueRelationSerializer


class IssueListView(APIView):
    """Issue 列表與查詢"""
    
    def get(self, request):
        queryset = (
            Issue.objects.all()
            .select_related('project', 'customer', 'assignee', 'reporter', 'warranty')
            .prefetch_related('customer__warranties')
        )
        
        # 篩選條件
        if status_list := request.query_params.getlist('status[]'):
            queryset = queryset.filter(status__in=status_list)
        
        if priority_list := request.query_params.getlist('priority[]'):
            queryset = queryset.filter(priority__in=priority_list)
        
        if category_list := request.query_params.getlist('category[]'):
            queryset = queryset.filter(category__in=category_list)
        
        if source_list := request.query_params.getlist('source[]'):
            queryset = queryset.filter(source__in=source_list)
        
        if project_id := request.query_params.get('project_id'):
            queryset = queryset.filter(project_id=project_id)
        
        if customer_id := request.query_params.get('customer_id'):
            queryset = queryset.filter(customer_id=customer_id)
        
        if assignee_id := request.query_params.get('assignee_id'):
            queryset = queryset.filter(assignee_id=assignee_id)
        
        if date_from := request.query_params.get('from'):
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to := request.query_params.get('to'):
            queryset = queryset.filter(created_at__lte=date_to)
        
        if search := request.query_params.get('q'):
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # 排序
        order_by = request.query_params.get('ordering', '-updated_at')
        # 支援多欄排序（用逗號分隔）
        if ',' in order_by:
            order_fields = [f.strip() for f in order_by.split(',')]
            queryset = queryset.order_by(*order_fields)
        else:
            queryset = queryset.order_by(order_by)
        
        # 分頁
        page_size = int(request.query_params.get('page_size', 50))
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = IssueSerializer(queryset[start:end], many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
        })
    
    def post(self, request):
        """建立 Issue"""
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            issue = serializer.save()
            if not issue.reporter:
                from django.contrib.auth.models import User
                first_user = User.objects.first()
                if first_user:
                    issue.reporter = first_user
                    issue.save()
            response_serializer = IssueSerializer(issue)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueDetailView(APIView):
    """Issue 詳細（含活動、子任務、關聯、附件）"""
    
    def get(self, request, pk):
        try:
            issue = (
                Issue.objects.select_related(
                    'project', 'customer', 'assignee', 'reporter', 'warranty'
                )
                .prefetch_related('customer__warranties')
                .get(pk=pk)
            )
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IssueDetailSerializer(issue)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """更新 Issue"""
        try:
            issue = Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = IssueSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            issue = serializer.save()
            response_serializer = IssueSerializer(issue)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """刪除 Issue"""
        try:
            issue = Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        issue.delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)


class IssueStatusUpdateView(APIView):
    """狀態變更（寫入歷史）"""
    
    def patch(self, request, pk):
        try:
            issue = Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = issue.status
        issue.status = new_status
        issue.save()
        
        # 寫入狀態歷史
        from .models import IssueStatusHistory
        IssueStatusHistory.objects.create(
            issue=issue,
            from_status=old_status,
            to_status=new_status,
            changed_by=request.user if request.user.is_authenticated else None,
        )
        
        serializer = IssueSerializer(issue)
        return Response(serializer.data)


class IssueBatchUpdateView(APIView):
    """批次更新 Issue（狀態/指派）"""
    
    def post(self, request):
        issue_ids = request.data.get('issue_ids', [])
        if not issue_ids:
            return Response({'error': 'issue_ids is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 取得要更新的欄位
        new_status = request.data.get('status')
        new_assignee_id = request.data.get('assignee_id')
        
        if not new_status and not new_assignee_id:
            return Response({'error': 'status or assignee_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 批次更新
        updated_count = 0
        from .models import IssueStatusHistory
        from django.contrib.auth.models import User
        
        issues = Issue.objects.filter(id__in=issue_ids)
        
        for issue in issues:
            if new_status and issue.status != new_status:
                old_status = issue.status
                issue.status = new_status
                # 寫入狀態歷史
                IssueStatusHistory.objects.create(
                    issue=issue,
                    from_status=old_status,
                    to_status=new_status,
                    changed_by=request.user if request.user.is_authenticated else None,
                )
            
            if new_assignee_id:
                try:
                    assignee = User.objects.get(id=new_assignee_id)
                    issue.assignee = assignee
                except User.DoesNotExist:
                    continue
            
            issue.save()
            updated_count += 1
        
        return Response({
            'success': True,
            'updated_count': updated_count,
            'total_count': len(issue_ids),
        })


class IssueAttachmentView(APIView):
    """附件管理"""
    
    def get(self, request, pk):
        """取得 Issue 的附件列表"""
        try:
            issue = Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        attachments = IssueAttachment.objects.filter(issue=issue).order_by('-created_at')
        serializer = IssueAttachmentSerializer(attachments, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, pk):
        """上傳附件"""
        import os
        
        try:
            issue = Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if 'file' not in request.FILES:
            return Response({'error': 'file is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # 白名單檢查
        allowed_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.zip']
        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in allowed_extensions:
            return Response({
                'error': f'不支援的檔案格式。允許的格式：{", ".join(allowed_extensions)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 大小限制（10MB）
        if file.size > 10 * 1024 * 1024:
            return Response({'error': '檔案大小不能超過 10MB'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 儲存檔案
        attachment = IssueAttachment.objects.create(
            issue=issue,
            file=file,
            filename=file.name,
            uploaded_by=request.user if request.user.is_authenticated else None,
        )
        
        serializer = IssueAttachmentSerializer(attachment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, pk, attachment_id):
        """刪除附件"""
        try:
            attachment = IssueAttachment.objects.get(pk=attachment_id, issue_id=pk)
            attachment.file.delete()  # 刪除檔案
            attachment.delete()
            return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)
        except IssueAttachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)


class IssueCommentView(APIView):
    """評論管理"""
    
    def get(self, request, pk):
        """取得評論列表"""
        comments = IssueComment.objects.filter(issue_id=pk).order_by('-created_at')
        serializer = IssueCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        """建立評論"""
        try:
            issue = Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # 如果沒有認證用戶，使用第一個用戶或 Issue 的 reporter
        author = request.user if request.user.is_authenticated else None
        if not author:
            from django.contrib.auth.models import User
            author = issue.reporter or User.objects.first()
        
        serializer = IssueCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(issue=issue, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueCommentDetailView(APIView):
    """單筆評論管理"""

    def put(self, request, pk, comment_id):
        try:
            comment = IssueComment.objects.get(pk=comment_id, issue_id=pk)
        except IssueComment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = IssueCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, comment_id):
        try:
            comment = IssueComment.objects.get(pk=comment_id, issue_id=pk)
        except IssueComment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)


class IssueRelationView(APIView):
    """Issue 關聯管理"""

    reverse_map = {
        'relates': 'relates',
        'duplicates': 'duplicates',
    }

    def get(self, request, pk):
        relations = IssueRelation.objects.filter(issue_id=pk).select_related('related_issue')
        serializer = IssueRelationSerializer(relations, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        try:
            issue = Issue.objects.get(pk=pk)
        except Issue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=status.HTTP_404_NOT_FOUND)

        related_issue_id = request.data.get('related_issue')
        relation_type = request.data.get('relation_type')

        if not related_issue_id or not relation_type:
            return Response({'error': 'related_issue 和 relation_type 為必填'}, status=status.HTTP_400_BAD_REQUEST)

        if int(related_issue_id) == issue.id:
            return Response({'error': '無法與自己建立關聯'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            related_issue = Issue.objects.get(pk=related_issue_id)
        except Issue.DoesNotExist:
            return Response({'error': 'Related issue not found'}, status=status.HTTP_404_NOT_FOUND)

        if relation_type not in dict(IssueRelation.RELATION_TYPES):
            return Response({'error': '無效的 relation_type'}, status=status.HTTP_400_BAD_REQUEST)

        relation, created = IssueRelation.objects.get_or_create(
            issue=issue,
            related_issue=related_issue,
            relation_type=relation_type,
        )
        reverse_type = self.reverse_map.get(relation_type, 'relates')
        IssueRelation.objects.get_or_create(
            issue=related_issue,
            related_issue=issue,
            relation_type=reverse_type,
        )

        serializer = IssueRelationSerializer(relation)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class IssueRelationDetailView(APIView):
    """單筆關聯管理"""

    reverse_map = IssueRelationView.reverse_map

    def delete(self, request, pk, relation_id):
        try:
            relation = IssueRelation.objects.get(pk=relation_id, issue_id=pk)
        except IssueRelation.DoesNotExist:
            return Response({'error': 'Relation not found'}, status=status.HTTP_404_NOT_FOUND)

        reverse_type = self.reverse_map.get(relation.relation_type, 'relates')
        IssueRelation.objects.filter(
            issue=relation.related_issue,
            related_issue=relation.issue,
            relation_type=reverse_type,
        ).delete()

        relation.delete()
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)


class IssueImportView(APIView):
    """匯入 Issue（CSV/XLSX）"""
    
    def post(self, request):
        from .services.import_service import parse_csv_file, parse_xlsx_file, import_issues
        from django.contrib.auth.models import User
        
        if 'file' not in request.FILES:
            return Response({'error': '請選擇檔案'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        file_content = file.read()
        
        # 判斷檔案類型
        filename = file.name.lower()
        if filename.endswith('.csv'):
            try:
                data = parse_csv_file(file_content)
            except Exception as e:
                return Response({'error': f'CSV 解析失敗：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        elif filename.endswith(('.xlsx', '.xls')):
            try:
                data = parse_xlsx_file(file_content)
            except Exception as e:
                return Response({'error': f'Excel 解析失敗：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '不支援的檔案格式，請使用 CSV 或 XLSX'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not data:
            return Response({'error': '檔案為空或格式不正確'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 取得預設用戶
        default_user = None
        if request.user.is_authenticated:
            default_user = request.user
        else:
            default_user = User.objects.first()
        
        # 匯入資料
        success_count, error_count, errors = import_issues(data, default_user)
        
        return Response({
            'success': True,
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10],  # 只返回前 10 個錯誤
            'message': f'成功匯入 {success_count} 筆，失敗 {error_count} 筆'
        })


class IssueExportView(APIView):
    """匯出 Issue（CSV/XLSX）"""
    
    def get(self, request):
        from .services.export import export_issues_csv, export_issues_xlsx
        from django.db.models import Q
        
        # 取得篩選條件（與列表 API 相同）
        queryset = Issue.objects.all()
        
        if status_list := request.query_params.getlist('status[]'):
            queryset = queryset.filter(status__in=status_list)
        
        if priority_list := request.query_params.getlist('priority[]'):
            queryset = queryset.filter(priority__in=priority_list)
        
        if category_list := request.query_params.getlist('category[]'):
            queryset = queryset.filter(category__in=category_list)
        
        if source_list := request.query_params.getlist('source[]'):
            queryset = queryset.filter(source__in=source_list)
        
        if project_id := request.query_params.get('project_id'):
            queryset = queryset.filter(project_id=project_id)
        
        if customer_id := request.query_params.get('customer_id'):
            queryset = queryset.filter(customer_id=customer_id)
        
        if assignee_id := request.query_params.get('assignee_id'):
            queryset = queryset.filter(assignee_id=assignee_id)
        
        if date_from := request.query_params.get('from'):
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to := request.query_params.get('to'):
            queryset = queryset.filter(created_at__lte=date_to)
        
        if search := request.query_params.get('q'):
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # 預載入關聯資料
        issues = queryset.select_related('project', 'customer', 'assignee', 'reporter').order_by('-created_at')
        
        # 根據格式選擇匯出方式
        format_type = request.query_params.get('format', 'xlsx').lower()
        
        if format_type == 'csv':
            return export_issues_csv(list(issues))
        else:
            return export_issues_xlsx(list(issues))

