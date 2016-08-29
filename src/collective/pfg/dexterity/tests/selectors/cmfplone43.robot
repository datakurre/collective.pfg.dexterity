*** Settings ***

Library  Selenium2Library

*** Variables ***

${ACTION_MENU_HEADER}  .actionMenuHeader a
${ACTION_MENU_CONTENT}  .actionMenuContent

${MODAL_BUTTONS_DELETE}  css=input[value="Delete"]

${FORM_FIELDS_TITLE}  title
${FORM_BUTTONS_SAVE}  form.button.save

*** Keywords ***

Select target folder
    Click button  Add...
    Click link  css=.overlay a[rel='Home']
    Page should contain element  css=.overlay tr.even input[type='checkbox']
    Click element  css=.overlay tr.even input[type='checkbox']
