Products.MeetingCharleroi Changelog
===================================

4.1rc2 (unreleased)
-------------------

- Updated meetingitem_view to call mayQuickEdit('completeness') with bypassWritePermissionCheck=True
- Avoid migration to 4.1 launched 2 times because of upgradeAll, added 'Products.MeetingCharleroi:default' to extra_omitted

4.1rc1 (2019-06-11)
-------------------

- Be defensive when using getProperty on a member object, do not fail if member is None
- Category 'indeterminee' can not be used on MeetingItemCollege if not to send to 'meting-config-council'
- Added possibility to send and item that is 'prevalidated' back to 'proposed' and 'itemcreated'
- Only a real Manager may backTo_prevalidated_from_waiting_advices
- Adapted finances advice to work with dexterity.localrolesfield
- Use AdviceAfterTransitionEvent instead AdviceTransitionEvent

4.0 (2017-08-22)
----------------
- Added email notification to the MeetingReviewer when an item is validated
  automatically because the freshly signed finances advice was positive
- Added 'Finances category' faceted widget only displayed to (Meeting)Managers
  and finances advisers
- Added custom inserting order 'on_police_then_other_groups_then_communications'
- Rely on inserting order 'on_groups_in_charge'
- Added listType 'depose'
- Use WFAdaptation 'mark_not_applicable'
