# Generated migration for scoring system and rest clearance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0009_rename_inspections_inspect_7858fb_idx_inspections_inspection_id_idx_and_more'),
    ]

    operations = [
        # Add adequate_rest field for fatigue/rest clearance
        migrations.AddField(
            model_name='healthfitnesscheck',
            name='adequate_rest',
            field=models.BooleanField(
                blank=True,
                help_text='Has the driver rested for 8 hours or more?',
                null=True
            ),
        ),
        # Add rest_clearance_status field
        migrations.AddField(
            model_name='healthfitnesscheck',
            name='rest_clearance_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('cleared', 'Cleared for Travel'),
                    ('not_cleared', 'Not Cleared - Insufficient Rest')
                ],
                help_text='Travel clearance based on rest status',
                max_length=20
            ),
        ),
        # Add section_score field for health fitness
        migrations.AddField(
            model_name='healthfitnesscheck',
            name='section_score',
            field=models.IntegerField(
                default=0,
                help_text='Calculated score for this section (0-100)'
            ),
        ),
        # Add max_possible_score field
        migrations.AddField(
            model_name='healthfitnesscheck',
            name='max_possible_score',
            field=models.IntegerField(
                default=530,
                help_text='Maximum possible score for this section'
            ),
        ),
    ]
