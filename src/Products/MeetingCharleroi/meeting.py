from Products.CMFPlone.utils import safe_unicode
from Products.PloneMeeting.content.meeting import IMeeting, assembly_constraint, Meeting
from Products.PloneMeeting.interfaces import IDXMeetingContent
from Products.PloneMeeting.widgets.pm_textarea import PMTextAreaFieldWidget
from plone import api
from plone.app.textfield import RichText
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.directives import form
from Products.PloneMeeting.config import PMMessageFactory as _
from plone.supermodel import model


class IMeetingCustomCharleroi(IDXMeetingContent):
    """ """

    form.order_before(assembly_police="signatures")
    form.widget("assembly_police", PMTextAreaFieldWidget)
    assembly_police = RichText(
        title=_("title_assembly_police"),
        default_mime_type="text/plain",
        allowed_mime_types=("text/plain",),
        output_mime_type="text/x-html-safe",
        constraint=assembly_constraint,
        required=False,
    )

    form.order_after(assembly_privacy_secret_absents="assembly_police")
    form.widget("assembly_privacy_secret_absents", PMTextAreaFieldWidget)
    assembly_privacy_secret_absents = RichText(
        title=_("title_assembly_privacy_secret_absents"),
        default_mime_type="text/plain",
        allowed_mime_types=("text/plain",),
        output_mime_type="text/x-html-safe",
        constraint=assembly_constraint,
        required=False,
    )

    model.fieldset(
        "assembly",
        label=_("fieldset_assembly"),
        fields=["assembly_police", "assembly_privacy_secret_absents"],
    )


Meeting.FIELD_INFOS["assembly_police"] = {"optional": True, "condition": ""}
Meeting.FIELD_INFOS["assembly_privacy_secret_absents"] = {"optional": True, "condition": ""}


@form.default_value(field=IMeetingCustomCharleroi["assembly_police"])
def default_assembly_police(data):
    tool = api.portal.get_tool("portal_plonemeeting")
    cfg = tool.getMeetingConfig(data.context)
    res = safe_unicode(cfg.getAssemblyPolice())
    return res


class CustomCharleroiMeetingSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IMeeting, IMeetingCustomCharleroi,)
