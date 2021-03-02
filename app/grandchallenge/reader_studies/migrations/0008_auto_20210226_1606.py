# Generated by Django 3.1.6 on 2021-02-26 16:06

from django.db import migrations, models

import grandchallenge.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("reader_studies", "0007_auto_20210201_2220"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="image_port",
            field=models.CharField(
                blank=True,
                choices=[
                    ("M", "Main"),
                    ("S", "Secondary"),
                    ("TERTIARY", "Tertiary"),
                    ("QUATERNARY", "Quaternary"),
                    ("QUINARY", "Quinary"),
                    ("SENARY", "Senary"),
                    ("SEPTENARY", "Septenary"),
                    ("OCTONARY", "Octonary"),
                    ("NONARY", "Nonary"),
                    ("DENARY", "Denary"),
                ],
                default="",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="readerstudy",
            name="hanging_list",
            field=models.JSONField(
                blank=True,
                default=list,
                validators=[
                    grandchallenge.core.validators.JSONSchemaValidator(
                        schema={
                            "$schema": "http://json-schema.org/draft-06/schema#",
                            "definitions": {},
                            "items": {
                                "$id": "#/items",
                                "additionalProperties": False,
                                "properties": {
                                    "denary": {
                                        "$id": "#/items/properties/denary",
                                        "default": "",
                                        "examples": ["im_denary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Denary Schema",
                                        "type": "string",
                                    },
                                    "denary-overlay": {
                                        "$id": "#/items/properties/denary-overlay",
                                        "default": "",
                                        "examples": ["im_denary-overlay.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Denary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "main": {
                                        "$id": "#/items/properties/main",
                                        "default": "",
                                        "examples": ["im_main.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Main Schema",
                                        "type": "string",
                                    },
                                    "main-overlay": {
                                        "$id": "#/items/properties/main-overlay",
                                        "default": "",
                                        "examples": ["im_main-overlay.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Main-Overlay Schema",
                                        "type": "string",
                                    },
                                    "nonary": {
                                        "$id": "#/items/properties/nonary",
                                        "default": "",
                                        "examples": ["im_nonary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Nonary Schema",
                                        "type": "string",
                                    },
                                    "nonary-overlay": {
                                        "$id": "#/items/properties/nonary-overlay",
                                        "default": "",
                                        "examples": ["im_nonary-overlay.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Nonary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "octonary": {
                                        "$id": "#/items/properties/octonary",
                                        "default": "",
                                        "examples": ["im_octonary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Octonary Schema",
                                        "type": "string",
                                    },
                                    "octonary-overlay": {
                                        "$id": "#/items/properties/octonary-overlay",
                                        "default": "",
                                        "examples": [
                                            "im_octonary-overlay.mhd"
                                        ],
                                        "pattern": "^(.*)$",
                                        "title": "The Octonary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "quaternary": {
                                        "$id": "#/items/properties/quaternary",
                                        "default": "",
                                        "examples": ["im_quaternary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Quaternary Schema",
                                        "type": "string",
                                    },
                                    "quaternary-overlay": {
                                        "$id": "#/items/properties/quaternary-overlay",
                                        "default": "",
                                        "examples": [
                                            "im_quaternary-overlay.mhd"
                                        ],
                                        "pattern": "^(.*)$",
                                        "title": "The Quaternary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "quinary": {
                                        "$id": "#/items/properties/quinary",
                                        "default": "",
                                        "examples": ["im_quinary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Quinary Schema",
                                        "type": "string",
                                    },
                                    "quinary-overlay": {
                                        "$id": "#/items/properties/quinary-overlay",
                                        "default": "",
                                        "examples": ["im_quinary-overlay.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Quinary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "secondary": {
                                        "$id": "#/items/properties/secondary",
                                        "default": "",
                                        "examples": ["im_secondary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Secondary Schema",
                                        "type": "string",
                                    },
                                    "secondary-overlay": {
                                        "$id": "#/items/properties/secondary-overlay",
                                        "default": "",
                                        "examples": [
                                            "im_secondary-overlay.mhd"
                                        ],
                                        "pattern": "^(.*)$",
                                        "title": "The Secondary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "senary": {
                                        "$id": "#/items/properties/senary",
                                        "default": "",
                                        "examples": ["im_senary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Senary Schema",
                                        "type": "string",
                                    },
                                    "senary-overlay": {
                                        "$id": "#/items/properties/senary-overlay",
                                        "default": "",
                                        "examples": ["im_senary-overlay.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Senary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "septenary": {
                                        "$id": "#/items/properties/septenary",
                                        "default": "",
                                        "examples": ["im_septenary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Septenary Schema",
                                        "type": "string",
                                    },
                                    "septenary-overlay": {
                                        "$id": "#/items/properties/septenary-overlay",
                                        "default": "",
                                        "examples": [
                                            "im_septenary-overlay.mhd"
                                        ],
                                        "pattern": "^(.*)$",
                                        "title": "The Septenary-Overlay Schema",
                                        "type": "string",
                                    },
                                    "tertiary": {
                                        "$id": "#/items/properties/tertiary",
                                        "default": "",
                                        "examples": ["im_tertiary.mhd"],
                                        "pattern": "^(.*)$",
                                        "title": "The Tertiary Schema",
                                        "type": "string",
                                    },
                                    "tertiary-overlay": {
                                        "$id": "#/items/properties/tertiary-overlay",
                                        "default": "",
                                        "examples": [
                                            "im_tertiary-overlay.mhd"
                                        ],
                                        "pattern": "^(.*)$",
                                        "title": "The Tertiary-Overlay Schema",
                                        "type": "string",
                                    },
                                },
                                "required": ["main"],
                                "title": "The Items Schema",
                                "type": "object",
                            },
                            "title": "The Hanging List Schema",
                            "type": "array",
                        }
                    )
                ],
            ),
        ),
    ]
