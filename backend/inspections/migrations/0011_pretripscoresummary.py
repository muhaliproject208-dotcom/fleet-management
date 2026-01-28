# Generated migration for PreTripScoreSummary model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0010_add_scoring_and_rest_clearance'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreTripScoreSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('health_fitness_score', models.IntegerField(default=0, help_text='Health & Fitness section score')),
                ('health_fitness_max', models.IntegerField(default=530, help_text='Max possible Health & Fitness score')),
                ('documentation_score', models.IntegerField(default=0, help_text='Documentation section score')),
                ('documentation_max', models.IntegerField(default=455, help_text='Max possible Documentation score')),
                ('vehicle_exterior_score', models.IntegerField(default=0, help_text='Vehicle Exterior checks score')),
                ('vehicle_exterior_max', models.IntegerField(default=240, help_text='Max possible Exterior score')),
                ('engine_fluid_score', models.IntegerField(default=0, help_text='Engine & Fluid checks score')),
                ('engine_fluid_max', models.IntegerField(default=220, help_text='Max possible Engine/Fluid score')),
                ('interior_cabin_score', models.IntegerField(default=0, help_text='Interior & Cabin checks score')),
                ('interior_cabin_max', models.IntegerField(default=185, help_text='Max possible Interior score')),
                ('functional_score', models.IntegerField(default=0, help_text='Functional checks score')),
                ('functional_max', models.IntegerField(default=165, help_text='Max possible Functional score')),
                ('safety_equipment_score', models.IntegerField(default=0, help_text='Safety Equipment checks score')),
                ('safety_equipment_max', models.IntegerField(default=135, help_text='Max possible Safety score')),
                ('total_score', models.IntegerField(default=0, help_text='Total pre-trip checklist score')),
                ('max_possible_score', models.IntegerField(default=1930, help_text='Maximum possible total score')),
                ('score_percentage', models.DecimalField(decimal_places=2, default=0, help_text='Overall score percentage', max_digits=5)),
                ('score_level', models.CharField(choices=[('excellent', 'Excellent (90-100%)'), ('good', 'Good (75-89%)'), ('fair', 'Fair (60-74%)'), ('poor', 'Poor (Below 60%)')], default='poor', help_text='Overall score level', max_length=15)),
                ('critical_failures', models.JSONField(blank=True, default=list, help_text='List of critical check failures')),
                ('has_critical_failures', models.BooleanField(default=False, help_text='Whether any critical checks failed')),
                ('is_cleared_for_travel', models.BooleanField(default=False, help_text='Overall travel clearance status')),
                ('clearance_notes', models.TextField(blank=True, help_text='Notes about clearance decision')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('inspection', models.OneToOneField(help_text='Associated pre-trip inspection', on_delete=django.db.models.deletion.CASCADE, related_name='pre_trip_score', to='inspections.pretripinspection')),
            ],
            options={
                'verbose_name': 'Pre-Trip Score Summary',
                'verbose_name_plural': 'Pre-Trip Score Summaries',
                'ordering': ['-created_at'],
            },
        ),
    ]
