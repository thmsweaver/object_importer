from ._base import BaseMigration


class Migration(BaseMigration):
    fields = [
        'account_id',
        'brand_id',
        'display_name',
        'extra_data',
        'id',  # incremented and should not conflict
        'platform',
        'timezone_name'
    ]

    def should_skip_import(self, row_dict):
        return row_dict.get('platform') != 'SNAPCHAT'
