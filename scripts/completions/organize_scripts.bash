# Bash completion for organize_scripts.py
# Source this file in your ~/.bashrc or ~/.bash_profile:
#   source /path/to/scripts/completions/organize_scripts.bash

_organize_scripts_completions() {
    local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main subcommands
    local commands="dry-run execute"

    # Common options
    local common_opts="--verbose --log-file"

    if [[ ${cur} == -* ]]; then
        # Completing an option
        COMPREPLY=( $(compgen -W "${common_opts}" -- ${cur}) )
        return 0
    fi

    case "${prev}" in
        dry-run|execute)
            # After subcommand, offer options
            COMPREPLY=( $(compgen -W "${common_opts}" -- ${cur}) )
            return 0
            ;;
        --log-file)
            # File completion for --log-file
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        *)
            # Default: offer subcommands
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            return 0
            ;;
    esac
}

complete -F _organize_scripts_completions organize_scripts.py
complete -F _organize_scripts_completions python
