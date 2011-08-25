#!/bin/bash
i18ndude rebuild-pot --pot collective/pfg/dexterity/locales/collective.pfg.dexterity.pot --create collective.pfg.dexterity collective/pfg/dexterity

i18ndude sync --pot collective/pfg/dexterity/locales/collective.pfg.dexterity.pot collective/pfg/dexterity/locales/*/LC_MESSAGES/collective.pfg.dexterity.po
