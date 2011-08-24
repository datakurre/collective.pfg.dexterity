#!/bin/bash
i18ndude rebuild-pot --pot jyu/pfg/dexterity/locales/jyu.pfg.dexterity.pot --create jyu.pfg.dexterity jyu/pfg/dexterity

i18ndude sync --pot jyu/pfg/dexterity/locales/jyu.pfg.dexterity.pot jyu/pfg/dexterity/locales/*/LC_MESSAGES/jyu.pfg.dexterity.po
