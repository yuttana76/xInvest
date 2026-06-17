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
    list_display = ('req_code', 'title', 'workflow', 'creator', 'status', 'get_current_step', 'created_at')
    list_filter = ('status', 'workflow')
    search_fields = ('req_code', 'title', 'creator__username', 'creator__email')
    inlines = [ApprovalLogInline, RequestFileInline]
    readonly_fields = ('creator', 'created_at', 'updated_at', 'completed_at')

    def get_current_step(self, obj):
        step = obj.get_current_step_info()
        if step:
            return f"Step {obj.current_step_number}: {step.step_name}"
        return f"Step {obj.current_step_number}"
    get_current_step.short_description = 'Current Step'

@admin.register(ApprovalLog)
class ApprovalLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'approver', 'step_name', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('request__title', 'approver__username', 'comment')

@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ('step_name', 'workflow', 'step_number', 'required_group', 'is_department_manager')
    list_filter = ('workflow', 'required_group', 'is_department_manager')
    search_fields = ('step_name', 'workflow__name')

# file
@admin.register(RequestFile)
class RequestFileAdmin(admin.ModelAdmin):
    list_display = ('request', 'file', 'file_name', 'uploaded_at')
    list_filter = ('request', 'uploaded_at')
    search_fields = ('request__title', 'file_name')
