# Generated by Django 4.2.14 on 2024-08-08 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("licenses", "0002_alter_customerprofile_account_number_feature"),
    ]

    operations = [
        migrations.AddField(
            model_name="product", name="features", field=models.JSONField(default=dict),
        ),
        migrations.DeleteModel(name="Feature",),
    ]
