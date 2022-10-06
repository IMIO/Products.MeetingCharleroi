Products.MeetingCharleroi Changelog
===================================

4.2.0a1 (2022-10-06)
--------------------

- Compatible for PloneMeeting 4.2.
  [aduchene]
- Removed specific `charleroi_add_refadmin` WFA and use itemWFValidationLevels instead.
  [aduchene]
- Use a custom schema policy to add attributes on Meeting's schema (DX).
  [aduchene]

4.1.7 (2020-10-30)
------------------

- Removed `CustomCharleroiMeeting.getPrintableItemsByCategory`,
  use same method from parent `CustomMeeting` (`MeetingCommunes`).
  [gbastien]

4.1.6 (2020-08-21)
------------------

- Adapted code and tests regarding DX meetingcategory.
  [gbastien]
- Adapted templates regarding last changes in Products.PloneMeeting.
  [gbastien]
- Disabled POD template in zcharleroi profile for now as is it broken.
  [gbastien]

4.1.5 (2020-06-24)
------------------

- Adapted `meetingitem_view.pt` regarding changes in `Products.PloneMeeting` (`groupsInCharge`).
  [gbastien]

4.1.4 (2020-05-08)
------------------

- Removed field `MeetingItem.itemIsSigned` from `meetingitem_edit`, it is managed thru the `meetingitem_view`

4.1.3 (2020-04-29)
------------------

- Fixed `CustomCharleroiMeetingConfig.extraInsertingMethods` returned format that was breaking the `@@display-inserting-methods-helper-msg` view.

4.1.2 (2020-03-12)
------------------

- Removed useless CSS definition for state-proposed_to_refadmin label.
- Adapted templates regarding changes in PloneMeeting, removed ToolPloneMeeting.modelAdaptations functionnality.
- Fixed item template regarding field 'proposingGroupWithGroupInCharge' that may be empty on an item template.
- Adapted Page templates regarding changes in PloneMeeting.
- Removed accepted_and_returned prettylink icon as corresponding item WF state was removed.
- Override adaptatable method MeetingItem.getAdviceRelatedIndexes to include index 'financesAdviceCategory' that will be reindexed when advice added/modified/removed.

4.1.1 (2019-10-14)
------------------

- Updated templates regarding changes in Products.PloneMeeting.

4.1 (2019-10-04)
----------------

- Fix showFinancesAdvice when the item is in state prevalidated_waiting_advices and the user has the right to print it in deliberation.

4.1rc6 (2019-09-23)
-------------------

- MeetingItem.listOptionalAdvisers was removed and replaced by a vocabulary factory, adapted code accordingly
- Implement MeetingItem._adviceIsAddable so it is not addable while item is not complete, this way the 'search items to control completeness of' works as expected
- MeetingConfig.onMeetingTransitionItemTransitionToTrigger was moved to MeetingConfig.onMeetingTransitionItemActionToExecute, adapted code accordingly
- Updated meetingitem_view.pt regarding changes in Products.PloneMeeting ase meetingitem_view.pt

4.1rc5 (2019-07-02)
-------------------

- Use Products.MeetingCommunes.config.FINANCE_WAITING_ADVICES_STATES constant instead new FINANCE_GIVEABLE_ADVICE_STATES
  Redefine MeetingCommunes.config constants after PloneMeeting.config constants as PloneMeeting.config is imported in MeetingCommunes.config,
  all this should be done in registry stored values to avoid monkeypatches problems...

4.1rc4 (2019-06-28)
-------------------

- Adapted regarding MeetingItem.groupInCharge moved to MeetingItem.groupsInCharge
- Removed import_step calling setuphandlers.updateRoleMappings

4.1rc3 (2019-06-18)
-------------------

- Fix document generation specific methods

4.1rc2 (2019-06-14)
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
