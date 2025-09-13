from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BasicColumnData",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.IntegerField(null=True)),
                ("updated", models.IntegerField(null=True)),
                ("cc_calculated_pct", models.IntegerField(null=True)),
                ("dbn", models.CharField(max_length=10, null=True)),
                ("school_name", models.CharField(max_length=128, null=True)),
                ("num_of_sat_test_takers", models.IntegerField(null=True)),
                ("sat_critical_reading_avg_score", models.IntegerField(null=True)),
                ("sat_math_avg_score", models.IntegerField(null=True)),
                ("sat_writing_avg_score", models.IntegerField(null=True)),
                ("tag_with_null_value", models.CharField(max_length=50, null=True)),
                ("total_score", models.FloatField(null=True)),
                ("zip_code", models.IntegerField(null=True)),
                ("_ack1", models.IntegerField(null=True)),
                ("_ack2", models.IntegerField(null=True)),
                ("_ack3", models.IntegerField(null=True)),
                ("_ack4", models.IntegerField(null=True)),
                ("cc_amount___total", models.IntegerField(null=True)),
                ("foo_bar", models.IntegerField(null=True)),
            ],
        ),
    ]
