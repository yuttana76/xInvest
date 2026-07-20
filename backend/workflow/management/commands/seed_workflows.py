import json
import os

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from workflow.models import WorkflowConfig, WorkflowStep, RequestSubject

DEFAULT_SPEC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'fixtures', 'workflows_seed.json',
)


class Command(BaseCommand):
    help = (
        "Seed WorkflowConfig/WorkflowStep/RequestSubject (and the auth Groups "
        "they reference) from a JSON spec file. Idempotent — safe to re-run on "
        "every deploy. See workflow/fixtures/workflows_seed.json for the format."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', default=DEFAULT_SPEC_PATH,
            help=f"Path to the JSON spec file (default: {DEFAULT_SPEC_PATH})",
        )

    def handle(self, *args, **options):
        file_path = options['file']
        if not os.path.exists(file_path):
            raise CommandError(f"Spec file not found: {file_path}")

        with open(file_path, encoding='utf-8') as f:
            spec = json.load(f)

        with transaction.atomic():
            groups = {}
            for group_name in spec.get('groups', []):
                group, _ = Group.objects.get_or_create(name=group_name)
                groups[group_name] = group

            workflow_count = 0
            step_count = 0
            subject_count = 0

            for wf_spec in spec.get('workflows', []):
                workflow, _ = WorkflowConfig.objects.update_or_create(
                    name=wf_spec['name'],
                    defaults={
                        'category': wf_spec.get('category', ''),
                        'description': wf_spec.get('description', ''),
                        'prefix': wf_spec.get('prefix', 'REQ'),
                    },
                )
                workflow_count += 1

                for step_spec in wf_spec.get('steps', []):
                    group_name = step_spec.get('required_group')
                    WorkflowStep.objects.update_or_create(
                        workflow=workflow,
                        step_number=step_spec['step_number'],
                        defaults={
                            'step_name': step_spec['step_name'],
                            'required_group': groups.get(group_name) if group_name else None,
                            'is_department_manager': step_spec.get('is_department_manager', False),
                        },
                    )
                    step_count += 1

                for subj_spec in wf_spec.get('subjects', []):
                    RequestSubject.objects.update_or_create(
                        workflow=workflow,
                        code=subj_spec['code'],
                        defaults={
                            'name': subj_spec['name'],
                            'is_active': subj_spec.get('is_active', True),
                            'order': subj_spec.get('order', 0),
                        },
                    )
                    subject_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. Groups: {len(groups)}, Workflows: {workflow_count}, "
            f"Steps: {step_count}, Subjects: {subject_count}."
        ))
