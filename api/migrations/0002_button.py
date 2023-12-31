# Generated by Django 4.2.2 on 2023-06-20 23:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Button',
            fields=[
                ('basemodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.basemodel')),
                ('text', models.CharField(max_length=50)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buttons', to='api.content')),
            ],
            bases=('api.basemodel',),
        ),
    ]
