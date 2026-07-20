from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invest', '0016_performanceprivatefundbalance_business_date_str'),
    ]

    operations = [
        # 1. Rename ICLicense model to Marketing
        migrations.RenameModel(
            old_name='ICLicense',
            new_name='Marketing',
        ),
        # 2. Rename field IC_license to license_code in Marketing
        migrations.RenameField(
            model_name='marketing',
            old_name='IC_license',
            new_name='license_code',
        ),
        # 3. Update verbose names for Marketing
        migrations.AlterModelOptions(
            name='marketing',
            options={'verbose_name': 'Marketing', 'verbose_name_plural': 'Marketing Team'},
        ),
        # 4. Rename IC_license field in InvestorAccount to marketing
        migrations.RenameField(
            model_name='investoraccount',
            old_name='IC_license',
            new_name='marketing',
        ),
        # 5. Rename IC_license field in PrivateFundAccount to marketing
        migrations.RenameField(
            model_name='privatefundaccount',
            old_name='IC_license',
            new_name='marketing',
        ),
        # 6. Rename iCLicense field in MFTransaction to marketingCode
        migrations.RenameField(
            model_name='mftransaction',
            old_name='iCLicense',
            new_name='marketingCode',
        ),
        # 7. Alter marketingCode to be nullable
        migrations.AlterField(
            model_name='mftransaction',
            name='marketingCode',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        # 8. Update Unique Together for Marketing
        migrations.AlterUniqueTogether(
            name='marketing',
            unique_together={('compCode', 'license_code')},
        ),
    ]
