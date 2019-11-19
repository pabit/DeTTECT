import argparse
from interactive_menu import *
import os
import signal


def _init_menu():
    """
    Initialise the command line parameter menu.
    :return:
    """
    menu_parser = argparse.ArgumentParser(description='Detect Tactics, Techniques & Combat Threats',
                                          epilog='Source: https://github.com/rabobank-cdc/DeTTECT')
    menu_parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    menu_parser.add_argument('-i', '--interactive', help='launch the interactive menu, which has support for all modes',
                             action='store_true')

    # add subparsers
    subparsers = menu_parser.add_subparsers(title='MODE',
                                            description='Select the mode to use. Every mode has its own arguments and '
                                                        'help info displayed using: {visibility, detection, group, '
                                                        'generic} --help', metavar='', dest='subparser')

    # create the data source parser
    parser_data_sources = subparsers.add_parser('datasource', help='data source mapping and quality',
                                                aliases=['ds'],
                                                description='Create a heat map based on data sources, output data '
                                                            'sources to Excel or generate a data source improvement '
                                                            'graph.')
    parser_data_sources.add_argument('-ft', '--file-tech', help='path to the technique administration YAML file '
                                                                '(used with the option \'-u, --update\' to update '
                                                                'the visibility scores)',
                                     required=False)
    parser_data_sources.add_argument('-fd', '--file-ds', help='path to the data source administration YAML file',
                                     required=True)
    parser_data_sources.add_argument('-s', '--search', help='only include data sources which match the provided EQL '
                                                            'query')
    parser_data_sources.add_argument('-l', '--layer', help='generate a data source layer for the ATT&CK navigator',
                                     action='store_true')
    parser_data_sources.add_argument('-e', '--excel', help='generate an Excel sheet with all data source',
                                     action='store_true')
    parser_data_sources.add_argument('-g', '--graph', help='generate a graph with data sources added through time',
                                     action='store_true')
    parser_data_sources.add_argument('-y', '--yaml', help='generate a technique administration YAML file with '
                                                          'visibility scores based on the number of available data '
                                                          'sources', action='store_true')
    parser_data_sources.add_argument('-u', '--update', help='update the visibility scores within a technique '
                                                            'administration YAML file based on changes within any of '
                                                            'the data sources. Past visibility scores are preserved in '
                                                            'the \'score_logbook\', and manually assigned scores are '
                                                            'not updated without your approval. The updated visibility '
                                                            'scores are calculated in the same way as with the option: '
                                                            '-y, --yaml', action='store_true')
    parser_data_sources.add_argument('--health', help='check the YAML file(s) for errors', action='store_true')

    # create the visibility parser
    parser_visibility = subparsers.add_parser('visibility', aliases=['v'],
                                              help='visibility coverage mapping based on techniques and data sources',
                                              description='Create a heat map based on visibility scores, overlay '
                                                          'visibility with detections, output to Excel or check the '
                                                          'health of the technique administration YAML file.')
    parser_visibility.add_argument('-ft', '--file-tech', help='path to the technique administration YAML file (used to '
                                                              'score the level of visibility)', required=True)
    parser_visibility.add_argument('-fd', '--file-ds', help='path to the data source administration YAML file (used to '
                                                            'add metadata on the involved data sources)')
    parser_visibility.add_argument('-sd', '--search-detection', help='only include detection objects which match the '
                                                                     'provided EQL query')
    parser_visibility.add_argument('-sv', '--search-visibility', help='only include visibility objects which match the '
                                                                      'provided EQL query')
    parser_visibility.add_argument('--all-scores', help='include all \'score\' objects from the \'score_logbook\' in '
                                                        'the EQL search. The default behaviour is to only include the '
                                                        'most recent \'score\' objects',
                                   action='store_true', default=False)
    parser_visibility.add_argument('-l', '--layer', help='generate a visibility layer for the ATT&CK navigator',
                                   action='store_true')
    parser_visibility.add_argument('-e', '--excel', help='generate an Excel sheet with all administrated techniques',
                                   action='store_true')
    parser_visibility.add_argument('-o', '--overlay', help='generate a visibility layer overlaid with detections for '
                                                           'the ATT&CK navigator', action='store_true')
    parser_visibility.add_argument('-g', '--graph', help='generate a graph with visibility added through time',
                                   action='store_true')
    parser_visibility.add_argument('--health', help='check the YAML file for errors', action='store_true')

    # create the detection parser
    parser_detection = subparsers.add_parser('detection', aliases=['d'],
                                             help='detection coverage mapping based on techniques',
                                             description='Create a heat map based on detection scores, overlay '
                                                         'detections with visibility, generate a detection '
                                                         'improvement graph, output to Excel or check the health of '
                                                         'the technique administration YAML file.')
    parser_detection.add_argument('-ft', '--file-tech', help='path to the technique administration YAML file (used to '
                                                             'score the level of detection)', required=True)
    parser_detection.add_argument('-fd', '--file-ds', help='path to the data source administration YAML file (used in '
                                                           'the overlay with visibility to add metadata on the '
                                                           'involved data sources)')
    parser_detection.add_argument('-sd', '--search-detection', help='only include detection objects which match the '
                                                                    'provided EQL query')
    parser_detection.add_argument('-sv', '--search-visibility', help='only include visibility objects which match the '
                                                                     'provided EQL query')
    parser_detection.add_argument('--all-scores', help='include all \'score\' objects from the \'score_logbook\' in '
                                                       'the EQL search. The default behaviour is to only include the '
                                                       'most recent \'score\' objects',
                                  action='store_true', default=False)
    parser_detection.add_argument('-l', '--layer', help='generate detection layer for the ATT&CK navigator',
                                  action='store_true')
    parser_detection.add_argument('-e', '--excel', help='generate an Excel sheet with all administrated techniques',
                                  action='store_true')
    parser_detection.add_argument('-o', '--overlay', help='generate a detection layer overlaid with visibility for '
                                                          'the ATT&CK navigator', action='store_true')
    parser_detection.add_argument('-g', '--graph', help='generate a graph with detections added through time',
                                  action='store_true')
    parser_detection.add_argument('--health', help='check the YAML file(s) for errors', action='store_true')

    # create the group parser
    parser_group = subparsers.add_parser('group', aliases=['g'],
                                         description='Create threat actor group heat maps, compare group(s) and '
                                                     'compare group(s) with visibility and detection coverage.',
                                         help='threat actor group mapping')
    parser_group.add_argument('-g', '--groups', help='specify the ATT&CK Groups to include separated using commas. '
                                                     'Group can be their ID, name or alias (default is all groups). '
                                                     'Other option is to provide a YAML file with a custom group(s) '
                                                     '(default = all)',
                              default='all')
    parser_group.add_argument('-o', '--overlay', help='specify what to overlay on the group(s) (provided using the '
                                                      'arguments \'-g/--groups\'): group(s), visibility or detection. '
                                                      'When overlaying a GROUP: the group can be their ATT&CK ID, name '
                                                      'or alias separated using commas. Or provide a file path of a '
                                                      'YAML file with a custom group(s). When overlaying VISIBILITY or '
                                                      'DETECTION provide a YAML with the technique administration.')
    parser_group.add_argument('-t', '--overlay-type', help='specify the type of overlay (default = group)',
                              choices=['group', 'visibility', 'detection'], default='group')
    parser_group.add_argument('--software-group', help='add techniques to the heat map by checking which software is '
                                                       'used by group(s), and hence which techniques the software '
                                                       'supports (does not influence the scores). If overlay group(s) '
                                                       'are provided, only software related to those group(s) are '
                                                       'included', action='store_true', default=False)
    parser_group.add_argument('-p', '--platform', help='specify the platform (default = Windows)',
                              choices=['all'] + list(PLATFORMS.values()), default='Windows')
    parser_group.add_argument('-s', '--stage', help='specify the stage (default = attack)',
                              choices=['attack', 'pre-attack'], default='attack')
    parser_group.add_argument('-sd', '--search-detection', help='only include detection objects which match the '
                                                                'provided EQL query')
    parser_group.add_argument('-sv', '--search-visibility', help='only include visibility objects which match the '
                                                                 'provided EQL query')
    parser_group.add_argument('--all-scores', help='include all \'score\' objects from the \'score_logbook\' in '
                                                   'the EQL search. The default behaviour is to only include the '
                                                   'most recent \'score\' objects',
                              action='store_true', default=False)
    parser_group.add_argument('--health', help='check the YAML file(s) for errors', action='store_true')

    # create the generic parser
    parser_generic = subparsers.add_parser('generic', description='Generic functions which will output to stdout.',
                                           help='includes: statistics on ATT&CK data source and updates on techniques'
                                                ', groups and software', aliases=['ge'])

    parser_generic.add_argument('-ds', '--datasources', help='get a sorted count on how many ATT&CK Enterprise '
                                                             'techniques are covered by a particular Data Source',
                                action='store_true')
    parser_generic.add_argument('-m', '--mitigations', help='get a sorted count on how many ATT&CK Enterprise or '
                                                            'Mobile techniques are covered by a Mitigation',
                                choices=['enterprise', 'mobile'])
    parser_generic.add_argument('-u', '--updates', help='get a sorted list for when updates were released for '
                                                        'techniques, groups or software',
                                choices=['techniques', 'groups', 'software'])
    parser_generic.add_argument('--sort', help='sorting of the output from \'-u/--update\' on modified or creation '
                                               'date (default = modified)', choices=['modified', 'created'],
                                default='modified')

    return menu_parser


def _menu(menu_parser):
    """
    Parser for the command line parameter menu and calls the appropriate functions.
    :param menu_parser: the argparse menu as created with '_init_menu()'
    :return:
    """
    args = menu_parser.parse_args()

    if args.interactive:
        interactive_menu()

    elif args.subparser in ['datasource', 'ds']:
        if check_file(args.file_ds, FILE_TYPE_DATA_SOURCE_ADMINISTRATION, args.health):
            file_ds = args.file_ds

            if args.search:
                file_ds = data_source_search(args.file_ds, FILE_TYPE_DATA_SOURCE_ADMINISTRATION, args.search)
                if not file_ds:
                    quit()  # something went wrong in executing the search or 0 results where returned
            if args.update and check_file(args.file_tech, FILE_TYPE_TECHNIQUE_ADMINISTRATION, args.health):
                update_technique_administration_file(file_ds, args.file_tech)
            if args.layer:
                generate_data_sources_layer(file_ds)
            if args.excel:
                export_data_source_list_to_excel(file_ds)
            if args.graph:
                plot_data_sources_graph(file_ds)
            if args.yaml:
                generate_technique_administration_file(file_ds)

    elif args.subparser in ['visibility', 'v']:
        if args.layer or args.overlay:
            if not args.file_ds:
                print('[!] Generating a visibility layer or an overlay requires the data source '
                      'administration YAML file (\'-fd, --file-ds\')')
                quit()
            if not check_file(args.file_ds, FILE_TYPE_DATA_SOURCE_ADMINISTRATION, args.health):
                quit()

        if check_file(args.file_tech, FILE_TYPE_TECHNIQUE_ADMINISTRATION, args.health):
            file_tech = args.file_tech

            if args.search_detection or args.search_visibility:
                file_tech = techniques_search(args.file_tech, args.search_visibility, args.search_detection,
                                              include_all_score_objs=args.all_scores)
                if not file_tech:
                    quit()  # something went wrong in executing the search or 0 results where returned
            if args.layer:
                generate_visibility_layer(file_tech, args.file_ds, False)
            if args.overlay:
                generate_visibility_layer(file_tech, args.file_ds, True)
            if args.graph:
                plot_graph(file_tech, 'visibility')
            if args.excel:
                export_techniques_list_to_excel(file_tech)

    # toto add search capabilities
    elif args.subparser in ['group', 'g']:
        if not generate_group_heat_map(args.groups, args.overlay, args.overlay_type, args.stage, args.platform,
                                       args.software_group, args.search_visibility, args.search_detection, args.health,
                                       include_all_score_objs=args.all_scores):
            quit()  # something went wrong in executing the search or 0 results where returned

    elif args.subparser in ['detection', 'd']:
        if args.overlay:
            if not args.file_ds:
                print('[!] An overlay requires the data source administration YAML file (\'-fd, --file-ds\')')
                quit()
            if not check_file(args.file_ds, FILE_TYPE_DATA_SOURCE_ADMINISTRATION, args.health):
                quit()

        if check_file(args.file_tech, FILE_TYPE_TECHNIQUE_ADMINISTRATION, args.health):
            file_tech = args.file_tech

            if args.search_detection or args.search_visibility:
                file_tech = techniques_search(args.file_tech, args.search_visibility, args.search_detection,
                                              include_all_score_objs=args.all_scores)
                if not file_tech:
                    quit()  # something went wrong in executing the search or 0 results where returned
            if args.layer:
                generate_detection_layer(file_tech, args.file_ds, False)
            if args.overlay and check_file(args.file_ds, FILE_TYPE_DATA_SOURCE_ADMINISTRATION, args.health):
                generate_detection_layer(file_tech, args.file_ds, True)
            if args.graph:
                plot_graph(file_tech, 'detection')
            if args.excel:
                export_techniques_list_to_excel(file_tech)

    elif args.subparser in ['generic', 'ge']:
        if args.datasources:
            get_statistics_data_sources()
        elif args.mitigations:
            get_statistics_mitigations(args.mitigations)
        elif args.updates:
            get_updates(args.updates, args.sort)

    else:
        menu_parser.print_help()


def _prepare_folders():
    """
    Create the folders 'cache' and 'output' if they do not exist.
    :return:
    """
    if not os.path.exists('cache'):
        os.mkdir('cache')
    if not os.path.exists('output'):
        os.mkdir('output')


def _signal_handler(signum, frame):
    """
    Function to handles exiting via Ctrl+C.
    :param signum:
    :param frame:
    :return:
    """
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, _signal_handler)
    _prepare_folders()
    _menu(_init_menu())
