# Generated by Django 2.0 on 2018-11-19 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KeywordsInfo',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('key_type', models.IntegerField(blank=True, null=True)),
                ('object_code', models.CharField(max_length=64)),
                ('key_info', models.CharField(blank=True, max_length=64, null=True)),
                ('state', models.IntegerField(blank=True, null=True)),
                ('insert_time', models.DateTimeField(blank=True, null=True)),
                ('creater', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'keywords_info',
            },
        ),
        migrations.CreateModel(
            name='RequirementsInfo',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('req_code', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('req_name', models.CharField(blank=True, max_length=64, null=True)),
                ('req_form_type', models.IntegerField(blank=True, null=True)),
                ('r_abstract', models.TextField(blank=True, null=True)),
                ('use_type', models.IntegerField(blank=True, null=True)),
                ('cooperation_type', models.IntegerField(blank=True, null=True)),
                ('obtain_type', models.IntegerField(blank=True, null=True)),
                ('osource_name', models.CharField(blank=True, max_length=64, null=True)),
                ('obtain_source', models.CharField(blank=True, max_length=255, null=True)),
                ('entry_type', models.IntegerField(blank=True, null=True)),
                ('owner_type', models.IntegerField(blank=True, null=True)),
                ('owber_code', models.CharField(blank=True, max_length=64, null=True)),
                ('owner_abstract', models.CharField(blank=True, max_length=255, null=True)),
                ('rcoop_t_abstract', models.CharField(blank=True, max_length=255, null=True)),
                ('expiry_dateb', models.DateTimeField(blank=True, null=True)),
                ('expiry_datee', models.DateTimeField(blank=True, null=True)),
                ('original_data', models.CharField(blank=True, max_length=255, null=True)),
                ('show_state', models.IntegerField(blank=True, null=True)),
                ('sniff_state', models.IntegerField(blank=True, null=True)),
                ('sniff_time', models.DateTimeField(blank=True, null=True)),
                ('creater', models.CharField(blank=True, max_length=32, null=True)),
                ('insert_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'requirements_info',
            },
        ),
        migrations.CreateModel(
            name='ResultCheckHistory',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('apply_code', models.CharField(blank=True, max_length=64, null=True)),
                ('opinion', models.TextField(blank=True, null=True)),
                ('result', models.IntegerField(blank=True, null=True)),
                ('check_time', models.DateTimeField(blank=True, null=True)),
                ('account', models.CharField(blank=True, max_length=64, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'result_check_history',
            },
        ),
        migrations.CreateModel(
            name='ResultOwnereBaseinfo',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('ecode', models.CharField(blank=True, max_length=64, null=True)),
                ('type', models.IntegerField(blank=True, null=True)),
                ('owner_name', models.CharField(blank=True, max_length=64, null=True)),
                ('owner_tel', models.CharField(blank=True, max_length=16, null=True)),
                ('owner_mobile', models.CharField(blank=True, max_length=16, null=True)),
                ('owner_email', models.CharField(blank=True, max_length=16, null=True)),
                ('owner_license', models.CharField(blank=True, max_length=64, null=True)),
                ('owner_abstract', models.TextField(blank=True, null=True)),
                ('homepage', models.CharField(blank=True, max_length=128, null=True)),
                ('creditvalue', models.IntegerField(blank=True, null=True)),
                ('state', models.IntegerField(blank=True, null=True)),
                ('account_code', models.CharField(blank=True, max_length=64, null=True)),
                ('creater', models.CharField(blank=True, max_length=32, null=True)),
                ('insert_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'result_ownere_baseinfo',
            },
        ),
        migrations.CreateModel(
            name='ResultsCooperationTypeInfo',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('r_type', models.IntegerField(blank=True, null=True)),
                ('rr_code', models.CharField(blank=True, max_length=64, null=True)),
                ('cooperation_code', models.CharField(blank=True, max_length=64, null=True)),
                ('state', models.IntegerField(blank=True, null=True)),
                ('insert_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'results_cooperation_type_info',
            },
        ),
        migrations.CreateModel(
            name='ResultsEaInfo',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('r_code', models.CharField(blank=True, max_length=64, null=True)),
                ('account_code', models.CharField(blank=True, max_length=64, null=True)),
                ('ea_text', models.TextField(blank=True, null=True)),
                ('insert_time', models.DateTimeField(blank=True, null=True)),
                ('state', models.IntegerField(blank=True, null=True)),
                ('account', models.CharField(blank=True, max_length=64, null=True)),
                ('check_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'results_ea_info',
            },
        ),
        migrations.CreateModel(
            name='ResultsInfo',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('r_code', models.CharField(blank=True, max_length=64, null=True, unique=True)),
                ('r_name', models.CharField(blank=True, max_length=64, null=True)),
                ('r_form_type', models.IntegerField(blank=True, null=True)),
                ('r_abstract', models.TextField(blank=True, null=True)),
                ('use_type', models.IntegerField(blank=True, null=True)),
                ('obtain_type', models.IntegerField(blank=True, null=True)),
                ('osource_name', models.CharField(blank=True, max_length=64, null=True)),
                ('obtain_source', models.CharField(blank=True, max_length=255, null=True)),
                ('entry_type', models.IntegerField(blank=True, null=True)),
                ('owner_type', models.IntegerField(blank=True, null=True)),
                ('owner_abstract', models.CharField(blank=True, max_length=255, null=True)),
                ('r_coop_t_abstract', models.CharField(blank=True, max_length=255, null=True)),
                ('expiry_dateb', models.DateTimeField(blank=True, null=True)),
                ('expiry_datee', models.DateTimeField(blank=True, null=True)),
                ('rexpiry_dateb', models.DateTimeField(blank=True, null=True)),
                ('rexpiry_datee', models.DateTimeField(blank=True, null=True)),
                ('original_data', models.CharField(blank=True, max_length=255, null=True)),
                ('show_state', models.IntegerField(blank=True, null=True)),
                ('sniff_state', models.IntegerField(blank=True, null=True)),
                ('sniff_time', models.DateTimeField(blank=True, null=True)),
                ('creater', models.CharField(blank=True, max_length=32, null=True)),
                ('insert_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'results_info',
            },
        ),
        migrations.CreateModel(
            name='ResultsOwnerInfo',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('r_code', models.CharField(blank=True, max_length=64, null=True)),
                ('owner_type', models.IntegerField(blank=True, null=True)),
                ('owner_code', models.CharField(blank=True, max_length=64, null=True)),
                ('main_owner', models.IntegerField(blank=True, null=True)),
                ('state', models.IntegerField(blank=True, null=True)),
                ('insert_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'results_owner_info',
            },
        ),
        migrations.CreateModel(
            name='RrApplyHistory',
            fields=[
                ('serial', models.AutoField(primary_key=True, serialize=False)),
                ('a_code', models.CharField(blank=True, max_length=64, null=True)),
                ('rr_code', models.CharField(blank=True, max_length=64, null=True)),
                ('account_code', models.CharField(blank=True, max_length=64, null=True)),
                ('state', models.IntegerField(blank=True, null=True)),
                ('apply_time', models.DateTimeField(blank=True, null=True)),
                ('apply_type', models.IntegerField(blank=True, null=True)),
                ('type', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'rr_apply_history',
            },
        ),
    ]