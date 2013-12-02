=================
os-refresh-config
=================

`os-refresh-config` uses `dib-run-parts` to run scripts in a
pre-defined set of directories::

  /opt/stack/os-config-refresh/pre-configure.d
  /opt/stack/os-config-refresh/configure.d
  /opt/stack/os-config-refresh/migration.d
  /opt/stack/os-config-refresh/post-configure.d

`/opt/stack/os-config-refresh` is the default base directory. You can
set `OS_REFRESH_CONFIG_BASE_DIR` environment variable to override the
default one.

Its intended purpose is to separate scripts execution into 4 phases:

1. Quiesce(pre-configure.d),
2. Configure(configure.d),
3. Migrate(migration.d),
4. Activate(post-configure.d).

It runs through all the phases above to ensure configuration is
applied and enabled on a machine. It will exit with an error if any
phase has a problem. The scripts in each phase should not depend on
each other having worked properly.
