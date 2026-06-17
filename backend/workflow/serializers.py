from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import WorkflowConfig, WorkflowStep, Request, ApprovalLog, RequestFile

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class WorkflowStepSerializer(serializers.ModelSerializer):
    required_group_name = serializers.ReadOnlyField(source='required_group.name')

    class Meta:
        model = WorkflowStep
        fields = ['id', 'step_number', 'step_name', 'required_group', 'required_group_name']

class WorkflowConfigSerializer(serializers.ModelSerializer):
    steps = WorkflowStepSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowConfig
        fields = ['id', 'name', 'category', 'description', 'steps']

class ApprovalLogSerializer(serializers.ModelSerializer):
    approver_name = serializers.ReadOnlyField(source='approver.get_full_name')

    class Meta:
        model = ApprovalLog
        fields = ['id', 'approver', 'approver_name', 'step_number', 'step_name', 'action', 'comment', 'created_at']

class RequestFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestFile
        fields = ['id', 'file', 'file_name', 'uploaded_at', 'description']

class RequestSerializer(serializers.ModelSerializer):
    creator_name = serializers.ReadOnlyField(source='creator.get_full_name')
    creator_username = serializers.ReadOnlyField(source='creator.username')
    workflow_name = serializers.ReadOnlyField(source='workflow.name')
    workflow_steps = WorkflowStepSerializer(source='workflow.steps', many=True, read_only=True)
    logs = ApprovalLogSerializer(many=True, read_only=True)
    files = RequestFileSerializer(many=True, read_only=True)
    current_step_info = serializers.SerializerMethodField()
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Request
        fields = [
            'id', 'req_code', 'title', 'description', 'workflow', 'workflow_name', 'workflow_steps',
            'creator', 'creator_name', 'creator_username', 'create_department',
            'current_step_number', 'status', 
            'assigned_to', 'created_at', 'updated_at', 'completed_at', 
            'logs', 'files', 'current_step_info', 'uploaded_files',
            'rating', 'rating_comment'
        ]
        read_only_fields = ['creator', 'current_step_number', 'status', 'created_at', 'updated_at', 'completed_at']

    def get_current_step_info(self, obj):
        step = obj.get_current_step_info()
        if step:
            return WorkflowStepSerializer(step).data
        return None

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])
        request_obj = Request.objects.create(**validated_data)
        for file in uploaded_files:
            RequestFile.objects.create(request=request_obj, file=file)
        return request_obj
