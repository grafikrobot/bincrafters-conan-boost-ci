from pprint import pprint
import argparse
from re import search

stages_libs = [
 set(['build', 'package_tools']),
 set(['generator']),
 set(['base']),
 set(['callable_traits',
      'compatibility',
      'config',
      'hof',
      'predef',
      'preprocessor']),
 set(['assert', 'io', 'mp11', 'static_assert', 'vmd', 'winapi']),
 set(['core', 'throw_exception']),
 set(['align',
      'array',
      'bind',
      'integer',
      'logic',
      'move',
      'system',
      'type_traits']),
 set(['atomic', 'crc', 'smart_ptr', 'tuple', 'utility']),
 set(['endian', 'exception', 'mpl', 'rational']),
 set(['concept_check',
      'detail',
      'metaparse',
      'polygon',
      'qvm',
      'ratio',
      'typeof']),
 set(['chrono',
      'container_hash',
      'conversion',
      'function_types',
      'numeric_interval',
      'optional']),
 set(['format',
      'fusion',
      'intrusive',
      'numeric_conversion',
      'stacktrace',
      'timer',
      'tti',
      'type_index']),
 set(['any', 'container', 'function', 'hana', 'iterator', 'variant']),
 set(['circular_buffer',
      'functional',
      'lambda',
      'locale',
      'regex',
      'scope_exit',
      'signals',
      'tokenizer',
      'unordered',
      'yap']),
 set(['cycle_group_a', 'local_function', 'multi_array']),
 set(['algorithm', 'range']),
 set(['cycle_group_b', 'filesystem', 'foreach', 'proto', 'test']),
 set(['gil', 'lexical_cast', 'math', 'phoenix']),
 set(['cycle_group_c', 'program_options', 'python', 'xpressive']),
 set(['date_time',
      'dynamic_bitset',
      'iostreams',
      'multiprecision',
      'parameter',
      'pool',
      'random',
      'serialization',
      'spirit',
      'thread']),
 set(['context',
      'contract',
      'convert',
      'dll',
      'geometry',
      'heap',
      'icl',
      'interprocess',
      'lockfree',
      'msm',
      'multi_index',
      'numeric_ublas',
      'ptr_container',
      'sort',
      'statechart',
      'type_erasure',
      'units',
      'uuid']),
 set(['accumulators',
      'assign',
      'coroutine',
      'coroutine2',
      'fiber',
      'flyweight',
      'poly_collection',
      'property_tree',
      'signals2',
      'wave']),
 set(['asio', 'compute', 'cycle_group_d']),
 set(['beast',
      'bimap',
      'disjoint_sets',
      'graph',
      'log',
      'process',
      'property_map'])
]

stages_names = [
    'bootstrap0',
    'bootstrap1',
    'bootstrap2',
    'stage0',
    'stage1',
    'stage2',
    'stage3',
    'stage4',
    'stage5',
    'stage6',
    'stage7',
    'stage8',
    'stage9',
    'stage10',
    'stage11',
    'stage12',
    'stage13',
    'stage14',
    'stage15',
    'stage16',
    'stage17',
    'stage18',
    'stage19',
    'stage20',
    'stage21',
    'stage22',
    'stage23',
    'stage24',
    'stage25',
    'stage26',
    'stage27',
    'stage28',
    'stage29',
    'stage30'
    ]

lib_subs = {
    'boost_package_tools':'boost-package-tools'
    }

lib_splits = [
    'build', 'bimap', 'graph', 'log', 'mpi', 'property_map', 'python']

setup = {
    'CLANG_39': 'linux',
    'CLANG_40': 'linux',
    'CLANG_50': 'linux',
    'CLANG_60': 'linux',
    'GCC_4': 'linux',
    'GCC_5': 'linux',
    'GCC_6': 'linux',
    'GCC_7': 'linux',
    'GCC_8': 'linux',
    'XCODE_83': 'xcode83',
    'XCODE_90': 'xcode90',
    'XCODE_91': 'xcode91',
    'XCODE_94': 'xcode94',
    'XCODE_10': 'xcode10'
    }

job_template = '''\
    - stage: {stage}
      env: REPO={name}
      <<: *{setup}
'''

job_template_split = '''\
    - stage: {stage}
      env:
        - REPO={name}
        - CONAN_ARCHS=x86
        - CONAN_DOCKER_32_IMAGES=1
      <<: *{setup}
    - stage: {stage}
      env:
        - REPO={name}
        - CONAN_ARCHS=x86_64
      <<: *{setup}
'''


def main(args):
    format_data = {}
    for libs in stages_libs:
        stage = stages_names.pop(0)
        format_data[stage] = {}
        for name in libs:
            boost_name = 'boost_' + name
            if boost_name in lib_subs:
                boost_name = lib_subs[boost_name]
            template = job_template
            if 'XCODE' not in args.build.upper() and name in lib_splits:
                template = job_template_split
            format_data[stage][name] = ''
            format_data[stage][name] += template.format(
                stage=stage,
                name=boost_name,
                setup=setup[args.build.upper()])
    
    with open(".travis.template.yml", "r") as f:
        travis_yml = f.read()
    
    def level_sort(x, y):
        x_type = search(r'([^0-9]+)', x).group(1)
        x_is_group = x.endswith("group")
        x_i = int(search(r'([0-9]+)', x).group(1))
        y_type = search(r'([^0-9]+)', y).group(1)
        y_is_group = y.endswith("group")
        y_i = int(search(r'([0-9]+)', y).group(1))
        if x_type != y_type:
            return cmp(x_type, y_type)
        elif x_i == y_i:
            return -1 if x_is_group and not y_is_group else 1
        else:
            return cmp(x_i, y_i)
    
    levels = sorted(format_data.keys(), level_sort)

    format_data['stages'] = ''
    for l in levels:
        format_data['stages'] += '''\
  - {0}
'''.format(l)

    format_data['jobs'] = ''
    for l in levels:
        if l in format_data:
            for j in sorted(format_data[l].keys()):
                format_data['jobs'] += format_data[l][j]

    # print(format_data['jobs'])
    # print(format_data['stages'])
    # pprint(format_data)
    # print(travis_yml.format(**format_data))
    
    with open(".travis.yml", "w") as f:
        f.write(travis_yml.format(**format_data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prefix_chars='+')
    # common args
    parser.add_argument('++debug', action='store_true')
    parser.add_argument("++build")
    args = parser.parse_args()
    main(args)
