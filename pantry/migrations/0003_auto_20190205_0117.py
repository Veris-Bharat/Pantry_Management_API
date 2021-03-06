# Generated by Django 2.1.5 on 2019-02-04 19:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pantry', '0002_auto_20190201_2007'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemBook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=0)),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pantry.Inventory')),
            ],
            options={
                'ordering': ('order_id',),
            },
        ),
        migrations.RemoveField(
            model_name='order',
            name='item_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.AddField(
            model_name='itembook',
            name='order_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pantry.Order'),
        ),
    ]
