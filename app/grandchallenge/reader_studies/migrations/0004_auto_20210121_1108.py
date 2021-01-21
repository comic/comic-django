# Generated by Django 3.1.1 on 2021-01-21 11:08

from django.db import migrations, models
import grandchallenge.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reader_studies', '0003_readerstudy_organizations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer',
            field=models.JSONField(null=True, validators=[grandchallenge.core.validators.JSONSchemaValidator(schema={'$schema': 'http://json-schema.org/draft-07/schema#', 'anyOf': [{'$ref': '#/definitions/null'}, {'$ref': '#/definitions/STXT'}, {'$ref': '#/definitions/MTXT'}, {'$ref': '#/definitions/BOOL'}, {'$ref': '#/definitions/NUMB'}, {'$ref': '#/definitions/HEAD'}, {'$ref': '#/definitions/2DBB'}, {'$ref': '#/definitions/DIST'}, {'$ref': '#/definitions/MDIS'}, {'$ref': '#/definitions/POIN'}, {'$ref': '#/definitions/MPOI'}, {'$ref': '#/definitions/POLY'}, {'$ref': '#/definitions/MPOL'}, {'$ref': '#/definitions/CHOI'}, {'$ref': '#/definitions/MCHO'}, {'$ref': '#/definitions/MCHD'}, {'$ref': '#/definitions/M2DB'}], 'definitions': {'2D-bounding-box-object': {'properties': {'corners': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'maxItems': 4, 'minItems': 4, 'type': 'array'}, 'name': {'type': 'string'}}, 'required': ['corners'], 'type': 'object'}, '2DBB': {'properties': {'corners': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'maxItems': 4, 'minItems': 4, 'type': 'array'}, 'name': {'type': 'string'}, 'type': {'enum': ['2D bounding box']}}, 'required': ['version', 'type', 'corners'], 'type': 'object'}, 'BOOL': {'type': 'boolean'}, 'CHOI': {'type': 'number'}, 'DIST': {'properties': {'end': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'name': {'type': 'string'}, 'start': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': {'enum': ['Distance measurement']}}, 'required': ['version', 'type', 'start', 'end'], 'type': 'object'}, 'HEAD': {'type': 'null'}, 'M2DB': {'properties': {'boxes': {'items': {'allOf': [{'$ref': '#/definitions/2D-bounding-box-object'}]}, 'type': 'array'}, 'name': {'type': 'string'}, 'type': {'enum': ['Multiple 2D bounding boxes']}}, 'required': ['version', 'type', 'boxes'], 'type': 'object'}, 'MCHD': {'items': {'type': 'number'}, 'type': 'array'}, 'MCHO': {'items': {'type': 'number'}, 'type': 'array'}, 'MDIS': {'properties': {'lines': {'items': {'allOf': [{'$ref': '#/definitions/line-object'}]}, 'type': 'array'}, 'name': {'type': 'string'}, 'type': {'enum': ['Multiple distance measurements']}}, 'required': ['version', 'type', 'lines'], 'type': 'object'}, 'MPOI': {'properties': {'name': {'type': 'string'}, 'points': {'items': {'allOf': [{'$ref': '#/definitions/point-object'}]}, 'type': 'array'}, 'type': {'enum': ['Multiple points']}}, 'required': ['version', 'type', 'points'], 'type': 'object'}, 'MPOL': {'properties': {'name': {'type': 'string'}, 'polygons': {'items': {'$ref': '#/definitions/polygon-object'}, 'type': 'array'}, 'type': {'enum': ['Multiple polygons']}}, 'required': ['type', 'version', 'polygons'], 'type': 'object'}, 'MTXT': {'type': 'string'}, 'NUMB': {'type': 'number'}, 'POIN': {'properties': {'name': {'type': 'string'}, 'point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': {'enum': ['Point']}}, 'required': ['version', 'type', 'point'], 'type': 'object'}, 'POLY': {'properties': {'groups': {'items': {'type': 'string'}, 'type': 'array'}, 'name': {'type': 'string'}, 'path_points': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': 'array'}, 'seed_point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'sub_type': {'type': 'string'}}, 'required': ['name', 'seed_point', 'path_points', 'sub_type', 'groups', 'version'], 'type': 'object'}, 'STXT': {'type': 'string'}, 'line-object': {'properties': {'end': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'name': {'type': 'string'}, 'start': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}}, 'required': ['start', 'end'], 'type': 'object'}, 'null': {'type': 'null'}, 'point-object': {'properties': {'name': {'type': 'string'}, 'point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}}, 'required': ['point'], 'type': 'object'}, 'polygon-object': {'properties': {'groups': {'items': {'type': 'string'}, 'type': 'array'}, 'name': {'type': 'string'}, 'path_points': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': 'array'}, 'seed_point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'sub_type': {'type': 'string'}}, 'required': ['name', 'seed_point', 'path_points', 'sub_type', 'groups'], 'type': 'object'}}, 'properties': {'version': {'additionalProperties': {'type': 'number'}, 'required': ['major', 'minor'], 'type': 'object'}}})]),
        ),
        migrations.AlterField(
            model_name='historicalanswer',
            name='answer',
            field=models.JSONField(null=True, validators=[grandchallenge.core.validators.JSONSchemaValidator(schema={'$schema': 'http://json-schema.org/draft-07/schema#', 'anyOf': [{'$ref': '#/definitions/null'}, {'$ref': '#/definitions/STXT'}, {'$ref': '#/definitions/MTXT'}, {'$ref': '#/definitions/BOOL'}, {'$ref': '#/definitions/NUMB'}, {'$ref': '#/definitions/HEAD'}, {'$ref': '#/definitions/2DBB'}, {'$ref': '#/definitions/DIST'}, {'$ref': '#/definitions/MDIS'}, {'$ref': '#/definitions/POIN'}, {'$ref': '#/definitions/MPOI'}, {'$ref': '#/definitions/POLY'}, {'$ref': '#/definitions/MPOL'}, {'$ref': '#/definitions/CHOI'}, {'$ref': '#/definitions/MCHO'}, {'$ref': '#/definitions/MCHD'}, {'$ref': '#/definitions/M2DB'}], 'definitions': {'2D-bounding-box-object': {'properties': {'corners': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'maxItems': 4, 'minItems': 4, 'type': 'array'}, 'name': {'type': 'string'}}, 'required': ['corners'], 'type': 'object'}, '2DBB': {'properties': {'corners': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'maxItems': 4, 'minItems': 4, 'type': 'array'}, 'name': {'type': 'string'}, 'type': {'enum': ['2D bounding box']}}, 'required': ['version', 'type', 'corners'], 'type': 'object'}, 'BOOL': {'type': 'boolean'}, 'CHOI': {'type': 'number'}, 'DIST': {'properties': {'end': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'name': {'type': 'string'}, 'start': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': {'enum': ['Distance measurement']}}, 'required': ['version', 'type', 'start', 'end'], 'type': 'object'}, 'HEAD': {'type': 'null'}, 'M2DB': {'properties': {'boxes': {'items': {'allOf': [{'$ref': '#/definitions/2D-bounding-box-object'}]}, 'type': 'array'}, 'name': {'type': 'string'}, 'type': {'enum': ['Multiple 2D bounding boxes']}}, 'required': ['version', 'type', 'boxes'], 'type': 'object'}, 'MCHD': {'items': {'type': 'number'}, 'type': 'array'}, 'MCHO': {'items': {'type': 'number'}, 'type': 'array'}, 'MDIS': {'properties': {'lines': {'items': {'allOf': [{'$ref': '#/definitions/line-object'}]}, 'type': 'array'}, 'name': {'type': 'string'}, 'type': {'enum': ['Multiple distance measurements']}}, 'required': ['version', 'type', 'lines'], 'type': 'object'}, 'MPOI': {'properties': {'name': {'type': 'string'}, 'points': {'items': {'allOf': [{'$ref': '#/definitions/point-object'}]}, 'type': 'array'}, 'type': {'enum': ['Multiple points']}}, 'required': ['version', 'type', 'points'], 'type': 'object'}, 'MPOL': {'properties': {'name': {'type': 'string'}, 'polygons': {'items': {'$ref': '#/definitions/polygon-object'}, 'type': 'array'}, 'type': {'enum': ['Multiple polygons']}}, 'required': ['type', 'version', 'polygons'], 'type': 'object'}, 'MTXT': {'type': 'string'}, 'NUMB': {'type': 'number'}, 'POIN': {'properties': {'name': {'type': 'string'}, 'point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': {'enum': ['Point']}}, 'required': ['version', 'type', 'point'], 'type': 'object'}, 'POLY': {'properties': {'groups': {'items': {'type': 'string'}, 'type': 'array'}, 'name': {'type': 'string'}, 'path_points': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': 'array'}, 'seed_point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'sub_type': {'type': 'string'}}, 'required': ['name', 'seed_point', 'path_points', 'sub_type', 'groups', 'version'], 'type': 'object'}, 'STXT': {'type': 'string'}, 'line-object': {'properties': {'end': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'name': {'type': 'string'}, 'start': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}}, 'required': ['start', 'end'], 'type': 'object'}, 'null': {'type': 'null'}, 'point-object': {'properties': {'name': {'type': 'string'}, 'point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}}, 'required': ['point'], 'type': 'object'}, 'polygon-object': {'properties': {'groups': {'items': {'type': 'string'}, 'type': 'array'}, 'name': {'type': 'string'}, 'path_points': {'items': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'type': 'array'}, 'seed_point': {'items': {'type': 'number'}, 'maxItems': 3, 'minItems': 3, 'type': 'array'}, 'sub_type': {'type': 'string'}}, 'required': ['name', 'seed_point', 'path_points', 'sub_type', 'groups'], 'type': 'object'}}, 'properties': {'version': {'additionalProperties': {'type': 'number'}, 'required': ['major', 'minor'], 'type': 'object'}}})]),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer_type',
            field=models.CharField(choices=[('STXT', 'Single line text'), ('MTXT', 'Multi line text'), ('BOOL', 'Bool'), ('NUMB', 'Number'), ('HEAD', 'Heading'), ('2DBB', '2D bounding box'), ('M2DB', 'Multiple 2D bounding boxes'), ('DIST', 'Distance measurement'), ('MDIS', 'Multiple distance measurements'), ('POIN', 'Point'), ('MPOI', 'Multiple points'), ('POLY', 'Polygon'), ('MPOL', 'Multiple polygons'), ('CHOI', 'Choice'), ('MCHO', 'Multiple choice'), ('MCHD', 'Multiple choice dropdown')], default='STXT', max_length=4),
        ),
    ]
