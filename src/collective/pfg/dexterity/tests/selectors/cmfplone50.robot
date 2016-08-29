*** Settings ***

Library  Selenium2Library

*** Variables ***

${ACTION_MENU_HEADER}  > a
${ACTION_MENU_CONTENT}  ul a

${MODAL_BUTTONS_DELETE}  css=.pattern-modal-buttons #form-buttons-Delete

${FORM_FIELDS_TITLE}  css=#form-widgets-IDublinCore-title
${FORM_BUTTONS_SAVE}  css=#form-buttons-save

*** Keywords ***

Select target folder
    Input text  css=.select2-input  Tracker
    Wait until page contains element
    ...  css=.pattern-relateditems.contenttype-folder
    Click element
    ...  css=.pattern-relateditems.contenttype-folder
