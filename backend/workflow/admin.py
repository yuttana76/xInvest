from django.contrib import admin
from .models import WorkflowConfig, WorkflowStep, Request, ApprovalLog, RequestFile, RequestSubject


class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 1


class RequestSubjectInline(admin.TabularInline):
    model = RequestSubject
    extra = 1
    fields = ('order', 'name', 'code', 'is_active')


class ApprovalLogInline(admin.TabularInline):
    model = ApprovalLog
    readonly_fields = ('approver', 'step_number', 'step_name', 'action', 'comment', 'created_at')
    extra = 0
    can_delete = False


class RequestFileInline(admin.TabularInline):
    model = RequestFile
    extra = 1


@admin.register(RequestSubject)
class RequestSubjectAdmin(admin.ModelAdmin):
    list_display = ('order', 'workflow', 'name', 'code', 'is_active')
    list_display_links = ('name',)
    list_editable = ('order', 'is_active')
    list_filter = ('workflow', 'is_active')
    search_fields = ('name', 'code', 'workflow__name')


@admin.register(WorkflowConfig)
class WorkflowConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    inlines = [WorkflowStepInline, RequestSubjectInline]


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('req_code', 'title', 'workflow', 'creator', 'status', 'priorify', 'expectDate', 'auditFlag', 'get_current_step', 'created_at')
    list_filter = ('status', 'workflow', 'priorify', 'auditFlag')
    search_fields = ('req_code', 'title', 'creator__username', 'creator__email')
    inlines = [ApprovalLogInline, RequestFileInline]
    readonly_fields = ('creator', 'created_at', 'updated_at', 'completed_at')
    filter_horizontal = ('reqSubject',)

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


@admin.register(RequestFile)
class RequestFileAdmin(admin.ModelAdmin):
    list_display = ('request', 'file', 'file_name', 'uploaded_at')
    list_filter = ('request', 'uploaded_at')
    search_fields = ('request__title', 'file_name')

