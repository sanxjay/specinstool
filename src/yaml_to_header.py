import yaml
import sys
import os

def escape_c_string(s):
    if s is None:
        return ""
    escaped = str(s).replace('\\', '\\\\')
    escaped = escaped.replace('"', '\\"')
    escaped = escaped.replace('\n', '\\n')
    escaped = escaped.replace('\r', '\\r')
    escaped = escaped.replace('\t', '\\t')
    escaped = escaped.replace('\a', '\\a')
    escaped = escaped.replace('\b', '\\b')
    escaped = escaped.replace('\f', '\\f')
    escaped = escaped.replace('\v', '\\v')
    return escaped

HEADER_GUARD = "INSTRUCTION_H"
HEADER_STRUCT = f"""#ifndef {HEADER_GUARD}
#define {HEADER_GUARD}
#define MAX_COMMENTS 8
#define MAX_COMMENT_LEN 128
#define MAX_VARIABLES 8
#define MAX_HINTS 8
#define MAX_PSEUDOINSTRUCTIONS 32
#define MAX_NAME_LEN 46
#define MAX_DESC_LEN 4900

typedef struct {{
    char name[MAX_NAME_LEN];
    char location[MAX_DESC_LEN];
}} encoding_variable_t;

typedef struct {{
    char match[MAX_DESC_LEN];
    encoding_variable_t variables[MAX_VARIABLES];
    int num_variables;
}} encoding_t;

typedef struct {{
    char s[MAX_DESC_LEN];
    char u[MAX_DESC_LEN];
    char vs[MAX_DESC_LEN];
    char vu[MAX_DESC_LEN];
}} access_t;

typedef struct {{
    char ref[MAX_DESC_LEN];
}} hint_t;

typedef struct {{
    char when[MAX_DESC_LEN];
    char to[MAX_NAME_LEN];
}} pseudoinstruction_t;

typedef struct {{
    char comments[MAX_COMMENTS][MAX_COMMENT_LEN];
    int num_comments;
    char schema[MAX_DESC_LEN];
    char kind[MAX_NAME_LEN];
    char name[MAX_NAME_LEN];
    char long_name[MAX_DESC_LEN];
    char description[MAX_DESC_LEN];
    char definedBy[MAX_NAME_LEN];
    char assembly[MAX_DESC_LEN];
    encoding_t encoding;
    access_t access;
    int data_independent_timing; // 0 = false, 1 = true
    hint_t hints[MAX_HINTS];
    int num_hints;
    pseudoinstruction_t pseudoinstructions[MAX_PSEUDOINSTRUCTIONS];
    int num_pseudoinstructions;
    char operation[MAX_DESC_LEN];
    char sail[MAX_DESC_LEN];
}} instruction_t;

"""

FOOTER_STRUCT = f"""
#endif // {HEADER_GUARD}
"""

'''def make_struct_var(name):
    # Convert instruction name to a valid C variable name
    return name.replace('.', '_') + '_instruction'
'''

def yaml_to_header(yaml_file, header_file):
    #extracting top comments
    comments = []
    with open(yaml_file, 'r') as f:
        lines = f.readlines()
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            comments.append(line.strip())
        elif line.strip() == '':
            continue
        else:
            data_start = i
            break
    #parsing YAML as before
    data = yaml.safe_load(''.join(lines[data_start:]))
    if not data:
        print("Error: YAML file is empty.")
        return
    if isinstance(data, dict):
        inst = data
    elif isinstance(data, list) and len(data) > 0:
        inst = data[0]
    else:
        print("Error: YAML file must contain instruction data.")
        return
    def getstr(d, k, fallback=""):
        v = d.get(k, fallback)
        return escape_c_string(str(v)) if v is not None else ""
    encoding_vars = []
    if 'encoding' in inst and 'variables' in inst['encoding']:
        for var in inst['encoding']['variables']:
            encoding_vars.append((getstr(var, 'name'), getstr(var, 'location')))
    hints = []
    if 'hints' in inst:
        for hint in inst['hints']:
            if isinstance(hint, dict) and '$ref' in hint:
                hints.append(getstr(hint, '$ref'))
    pseudoinsts = []
    if 'pseudoinstructions' in inst:
        for pseudo in inst['pseudoinstructions']:
            pseudoinsts.append((getstr(pseudo, 'when'), getstr(pseudo, 'to')))
    access = {'s': '', 'u': '', 'vs': '', 'vu': ''}
    if 'access' in inst:
        for k in access.keys():
            if k in inst['access']:
                access[k] = getstr(inst['access'], k)
    
    #writing the header file
    with open(header_file, 'w') as f:
        f.write(HEADER_STRUCT)
        #instructions at structure data
        inst_name = getstr(inst, "name")
        struct_var = "instruction_data"
        f.write(f"\nconst instruction_t {struct_var} = {{\n")
        
        f.write(f'    .num_comments = {len(comments)},\n')
        f.write('    .comments = {\n')
        for c in comments:
            cstr = c.replace('"', '\"')
            f.write(f'        "{cstr}",\n')
        f.write('    },\n')
        f.write(f'    .schema = "{getstr(inst, "$schema")}",\n')
        f.write(f'    .kind = "{getstr(inst, "kind")}",\n')
        f.write(f'    .name = "{getstr(inst, "name")}",\n')
        f.write(f'    .long_name = "{getstr(inst, "long_name", getstr(inst, "short_description"))}",\n')
        f.write(f'    .description = "{getstr(inst, "description")}",\n')
        f.write(f'    .definedBy = "{getstr(inst, "definedBy", getstr(inst, "isa"))}",\n')
        f.write(f'    .assembly = "{getstr(inst, "assembly")}",\n')
        f.write("    .encoding = {\n")
        f.write(f'        .match = "{getstr(inst.get("encoding", {}), "match", "")}",\n')
        f.write(f'        .num_variables = {len(encoding_vars)},\n')
        f.write("        .variables = {\n")
        for name, loc in encoding_vars:
            f.write(f'            {{"{name}", "{loc}"}},\n')
        f.write("        }\n    },\n")
        f.write("    .access = {\n")
        f.write(f'        .s = "{access["s"]}",\n')
        f.write(f'        .u = "{access["u"]}",\n')
        f.write(f'        .vs = "{access["vs"]}",\n')
        f.write(f'        .vu = "{access["vu"]}",\n')
        f.write("    },\n")
        dit = inst.get('data_independent_timing', False)
        f.write(f'    .data_independent_timing = {1 if dit else 0},\n')
        f.write(f'    .num_hints = {len(hints)},\n')
        f.write("    .hints = {\n")
        for ref in hints:
            f.write(f'        {{"{ref}"}},\n')
        f.write("    },\n")
        f.write(f'    .num_pseudoinstructions = {len(pseudoinsts)},\n')
        f.write("    .pseudoinstructions = {\n")
        for when, to in pseudoinsts:
            f.write(f'        {{"{when}", "{to}"}},\n')
        f.write("    },\n")
        op = getstr(inst, 'operation()', getstr(inst, 'operation'))
        f.write(f'    .operation = "{op}",\n')
        sail = getstr(inst, 'sail()', getstr(inst, 'sail'))
        f.write(f'    .sail = "{sail}"\n')
        f.write("};\n\n")
        f.write(FOOTER_STRUCT)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input.yaml> <output.h>")
        sys.exit(1)

    input_yaml = sys.argv[1]
    output_header = sys.argv[2]

    if not os.path.exists(input_yaml):
        print(f"Error: Input file '{input_yaml}' not found.")
        sys.exit(1)

    try:
        yaml_to_header(input_yaml, output_header)
    except:
        print(f"Successfully converted '{input_yaml}' to '{output_header}'.")
