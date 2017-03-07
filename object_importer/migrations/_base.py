from django.db import connections
from django.db.utils import ConnectionDoesNotExist


class BaseMigration(object):
    # this should be a list of `table_name`
    connection = 'foo'
    constraints = []
    fields = []
    fields_to_overwrite = []
    model_class = ''
    # TODO: this should actually just be name of class
    # which should also correspond to name of Django model
    table_name = ''

    def _row_transformer(self, row_dict):
        return row_dict

    def _overwrite_fields(self, obj, row_dict):
        """Overwrite any fields on the committed model.

        This is useful for retaining original `auto_` field values.
        """
        for field_name in self.fields_to_overwrite:
            setattr(obj, field_name, row_dict[field_name])

        try:
            obj.save()
        except Exception as e:
            print e.detail
            raise

    def merge_impl(self, row_dict):
        """Commit and return the object."""
        obj = self.model_class(**row_dict)

        try:
            obj.save()
        except Exception as e:
            print e.detail
            raise

        if self.fields_to_overwrite:
            self._overwrite_fields(obj, row_dict)

        return obj

    def merge(self, implementation):
        """Connect cursor to provided database, execute SQL, import objects.
        Args:
            fields (list): the list of fields to import
            table (str): the name of the table to query
            model_class (class): the class of the model to commit to the database
        Keyword Args:
            row_transformer (function): alter row data before committing
            merge_impl (function): handle committing row data to database
            options (dict of str: list): Overwrite any fields on
                the committed model, primarily used to retain original `auto_`
                field values
        """

        # TODO: mark node as imported

        cursor = setup_cursor()
        if cursor is None:
            return

        sql = (
            'SELECT {fields} FROM advisor_service_{table}'
            .format(fields=', '.join(fields), table=table)
        )
        print 'Executing SQL: (%s)' % sql
        count = cursor.execute(sql)
        print 'Fetched {count} {table}(s)...'.format(count=count, table=table)
        print '\n'

        if not merge_impl:
            def merge_impl(row_dict, model_class):
                """Simply commit and return the object, nothing fancy..."""
                obj = model_class(**row_dict)
                try:
                    obj.save()
                except Exception as e:
                    print e
                    import pdb; pdb.set_trace()  # noqa
                return obj

            merge_impl = merge_impl

        for row in cursor.fetchall():
            row_dict = dict(zip(fields, row))

            print 'fetched {table} with {id}'.format(
                table=table, id=row_dict.get('id'))

            if maybe_skip_import and maybe_skip_import(row_dict):
                print 'skipping'
                continue

            # maybe alter the row data before committing
            if row_transformer:
                row_transformer(row_dict)

            # commit the object to the database
            try:
                obj = merge_impl(row_dict, model_class)
            except Exception as e:
                print e
                import pdb; pdb.set_trace()  # noqa

            # maybe overwrite any fields and save (primarily `auto_` fields)
            if options.get('fields_to_overwrite'):
                for field_name in options.get('fields_to_overwrite', []):
                    setattr(obj, field_name, row_dict[field_name])

                try:
                    obj.save()
                except Exception as e:
                    print e
                    import pdb; pdb.set_trace()

    def setup_cursor(self):
        """Connect cursor to `snapchat` database (see settings.py)."""
        try:
            return connections[self.connection].cursor()
        except ConnectionDoesNotExist:
            print 'Snapchat Advisor database is not correctly configured'
            return None

    def should_skip_import(self, row_dict):
        """Conditionally skip importing the object."""
        return False

    # @property
    # def model_class(self):
    #     if hasattr(self, 'target_model_class', None):
    #         return self.target_model_class

    #     class_name = self.__class__.__name__
    #     model_name = class_name.replace('Import', '', 1)
    #     model_name = model_name[0]

    #     target_model_class = apps.get_model(
    #         app_label='this_project', model_name=model_name
    #     )
    #     self.target_model_class = target_model_class
    #     return target_model_class
