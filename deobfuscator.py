import re
import sys
import copy

def defeat_obfuscation_loops(obfuscated_script):

    obfuscation_loops = [m.span() for m in re.finditer(r'\$\w+\s*=\s*\d+\n\$\w+\s*=\s*\d+\nDo\nSwitch\s*\$\w+.*?EndSwitch\nUntil\s*.*?\n', obfuscated_script, re.DOTALL)]

    first_loop = obfuscated_script[obfuscation_loops[0][0]:obfuscation_loops[0][1] + 1]
    case_number = re.search(r'\$\w+\s*=\s*(\d+)', first_loop).group(1)
    statements = re.search(f'Case\s+{case_number}(.*)ExitLoop', first_loop, re.DOTALL).group(1)
    deobfuscated_script = obfuscated_script[:obfuscation_loops[0][0]] + statements

    for loop_index in range(1, len(obfuscation_loops)):
        deobfuscated_script += obfuscated_script[obfuscation_loops[loop_index - 1][1]: obfuscation_loops[loop_index][0]]
        obfuscated_loop = obfuscated_script[obfuscation_loops[loop_index][0]: obfuscation_loops[loop_index][1] + 1]

        case_number = re.search(r'\$\w+\s*=\s*(\d+)', obfuscated_loop).group(1)
        statements = re.search(f'Case\s+{case_number}(.*)ExitLoop', obfuscated_loop, re.DOTALL).group(1)
        deobfuscated_script += statements

    last_loop = obfuscated_script[obfuscation_loops[-1][0]:obfuscation_loops[-1][1] + 1]
    case_number = re.search(r'\$\w+\s*=\s*(\d+)', last_loop).group(1)
    statements = re.search(f'Case\s+{case_number}(.*)ExitLoop', last_loop, re.DOTALL).group(1)
    deobfuscated_script += obfuscated_script[obfuscation_loops[-2][1]:obfuscation_loops[-1][0]] + statements + obfuscated_script[obfuscation_loops[-1][1] + 1:]
    
    return deobfuscated_script

def _deobfuscate_strings(numbers_string, substract_number):
    result = ''
    
    numbers_list = numbers_string.split('.')
    for number in numbers_list:
        result = result + chr(int(number) - int(substract_number))

    return '"{}"'.format(result)

def deobfuscate_strings(obfuscated_script):

    deobfuscation_function_calls = [m.span() for m in re.finditer(r'faBwnHc\(\"[\d.]*\",\d\)', obfuscated_script)]

    first_call = obfuscated_script[deobfuscation_function_calls[0][0]:deobfuscation_function_calls[0][1] + 1]
    numbers_string = re.search(r'\"([\d.]*)\"', first_call).group(1)
    substract_number = re.search(r',(\d)', first_call).group(1)
    deobfuscated_script = obfuscated_script[:deobfuscation_function_calls[0][0]] + _deobfuscate_strings(numbers_string, substract_number)

    for call_index in range(1, len(deobfuscation_function_calls)):
        deobfuscated_script += obfuscated_script[deobfuscation_function_calls[call_index - 1][1]: deobfuscation_function_calls[call_index][0]]
        call = obfuscated_script[deobfuscation_function_calls[call_index][0]: deobfuscation_function_calls[call_index][1] + 1]
        numbers_string = re.search(r'\"([\d.]*)\"', call).group(1)
        substract_number = re.search(r',(\d)', call).group(1)
        deobfuscated_script += _deobfuscate_strings(numbers_string, substract_number)

    last_call = obfuscated_script[deobfuscation_function_calls[-1][0]:deobfuscation_function_calls[-1][1] + 1]
    numbers_string = re.search(r'\"([\d.]*)\"', last_call).group(1)
    substract_number = re.search(r',(\d)', last_call).group(1)
    deobfuscated_script += obfuscated_script[deobfuscation_function_calls[-2][1]:deobfuscation_function_calls[-1][0]] + _deobfuscate_strings(numbers_string, substract_number) + obfuscated_script[deobfuscation_function_calls[-1][1] + 1:]

    return deobfuscated_script

def defeat_unused_variables(obfuscated_script):

    deobfuscated_script = copy.deepcopy(obfuscated_script)
    script_variables_tokens = re.findall(r'\$\w+', obfuscated_script)
    variable_declarations = re.findall(r'Local \$\w* = ', obfuscated_script)
    for declaration in variable_declarations:
        variable_name = re.search(r'(\$\w+)', declaration).group(1)
        if script_variables_tokens.count(variable_name) == 1:
            deobfuscated_script = re.sub(f'Local \{variable_name} = .*', '', deobfuscated_script)

    return deobfuscated_script

def defeat_unused_functions(obfuscated_script):

    deobfuscated_script = copy.deepcopy(obfuscated_script)
    function_tokens = re.findall(r'(\w+)\(', obfuscated_script)
    function_declarations = re.findall(r'Func \w+\(', obfuscated_script)
    for declaration in function_declarations:
        function_name = re.search(r'(\w+)\(', declaration).group(1)
        if function_tokens.count(function_name) == 1:
            deobfuscated_script = re.sub(f'Func {function_name}\(.*?EndFunc', '', deobfuscated_script, flags=re.DOTALL)

    return deobfuscated_script

def defeat_unused_variables_and_functions(obfuscated_script):

    return re.sub(r'\n{3,}', '\n\n', defeat_unused_functions(defeat_unused_variables(obfuscated_script)))


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as obfuscated_script_file:
        obfuscated_script = obfuscated_script_file.read()
        with open ('deobfuscated_script.au3', 'w') as output_file:
            output_file.writelines(defeat_unused_variables_and_functions(deobfuscate_strings(defeat_obfuscation_loops(obfuscated_script))))
