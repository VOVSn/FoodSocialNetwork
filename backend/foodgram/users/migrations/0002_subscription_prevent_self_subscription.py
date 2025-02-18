# Generated by Django 4.2 on 2025-02-16 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(check=models.Q(('subscriber', models.F('author')), _negated=True), name='prevent_self_subscription'),
        ),
    ]
