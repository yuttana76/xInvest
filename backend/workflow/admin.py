from django.contrib import admin
from .models import WorkflowConfig, WorkflowStep, Request, ApprovalLog, RequestFile

class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 1

class ApprovalLogInline(admin.TabularInline):
    model = ApprovalLog
    readonly_fields = ('approver', 'step_number', 'step_name', 'action', 'comment', 'created_at')
    extra = 0
    can_delete = False

class RequestFileInline(admin.TabularInline):
    model = RequestFile
    extra = 1

@admin.register(WorkflowConfig)
class WorkflowConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    inlines = [WorkflowStepInline]

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('req_code','title', 'workflow', 'creator', 'status', 'current_step_number', 'created_at')
    list_filter = ('status', 'workflow')
    search_fields = ('req_code','title', 'creator__username', 'creator__email')
    inlines = [ApprovalLogInline, RequestFileInline]
    readonly_fields = ('creator', 'created_at', 'updated_at', 'completed_at')

@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'approver', 'step_name', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('request__title', 'approver__username', 'comment')
