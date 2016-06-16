from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import Schema
from Products.PloneMeeting.Meeting import Meeting


def update_meeting_schema(baseSchema):

    specificSchema = Schema((
        TextField(
            name='assemblyPolice',
            allowable_content_types="text/plain",
            optional=True,
            widget=TextAreaWidget(
                condition="python: here.attributeIsUsed('assemblyPolice')",
                label='Assemblypolice',
                label_msgid='PloneMeeting_label_assemblyPolice',
                i18n_domain='PloneMeeting',
            ),
            default_output_type="text/html",
            default_content_type="text/plain",
        ),
    ),)

    completeConfigSchema = baseSchema + specificSchema.copy()
    return completeConfigSchema
Meeting.schema = update_meeting_schema(Meeting.schema)

# Classes have already been registered, but we register them again here
# because we have potentially applied some schema adaptations (see above).
# Class registering includes generation of accessors and mutators, for
# example, so this is why we need to do it again now.
from Products.PloneMeeting.config import registerClasses
registerClasses()
