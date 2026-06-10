# Fish completion for organize_scripts.py
# Copy to ~/.config/fish/completions/ or source it

complete -c organize_scripts.py -f

# Subcommands
complete -c organize_scripts.py -n "__fish_use_subcommand" -a dry-run -d "Preview moves without changing anything"
complete -c organize_scripts.py -n "__fish_use_subcommand" -a execute   -d "Perform the actual file moves"

# Common options (available after subcommand or as top-level in some cases)
complete -c organize_scripts.py -n "__fish_seen_subcommand_from dry-run execute" -l verbose -d "Enable debug logging"
complete -c organize_scripts.py -n "__fish_seen_subcommand_from dry-run execute" -l log-file -r -F -d "Write structured JSON logs to this file"

# Also allow options before subcommand (for convenience)
complete -c organize_scripts.py -l verbose -d "Enable debug logging"
complete -c organize_scripts.py -l log-file -r -F -d "Write structured JSON logs to this file"
