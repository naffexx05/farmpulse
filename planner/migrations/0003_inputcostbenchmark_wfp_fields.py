from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_add_input_cost_ledger'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputcostbenchmark',
            name='data_source',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('manual',  'Manual / Seeded'),
                    ('wfp_vam', 'WFP VAM Data Bridges'),
                    ('admarc',  'ADMARC Bulletin'),
                ],
                default='manual',
                help_text='Origin of this price record',
            ),
        ),
        migrations.AddField(
            model_name='inputcostbenchmark',
            name='last_synced_at',
            field=models.DateTimeField(
                null=True, blank=True,
                help_text='When this price was last fetched from an external source',
            ),
        ),
    ]

