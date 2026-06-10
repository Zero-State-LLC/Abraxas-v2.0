# Zsh completion for organize_scripts.py
# Add to your ~/.zshrc:
#   fpath=(/path/to/scripts/completions $fpath)
#   autoload -Uz compinit && compinit

#compdef organize_scripts.py

_organize_scripts() {
    local -a commands opts

    commands=(
        'dry-run:Preview moves without changing anything'
        'execute:Perform the actual file moves'
    )

    opts=(
        '--verbose[Enable debug logging]'
        '--log-file[Write JSON logs to file]:log file:_files'
    )

    if (( CURRENT == 2 )); then
        _describe 'command' commands
        return
    fi

    case $words[2] in
        dry-run|execute)
            _arguments -s $opts
            ;;
    esac
}

compdef _organize_scripts organize_scripts.py
