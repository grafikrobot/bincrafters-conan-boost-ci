from pprint import pprint
import argparse
from re import search

stages_libs = [
 set(['build']),
 set(['generator', 'package_tools']),
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
      'timer',
      'tti',
      'type_index']),
 set(['any', 'container', 'function', 'hana', 'iterator', 'variant']),
 set(['circular_buffer',
      'functional',
      'gil',
      'lambda',
      'regex',
      'scope_exit',
      'signals',
      'tokenizer',
      'unordered']),
 set(['local_function', 'multi_array', 'range']),
 set(['algorithm', 'filesystem', 'foreach', 'level8group', 'proto']),
 set(['lexical_cast', 'math', 'phoenix', 'test']),
 set(['program_options', 'python', 'random', 'stacktrace', 'xpressive']),
 set(['iostreams', 'multiprecision', 'parameter']),
 set(['heap', 'level11group', 'lockfree']),
 set(['date_time', 'pool', 'serialization', 'spirit', 'thread']),
 set(['context',
      'contract',
      'convert',
      'dll',
      'dynamic_bitset',
      'geometry',
      'icl',
      'interprocess',
      'locale',
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
 set(['asio', 'compute', 'level14group', 'log']),
 set(['beast',
      'bimap',
      'disjoint_sets',
      'graph',
      'graph_parallel',
      'mpi',
      'process',
      'property_map']),
 set(['numeric_odeint'])
 ]

stages_names = [
    'bootstrap0',
    'bootstrap1',
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

setup = {
    'CLANG_39': 'linux',
    'CLANG_40': 'linux',
    'GCC_4': 'linux',
    'GCC_5': 'linux',
    'GCC_6': 'linux',
    'GCC_7': 'linux',
    'XCODE_73': 'xcode73',
    'XCODE_81': 'xcode83',
    'XCODE_83': 'xcode83',
    'XCODE_90': 'xcode90'
    }

job_template = '''\
    - stage: {stage}
      env: REPO={name}
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
            format_data[stage][name] = ''
            format_data[stage][name] += job_template.format(
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
