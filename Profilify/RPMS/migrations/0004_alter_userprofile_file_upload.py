# Generated by Django 5.0.2 on 2024-02-22 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RPMS', '0003_remove_userprofile_profile_picture_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='file_upload',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
    ]
