from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="finproduct",
            name="join_way",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="finproduct",
            name="join_member",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="finproduct",
            name="join_deny",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="finproduct",
            name="etc_note",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="finproduct",
            name="spcl_cnd",
            field=models.TextField(blank=True),
        ),
    ]
