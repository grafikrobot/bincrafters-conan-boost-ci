from pprint import pprint
import argparse
from re import search

stages = {
    "bootstrap0": {
        'source-only':[],
        'build':["boost_build"]
        },
    "bootstrap1": {
        'source-only':["boost_generator", "boost-package-tools"],
        'build':[]
        },
    "level0": {
        'source-only':["callable_traits", "compatibility", "config", "predef", "preprocessor"],
        'build':[]
        },
    "level1": {
        'source-only':["assert", "io", "mp11", "preprocessor", "static_assert", "vmd", "winapi"],
        'build':[]
        },
    "level2": {
        'source-only':["core", "throw_exception"],
        'build':[]
        },
    "level3": {
        'source-only':["align", "array", "bind", "integer", "logic", "move", "type_traits"],
        'build':["system"]
        },
    "level4": {
        'source-only':["crc", "smart_ptr", "tuple"],
        'build':["atomic"]
        },
    "level5group": {
        'source-only':["level5group"],
        'build':["exception"]
        },
    "level5": {
        'source-only':["concept_check", "conversion", "detail", "function", "function_types", "functional", "fusion", "iterator", "mpl", "optional", "type_index", "typeof", "utility"],
        'build':[]
        },
    "level6": {
        'source-only':["any", "endian", "format", "gil", "hana", "intrusive", "lambda", "multi_array", "numeric_conversion", "numeric_interval", "polygon", "qvm", "rational", "scope_exit", "tokenizer", "tti"],
        'build':["regex"]
        },
    "level7": {
        'source-only':["local_function", "range", "ratio"],
        'build':["container", "signals"]
        },
    "level8group": {
        'source-only':[],
        'build':["level8group"]
        },
    "level8": {
        'source-only':["circular_buffer", "foreach", "lexical_cast", "proto", "unordered"],
        'build':["chrono", "filesystem", "math"]
        },
    "level9": {
        'source-only':["algorithm", "phoenix", "variant", "xpressive"],
        'build':["program_options", "python", "random", "stacktrace", "timer"]
        },
    "level10": {
        'source-only':["multiprecision", "parameter"],
        'build':["iostreams", "test"]
        },
    "level11group": {
        'source-only':[],
        'build':["level11group"]
        },
    "level11": {
        'source-only':["heap", "lockfree", "metaparse", "pool", "spirit"],
        'build':["date_time", "locale", "serialization", "thread"]
        },
    "level12": {
        'source-only':["dll", "dynamic_bitset", "geometry", "icl", "interprocess", "msm", "multi_index", "numeric_ublas", "ptr_container", "sort", "statechart", "units", "uuid"],
        'build':["context", "convert", "type_erasure"]
        },
    "level13": {
        'source-only':["accumulators", "assign", "coroutine2", "flyweight", "poly_collection", "property_tree", "signals"],
        'build':["coroutine", "fiber", "wave"]
        },
    "level14group": {
        'source-only':[],
        'build':["level14group"]
        },
    "level14": {
        'source-only':["asio", "bimap", "compute", "disjoint_sets", "graph", "property_map"],
        'build':["graph_parallel", "log", "mpi"]
        },
    "level15": {
        'source-only':["beast", "numeric_odeint", "process"],
        'build':[]
        }
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
      env: REPO=boost_{name}
      <<: *{setup}
'''


def main(args):
    format_data = {}
    for stage in stages.keys():
        format_data[stage] = {}
        for name in stages[stage]['source-only'] + stages[stage]['build']:
            format_data[stage][name] = ''
            for compiler in args.build:
                format_data[stage][name] += job_template.format(
                    stage=stage,
                    name=name,
                    setup=setup[compiler.upper()])
    
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

    format_data['build'] = compiler.upper()
    
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
    parser.add_argument("++build", action='append', default=[])
    args = parser.parse_args()
    main(args)
