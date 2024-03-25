import re

def generate_swift_extension(enum_definition):
    # Use regular expressions to extract enumeration names and enumeration values
    # Recognition typedef GPB_ENUM(xxxx) { }; Such a format of enumeration, structure
    enum_name_match = re.search(r'typedef\s+GPB_ENUM\((.*?)\)', enum_definition, re.DOTALL)
    enum_values_match = re.search(r'\{(.*?)\}', enum_definition, re.DOTALL)

    if enum_name_match and enum_values_match:
        enum_name = enum_name_match.group(1).strip()
        enum_values = enum_values_match.group(1)
        # print(f'default======:{enum_name}:{enum_values}')
        # parse enum  
        enum_values_list = []
        skip_values = []
        comment_block = None
        for line in enum_values.split('\n'):
            line = line.strip()
            parts = line.split('=')
            value_name = parts[0].strip()
            value_code = parts[1].strip().strip(',') if len(parts) > 1 else ''
            if value_code.endswith('kGPBUnrecognizedEnumeratorValue'):
                skip_values.append(value_code)
            else:
                enum_values_list.append((value_name, value_code))

        # Generate Swift extension
        swift_extension = f"extension {enum_name} {{\n"
        swift_extension += "    public init?(rawValue: Int32) {\n"
        swift_extension += "        switch rawValue {\n"
        default_case = ""

        for index, (value_info, value_code) in enumerate(enum_values_list):
            case_name = value_info.split('_')[-1]
            case_name = case_name[:1].lower() + case_name[1:]
            if len(case_name) > 1:
                if case_name[0].isalpha() and case_name[1:].isdigit():
                    case_name = case_name[:1].upper() + case_name[1:]
            if value_code in skip_values:
                continue
            if case_name.startswith('/') or case_name.startswith('*'):
                continue
            if case_name == '/**':
                continue
            print(f'======:{case_name}')
            # fix error casevalie
            if case_name == 'gPBUnsetOneOfCase':
                case_name = 'gpbUnsetOneOfCase'
            if value_code:
                swift_extension += f"        case {value_code}: self = .{case_name}\n"
                # get default case
                if value_code == '0' or value_code == '1' or value_code == '2':
                    if default_case == "":
                        default_case = case_name
        
        swift_extension += f"        default:\n"
        swift_extension += f"            self = .{default_case}\n" # when use defalut case , add error log
        swift_extension += f"            print(\"catch enum:{enum_name} error case:\(rawValue), restore to defalut \({enum_name}.{default_case})\")\n"
        swift_extension += "        }\n"
        swift_extension += "    }\n"
        swift_extension += "}\n\n"
        # delete dont need line code
        cleaned_lines = []
        swift_extension_lines = swift_extension.split('\n')
        for line in swift_extension_lines:
            if line.endswith('self = .'):
                cleaned_lines.append(line)

        for item in cleaned_lines:
            if item in swift_extension_lines:
                swift_extension_lines.remove(item)
        cleaned_swift_extension = '\n'.join(swift_extension_lines)

        return cleaned_swift_extension
    else:
        return ""

def generate_enum_extensions(header_file):
    with open(header_file, 'r') as f:
        header_content = f.read()

    enum_definitions = re.findall(r'typedef\s+GPB_ENUM\(.*?\}\s*;\s*', header_content, re.DOTALL)
    swift_extensions = ""

    for enum_definition in enum_definitions:
        swift_extension = generate_swift_extension(enum_definition)
        swift_extensions += swift_extension

    return swift_extensions


# the oc.h file that need to be convert 
header_file = 'your/oc.h'
# had generated .swift extension file
output_file = 'to/safeEnum_extension.swift'

swift_extensions = generate_enum_extensions(header_file)

with open(output_file, 'w') as f:
    f.write(swift_extensions)
