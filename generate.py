from pprint import pprint
import argparse
from re import search

stages_libs = [
 set(['build']),
 set(['generator', 'package_tools']),
 set(['base']),
 set(['callable_traits',
      'compatibility',
      'config',
      'hof',
      'predef',
      'preprocessor']),
 set(['assert',
      'atomic',
      'chrono',
      'circular_buffer',
      'container',
      'container_hash',
      'context',
      'conversion',
      'core',
      'coroutine',
      'coroutine2',
      'endian',
      'exception',
      'fiber',
      'filesystem',
      'flyweight',
      'format',
      'function',
      'generator',
      'icl',
      'integer',
      'interprocess',
      'intrusive',
      'io',
      'iterator',
      'locale',
      'move',
      'mp11',
      'multi_index',
      'optional',
      'phoenix',
      'poly_collection',
      'qvm',
      'rational',
      'regex',
      'signals2',
      'smart_ptr',
      'statechart',
      'static_assert',
      'system',
      'throw_exception',
      'tokenizer',
      'type_erasure',
      'units',
      'unordered',
      'uuid',
      'variant',
      'vmd',
      'wave',
      'winapi',
      'xpressive']),
 set(['align',
      'array',
      'asio',
      'assign',
      'beast',
      'bind',
      'crc',
      'cycle_group_a',
      'cycle_group_b',
      'detail',
      'function_types',
      'heap',
      'lambda',
      'lockfree',
      'log',
      'logic',
      'metaparse',
      'mpl',
      'multi_array',
      'numeric_interval',
      'numeric_odeint',
      'polygon',
      'ptr_container',
      'python',
      'ratio',
      'stacktrace',
      'timer',
      'tti',
      'tuple',
      'type_traits',
      'typeof',
      'utility']),
 set(['algorithm',
      'compute',
      'concept_check',
      'convert',
      'cycle_group_c',
      'cycle_group_d',
      'dll',
      'foreach',
      'functional',
      'fusion',
      'geometry',
      'gil',
      'hana',
      'local_function',
      'numeric_conversion',
      'numeric_ublas',
      'parameter',
      'process',
      'proto',
      'scope_exit',
      'sort',
      'test',
      'type_index']),
 set(['any',
      'bimap',
      'contract',
      'msm',
      'program_options',
      'property_tree',
      'range',
      'signals',
      'yap']),
 set(['accumulators', 'lexical_cast', 'math']),
 set(['date_time',
      'dynamic_bitset',
      'iostreams',
      'multiprecision',
      'pool',
      'random',
      'serialization',
      'spirit',
      'thread']),
 set(['disjoint_sets', 'graph', 'graph_parallel', 'mpi', 'property_map'])
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
    'XCODE_90': 'xcode9',
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
