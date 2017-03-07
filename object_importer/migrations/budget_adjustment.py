from ._base import BaseMigration


class Migration(BaseMigration):
    constraints = ['campaign']

    fields = [
        'adjustment_type',
        'amount',
        'campaign_id',
        'created_date',
        'notes',
        'pre_adjustment_budget',
        'updated_date'
    ]

    fields_to_overwrite = ['created_date', 'updated_date']
