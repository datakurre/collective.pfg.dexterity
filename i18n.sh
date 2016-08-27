#!/usr/bin/env bash
bin/i18ndude rebuild-pot --pot src/collective/pfg/dexterity/locales/collective.pfg.dexterity.pot --create collective.pfg.dexterity src/collective/pfg/dexterity
bin/i18ndude sync --pot src/collective/pfg/dexterity/locales/collective.pfg.dexterity.pot src/collective/pfg/dexterity/locales/*/LC_MESSAGES/collective.pfg.dexterity.po
