#!/usr/bin/env python3
# coding: utf-8

import argparse
import json
import jsonschema
import os
import sys
import re

PACK_DIR="pack"
SCHEMA_DIR="schema/v1"
validation_errors = 0
text_by_card_title = dict()
stripped_text_by_card_title = dict()

def check_dir_access(path):
    if not os.path.isdir(path):
        sys.exit("%s is not a valid path" % path)
    elif os.access(path, os.R_OK):
        return
    else:
        sys.exit("%s is not a readable directory")

def check_file_access(path):
    if not os.path.isfile(path):
        sys.exit("%s does not exist" % path)
    elif os.access(path, os.R_OK):
        return
    else:
        sys.exit("%s is not a readable file")

def check_json_schema(args, data, path):
    global validation_errors
    try:
        jsonschema.Draft4Validator.check_schema(data)
        return True
    except jsonschema.exceptions.SchemaError as e:
        verbose_print(args, "%s: Schema file is not valid Draft 4 JSON schema.\n" % path, 0)
        validation_errors += 1
        verbose_print(args, "%s\n" % e.message, 0)
        return False

def load_json_file(args, path):
    global validation_errors
    try:
        with open(path, "rb") as data_file:
            bin_data = data_file.read()
        raw_data = bin_data.decode("utf-8")
        json_data = json.loads(raw_data)
    except ValueError as e:
        verbose_print(args, "%s: File is not valid JSON.\n" % path, 0)
        validation_errors += 1
        verbose_print(args, "%s\n" % e.message, 0)
        return None

    return json_data

def load_cycles(args):
    verbose_print(args, "Loading cycle index file...\n", 1)
    cycles_path = os.path.join(args.base_path, "cycles.json")
    cycles_data = load_json_file(args, cycles_path)

    return cycles_data

def load_packs(args, cycles_data):
    verbose_print(args, "Loading pack index file...\n", 1)
    packs_path = os.path.join(args.base_path, "packs.json")
    packs_data = load_json_file(args, packs_path)

    for p in packs_data:
        pack_filename = "{}.json".format(p["code"])
        pack_path = os.path.join(args.pack_path, pack_filename)
        check_file_access(pack_path)

    return packs_data

def load_factions(args):
    verbose_print(args, "Loading faction index file...\n", 1)
    factions_path = os.path.join(args.base_path, "factions.json")
    factions_data = load_json_file(args, factions_path)

    return factions_data

def load_types(args):
    verbose_print(args, "Loading type index file...\n", 1)
    types_path = os.path.join(args.base_path, "types.json")
    types_data = load_json_file(args, types_path)

    return types_data

def load_sides(args):
    verbose_print(args, "Loading side index file...\n", 1)
    sides_path = os.path.join(args.base_path, "sides.json")
    sides_data = load_json_file(args, sides_path)

    return sides_data

def parse_commandline():
    argparser = argparse.ArgumentParser(description="Validate JSON in the netrunner cards repository.")
    argparser.add_argument("-v", "--verbose", default=0, action="count", help="verbose mode")
    argparser.add_argument("-b", "--base_path", default=os.getcwd(), help="root directory of JSON repo (default: current directory)")
    argparser.add_argument("-p", "--pack_path", default=None, help=("pack directory of JSON repo (default: BASE_PATH/%s/)" % PACK_DIR))
    argparser.add_argument("-c", "--schema_path", default=None, help=("schema directory of JSON repo (default: BASE_PATH/%s/" % SCHEMA_DIR))
    args = argparser.parse_args()

    # Set all the necessary paths and check if they exist
    if getattr(args, "schema_path", None) is None:
        setattr(args, "schema_path", os.path.join(args.base_path,SCHEMA_DIR))
    if getattr(args, "pack_path", None) is None:
        setattr(args, "pack_path", os.path.join(args.base_path,PACK_DIR))
    check_dir_access(args.base_path)
    check_dir_access(args.schema_path)
    check_dir_access(args.pack_path)

    return args

def verify_stripped_text_is_ascii(args, card, pack_code):
    global validation_errors

    stripped_text = card.get('stripped_text', '')
    try:
        stripped_text.encode('ascii')
    except UnicodeEncodeError:
        verbose_print(args, "ERROR\n", 2)
        verbose_print(
            args,
            "Stripped text contains non-ascii characters in card: (pack code: '{}' title: '{}' stripped_text '{}')\n".format(
                pack_code,
                card['title'],
                stripped_text,
            ),
            0,
        )
        validation_errors += 1

def verify_text_has_fancy_text(args, card, pack_code):
    global validation_errors

    text = card.get('text', '')
    if ('[interrupt]' in text) and ('[interrupt] →' not in text):
        verbose_print(args, "ERROR\n", 2)
        verbose_print(
            args,
            "Incorrect interrupt text in card: (pack code: '{}' title: '{}' text '{}')\n".format(
                pack_code,
                card['title'],
                text,
            ),
            0,
        )
        validation_errors += 1
    if ('Interface' in text) and (('Interface ->' in text) or ('Interface →' not in text)):
        verbose_print(args, "ERROR\n", 2)
        verbose_print(
            args,
            "Incorrect interface text in card: (pack code: '{}' title: '{}' text '{}')\n".format(
                pack_code,
                card['title'],
                text,
            ),
            0,
        )
        validation_errors += 1

def validate_cards(args, packs_data, factions_data, types_data, sides_data):
    global validation_errors
    global text_by_card_title

    card_schema_path = os.path.join(args.schema_path, "card_schema.json")

    CARD_SCHEMA = load_json_file(args, card_schema_path)
    if not CARD_SCHEMA:
        return
    if not check_json_schema(args, CARD_SCHEMA, card_schema_path):
        return

    for p in packs_data:
        verbose_print(args, "Validating cards from %s...\n" % p["name"], 1)

        pack_path = os.path.join(args.pack_path, "{}.json".format(p["code"]))
        pack_data = load_json_file(args, pack_path)
        if not pack_data:
            continue

        for card in pack_data:
            if card.get('title') not in text_by_card_title:
                text_by_card_title[card.get('title')] = set()
            text_by_card_title[card.get('title')].add(card.get('text'))
            if card.get('title') not in stripped_text_by_card_title:
                stripped_text_by_card_title[card.get('title')] = set()
            stripped_text_by_card_title[card.get('title')].add(card.get('stripped_text'))
            verify_stripped_text_is_ascii(args, card, p["code"])
            verify_text_has_fancy_text(args, card, p["code"])

    for card in text_by_card_title:
        if len(text_by_card_title[card]) > 1:
            verbose_print(args, "ERROR\n",2)
            verbose_print(args, "Validation error for card '%s': Found %d different versions of text.\n" % (card, len(text_by_card_title[card])))
            for text in text_by_card_title[card]:
                verbose_print(args, "    '%s'\n" % (text))
            validation_errors += 1
    for card in stripped_text_by_card_title:
        if len(stripped_text_by_card_title[card]) > 1:
            verbose_print(args, "ERROR\n",2)
            verbose_print(args, "Validation error for card '%s': Found %d different versions of stripped_text.\n" % (card, len(stripped_text_by_card_title[card])))
            for stripped_text in stripped_text_by_card_title[card]:
                verbose_print(args, "    '%s'\n" % (stripped_text))
            validation_errors += 1


def check_translations_simple(args, base_translations_path, locale_name, base_file_name):
    file_name = "%s.%s.json" % (base_file_name, locale_name)
    verbose_print(args, "Loading file %s...\n" % file_name, 1)
    file_path = os.path.join(base_translations_path, locale_name, file_name)
    load_json_file(args, file_path)

def check_translations_packs(args, base_translations_path, locale_name):
    packs_translations_path = os.path.join(base_translations_path, locale_name, 'pack')
    file_names = os.listdir(packs_translations_path)
    for file_name in file_names:
        verbose_print(args, "Loading file %s...\n" % file_name, 1)
        file_path = os.path.join(packs_translations_path, file_name)
        load_json_file(args, file_path)

def check_translations(args, base_translations_path, locale_name):
    verbose_print(args, "Loading Translations for %s...\n" % locale_name, 1)
    translations_path = os.path.join(base_translations_path, locale_name)
    check_translations_simple(args, base_translations_path, locale_name, 'cycles')
    check_translations_simple(args, base_translations_path, locale_name, 'factions')
    check_translations_simple(args, base_translations_path, locale_name, 'packs')
    check_translations_simple(args, base_translations_path, locale_name, 'sides')
    check_translations_simple(args, base_translations_path, locale_name, 'types')
    check_translations_packs(args, base_translations_path, locale_name)

def check_all_translations(args):
    verbose_print(args, "Loading Translations...\n", 1)
    base_translations_path = os.path.join(args.base_path, "translations")
    translations_directories = os.listdir(base_translations_path)
    for locale_name in translations_directories:
        check_translations(args, base_translations_path, locale_name)

def check_mwl(args):
    verbose_print(args, "Loading MWL...\n", 1)
    mwl_path = os.path.join(args.base_path, "mwl.json")
    load_json_file(args, mwl_path)

def check_prebuilt(args):
    verbose_print(args, "Loading Prebuilts...\n", 1)
    pre_path = os.path.join(args.base_path, "prebuilts.json")
    load_json_file(args, pre_path)

def check_rotation(args, cycles_data):
    verbose_print(args, "Loading Rotations...\n", 1)
    rot_path = os.path.join(args.base_path, "rotations.json")
    rot_data = load_json_file(args, rot_path)

def verbose_print(args, text, minimum_verbosity=0):
    if args.verbose >= minimum_verbosity:
        sys.stdout.write(text)

def main():
    # Initialize global counters for encountered validation errors
    global formatting_errors
    global validation_errors
    formatting_errors = 0
    validation_errors = 0

    args = parse_commandline()

    check_all_translations(args)

    cycles = load_cycles(args)

    packs = load_packs(args, cycles)

    factions = load_factions(args)

    types = load_types(args)

    sides = load_sides(args)

    if packs and factions and types and sides:
        validate_cards(args, packs, factions, types, sides)
    else:
        verbose_print(args, "Skipping card validation...\n", 0)

    check_prebuilt(args)

    check_rotation(args, cycles)

    check_mwl(args)

    sys.stdout.write("Found %s validation errors\n" % (validation_errors))
    if validation_errors == 0:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
