# -*- coding: utf-8 -*-
#
# File: pm_updates.py
#
# Copyright (c) 2019 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.PloneMeeting.config import registerClasses
from Products.PloneMeeting.Meeting import Meeting
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.MeetingItem import MeetingItem


def update_item_schema(baseSchema):
    specificSchema = Schema(
        (
            TextField(
                name="bourgmestreObservations",
                widget=RichWidget(
                    label_msgid="PloneMeeting_bourgmestreObservations",
                    description_msgid="bourgmestre_observations_descr",
                    condition="python: here.attribute_is_used('bourgmestreObservations')",
                    rows=20,
                    label="BourgmestreObservations",
                    i18n_domain="PloneMeeting",
                ),
                default_content_type="text/html",
                read_permission="PloneMeeting: Write item MeetingManager reserved fields",
                searchable=False,
                allowable_content_types=("text/html",),
                default_output_type="text/x-html-safe",
                optional=True,
                write_permission="PloneMeeting: Write item MeetingManager reserved fields",
            ),
        ),
    )

    completeItemSchema = baseSchema + specificSchema.copy()
    return completeItemSchema


MeetingItem.schema = update_item_schema(MeetingItem.schema)


def update_meeting_schema(baseSchema):

    specificSchema = Schema(
        (
            TextField(
                name="assemblyPolice",
                allowable_content_types="text/plain",
                optional=True,
                widget=TextAreaWidget(
                    condition="python: 'assemblyPolice' in here.shownAssemblyFields()",
                    label="Assemblypolice",
                    label_msgid="meeting_assemblyPolice",
                    i18n_domain="PloneMeeting",
                ),
                default_output_type="text/html",
                default_method="getDefaultAssemblyPolice",
                default_content_type="text/plain",
            ),
            TextField(
                name="assemblyPrivacySecretAbsents",
                allowable_content_types="text/plain",
                optional=True,
                widget=TextAreaWidget(
                    condition="python: 'assemblyPrivacySecretAbsents' in here.shownAssemblyFields()",
                    label="Assemblyprivacysecretabsents",
                    label_msgid="PloneMeeting_label_assemblyPrivacySecretAbsents",
                    i18n_domain="PloneMeeting",
                ),
                default_output_type="text/html",
                default_content_type="text/plain",
            ),
        ),
    )

    completeMeetingSchema = baseSchema + specificSchema.copy()
    return completeMeetingSchema


Meeting.schema = update_meeting_schema(Meeting.schema)


def update_config_schema(baseSchema):
    specificSchema = Schema(
        (
            TextField(
                name="assemblyPolice",
                allowable_content_types=("text/plain",),
                widget=TextAreaWidget(
                    description="AssemblyPolice",
                    description_msgid="assembly_police_descr",
                    label="AssemblyPolice",
                    label_msgid="PloneMeeting_label_assemblyPolice",
                    i18n_domain="PloneMeeting",
                ),
                default_content_type="text/plain",
                schemata="assembly_and_signatures",
                write_permission="PloneMeeting: Write harmless config",
            ),
        ),
    )

    completeConfigSchema = baseSchema + specificSchema.copy()
    completeConfigSchema.moveField("assemblyPolice", after="assemblyStaves")
    return completeConfigSchema


MeetingConfig.schema = update_config_schema(MeetingConfig.schema)

registerClasses()
