# Generated by Django 4.2.14 on 2024-08-10 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("licenses", "0007_remove_order_product_order_cart_order_trackid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="amount",
            field=models.DecimalField(decimal_places=2, max_digits=40),
        ),
    ]
