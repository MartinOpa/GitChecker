# Generated by Django 4.2.8 on 2024-04-14 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(verbose_name='commit timestamp')),
                ('commit_message', models.TextField()),
                ('commit_url', models.CharField(max_length=300)),
                ('hash', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repo_id', models.BigIntegerField()),
                ('repo_name', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=300)),
                ('test_dir', models.TextField(default='testFolder')),
                ('test_command', models.TextField(default='test_script.py')),
            ],
        ),
        migrations.CreateModel(
            name='TestParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('version', models.CharField(default='python3.10', max_length=16)),
                ('param_name', models.CharField(max_length=100, unique=True)),
                ('parameters', models.JSONField(blank=True, default=dict, null=True)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GitChecker.repository')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='test timestamp')),
                ('summary', models.JSONField(default=dict)),
                ('detailed', models.JSONField(default=dict)),
                ('commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GitChecker.commit')),
                ('params', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='GitChecker.testparameters')),
            ],
        ),
        migrations.AddField(
            model_name='commit',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GitChecker.repository'),
        ),
    ]
