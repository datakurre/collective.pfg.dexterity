*** Settings ***
Library  OperatingSystem

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Resource  ${CMFPLONE_SELECTORS}  # magic variable from p.a.robotframework

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Run keywords  Open SauceLabs test browser  Background
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test Cases ***

Form folder is addable
    [Tags]  PloneFormGen
    Given I'm logged in as a 'Site Administrator'
     When I go to the front page
     Then I can add a new form folder

Date field is supported
    [Tags]  PloneFormGen  Adapter
    Given There's a content type with a date field
      And There's a published form with a date field
      And The form has properly configured 'Content Adapter'
     When I submit the form as an 'Anonymous User'
     Then A content object is created
      And it has the date field filled

*** Keywords ***

Background
    Given 'PloneFormGen' is activated
    And 'collective.pfg.dexterity' is activated

'${product}' is activated
    Product is activated  ${product}

'${portal_type}' is installed
    Portal type is installed  ${portal_type}

Open Menu
    [Arguments]  ${elementId}
    Element Should Be Visible  css=#${elementId} span
    Element Should Not Be Visible  css=#${elementId} ${ACTION_MENU_CONTENT}
    Click link  css=#${elementId} ${ACTION_MENU_HEADER}
    Wait until keyword succeeds  1  5  Element Should Be Visible  css=#${elementId} ${ACTION_MENU_CONTENT}

Open add new menu
    Open menu  plone-contentmenu-factories

Open action menu
    Open menu  plone-contentmenu-actions

Open workflow menu
    Open menu  plone-contentmenu-workflow

There's a content type with a date field
    Create type with date field  Ticket

There's a published form with a date field
    Set window size  1280  1280
    Enable autologin as  Site Administrator
    Go to  ${PLONE_URL}

    # Add a new Form FOlder
    Open add new menu
    Click link  css=#plone-contentmenu-factories a#formfolder

    # Work around Archetypes Plone 5 bug
    ${url} =  Get location
    Go to  ${url}

    Input text  title  Send Request
    Click button  form.button.save

    # Delete 'replyto' field (included by default) from the created Form Folder
    Page should contain   Your E-Mail Address
    Go to  ${PLONE_URL}/send-request/replyto
    Open action menu
    Click link  css=a#plone-contentmenu-actions-delete
    Sleep  1s
    Log source
    Wait until page contains element  ${MODAL_BUTTONS_DELETE}
    Click button  ${MODAL_BUTTONS_DELETE}
    ${status} =  Run keyword and return status
    ...  Wait until page does not contain  Your E-Mail Address
    Run keyword if  not ${status}
    ...  Wait until page contains  Your E-Mail Address has been deleted
    Page should contain  Send Request

    # Disable mailer adapter on the form
    Go to  ${PLONE_URL}/send-request/edit
    Unselect checkbox  actionAdapter_1
    Click button  form.button.save

    # Add a date field
    Open add new menu
    Click link  css=#plone-contentmenu-factories a#formdatefield
    Input text  title  Due Date
    Click button  form.button.save

    # Publish the form
    Go to  ${PLONE_URL}/send-request
    Open workflow menu
    # Click link  css=a#workflow-transition-publish
    Go to  ${PLONE_URL}/send-request/content_status_modify?workflow_action=publish

    # Pass CSRF protection
    ${csrf} =  Run keyword and return status
    ...  Page should contain  Confirming User Action
    Run keyword if  ${csrf}
    ...  Click button  Confirm action

    Wait until page contains  Item state changed.

    Disable autologin

The form has properly configured 'Content Adapter'
    Enable autologin as  Site Administrator

    # Create a folder for 'Content Adapter' to create content into
    Go to  ${PLONE_URL}
    Open add new menu
    Click link  css=#plone-contentmenu-factories a#folder
    Input text  ${FORM_FIELDS_TITLE}  Tracker
    Click button  ${FORM_BUTTONS_SAVE}

    # Add a new content adapter into the created Form Folder
    Go to  ${PLONE_URL}/send-request
    Open add new menu
    Click link  css=#plone-contentmenu-factories a#dexterity-content-adapter
    Input text  title  Ticket machine

    # Configure it to created Ticket-types
    ${success} =  Run keyword and return status
    ...  Select radio button  createdType  Ticket
    Run keyword if  not ${success}
    ...  Select from list  createdType  Ticket
    Select target folder
    Click button  form.button.save

    # Map form fields to Ticket-content one field at time
    Go to  ${PLONE_URL}/send-request/ticket-machine/edit

    Click link  Add new row
    Click link  Add new row
    Click link  Add new row

    Select from list  css=select#form_fieldMapping_0  topic
    Select from list  css=select#content_fieldMapping_0  title

    Select from list  css=select#form_fieldMapping_1  comments
    Select from list  css=select#content_fieldMapping_1  description

    Select from list  css=select#form_fieldMapping_2  due-date
    Select from list  css=select#content_fieldMapping_2  duedate

    # Configure adapter to submit the created content
    Select radio button  workflowTransition  submit
    Click button  form.button.save

    # Enable content creation magic (requires real owner with enough rights)
    Change ownership  send-request/ticket-machine  admin

    Disable autologin

I submit the form as an 'Anonymous User'
    Go to  ${PLONE_URL}/send-request

    Input text  topic  A ticket
    Input text  comments  Something important
    Select from list  due-date_year  2013
    Select from list  due-date_month  01
    Select from list  due-date_day  01

    Click button  form_submit
    Capture page screenshot

A content object is created
    Enable autologin as  Site Administrator
    Go to  ${PLONE_URL}/tracker
    Capture page screenshot
    Disable autologin

It has the date field filled
    Enable autologin as  Site Administrator
    Go to  ${PLONE_URL}/tracker/ticket
    ${status} =  Run keyword and return status
    ...  Element text should be  css=.date-field#form-widgets-duedate  1/1/13
    Run keyword if  not ${status}
    ...  Element should contain  css=#formfield-form-widgets-duedate  1/1/13
    Disable autologin

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}
    Go to  ${PLONE_URL}

I go to the front page
    Go to  ${PLONE_URL}

I can add a new form folder
    Open add new menu
    Click link  css=#plone-contentmenu-factories a#formfolder

    # Work around Archetypes Plone 5 bug
    ${url} =  Get location
    Go to  ${url}

    Input text  title  A sample form folder
    Click button  form.button.save
