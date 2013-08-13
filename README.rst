Runs through all of the phases to ensure configuration is applied and
enabled on a machine. Will exit with an error if any phase has a
problem. Scripts should not depend on eachother having worked properly.
Set ``OS_REFRESH_CONFIG_BASE_DIR`` environment variable to override the
default
