#!/bin/bash
# For resource changing module
ansible localhost -c local -m template -a "src=module_template.py.j2 dest=my_module.py" -e @module_template_vars.yaml
# For resource info collection module
ansible localhost -c local -m template -a "src=module_info_template.py.j2 dest=my_module_info.py" -e @module_template_vars.yaml
