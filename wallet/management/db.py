import os

from alembic.config import Config as AlembicConfig
from alembic import command
import click


@click.group()
@click.pass_obj
def db(app):
    """ Manage application database. """

    directory = app.instance['config'].get('MIGRATIONS_ROOT')
    db_uri = app.instance['config'].get_sqlalchemy_dsn()

    config = AlembicConfig(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)
    config.set_main_option('sqlalchemy.url', db_uri)

    app.migrations_config = config


@db.command()
@click.option('-m', '--message', default=None)
@click.option('--autogenerate', default=False, is_flag=True,
              help=('Populate revision script with andidate migration '
                    'operations, based on comparison of database to model'))
@click.option('--sql', default=False, is_flag=True,
              help=('Don`t emit SQL to database - dump to standard '
                    'output instead'))
@click.option('--head', default='head',
              help=('Specify head revision or <branchname>@head to'
                    'base new revision on'))
@click.option('--splice', default=False, is_flag=True,
              help='Allow a non-head revision as the "head" to splice onto')
@click.option('--branch-label', default=None,
              help="Specify a branch label to apply to the new revision")
@click.option('--version-path', default=None,
              help="Specify specific path from config for version file")
@click.option('--rev-id', default=None,
              help='Specify a hardcoded revision id instead of generating one')
@click.pass_obj
def migrate(app, message=None, autogenerate=False, sql=False, head='head',
            splice=False, branch_label=None, version_path=None, rev_id=None):
    """Create new database migration. """
    command.revision(app.migrations_config, message, sql=sql, head=head,
                     autogenerate=autogenerate, splice=splice,
                     branch_label=branch_label, version_path=version_path,
                     rev_id=rev_id)


@db.command()
@click.argument('revisions')
@click.option('-m', '--message', default=None)
@click.option('--branch-label', default=None,
              help='Specify a branch label to apply to the new revision')
@click.option('--rev-id', default=None,
              help='Specify a hardcoded revision id instead of generating one')
@click.pass_obj
def merge(app, revisions='', message=None, branch_label=None, rev_id=None):
    """Merge to revisions together. Creates a new migration file"""
    command.merge(app.migrations_config, revisions, message=message,
                  branch_label=branch_label, rev_id=rev_id)


@db.command()
@click.argument('revision', default='head')
@click.option('--sql', default=False,
              help=('Don`t emit SQl to database - dump to standard '
                    'output instead'))
@click.option('--tag', default=None,
              help='Arbitrary `tag` name - can be used by custom `env.py`')
@click.pass_obj
def upgrade(app, revision='head', sql=False, tag=None):
    """Upgrade to a later version"""
    command.upgrade(app.migrations_config, revision, sql=sql, tag=tag)


@db.command()
@click.argument('revision', default='head')
@click.option('--sql', default=False,
              help=('Don`t emit SQl to database - dump to standard '
                    'output instead'))
@click.option('--tag', default=None,
              help='Arbitrary `tag` name - can be used by custom `env.py`')
@click.pass_obj
def downgrade(app, revision='-1', sql=False, tag=None):
    """Revert to a previous version"""
    command.downgrade(app.migrations_config, revision, sql=sql, tag=tag)


@db.command()
@click.option('-r', '--rev-range', default=None,
              help='Specify a revision range; format is [start]:[end]')
@click.option('-v', '--verbose', default=False, help='Use more verbose output')
@click.pass_obj
def history(app, rev_range=None, verbose=False):
    """List changeset scripts in chronological order."""
    command.history(app.migrations_config, rev_range, verbose=verbose)


@db.command()
@click.option('-v', '--verbose', default=False, help='Use more verbose output')
@click.option('--resolve-dependencies', default=False,
              help='Treat dependency versions as down revisions')
@click.pass_obj
def heads(app, verbose=False, resolve_dependencies=False):
    """Show current available heads """
    command.heads(app.migrations_config, verbose=verbose,
                  resolve_dependencies=resolve_dependencies)


@db.command()
@click.option('-v', '--verbose', default=False, help='Use more verbose output')
@click.pass_obj
def branches(app, verbose=False):
    """Show current branch points"""
    command.branches(app.migrations_config, verbose=verbose)


@db.command()
@click.option('-v', '--verbose', default=False, help='Use more verbose output')
@click.pass_obj
def current(app, verbose=False):
    """Display the current revision for each database."""
    command.current(app.migrations_config, verbose=verbose)
