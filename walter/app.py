import os
import shutil
import argparse
import virtualenv
import logging
from pathlib import Path
from charondb import MySQLManager, LiteManager
from .lib.types import Config, Database, Project
from tabulate import tabulate
import subprocess

BASE_DIR = os.environ['HOME']
PACKAGE_DIR = Path(__file__).parent
CONFIG_TEMPLATE = PACKAGE_DIR / 'config.json'
USER_CONFIG = Path(BASE_DIR) / '.config' / 'walter.json'

if not USER_CONFIG.exists():
    USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_TEMPLATE.exists():
        shutil.copyfile(str(CONFIG_TEMPLATE), str(USER_CONFIG))


class Walter:
    def __init__(self):
        self.PARSE = self.__create_parser()
        self.ARGS = self.PARSE.parse_args()
        self.config = Config(str(USER_CONFIG))
        self.PROJECT_BASE_DIR = os.path.join(
            BASE_DIR, self.config.project_dir)
        self._init_database()
        self._init_logger(self.ARGS.debug)
        if not self.config.init:
            paths = ['project_dir', 'complete_dir', 'incomplete_dir']
            for path in paths:
                dist = os.path.join(BASE_DIR, getattr(self.config, path))
                if not os.path.exists(dist):
                    os.makedirs(dist)
            self.config.init = True
            self.config.write()

    def _init_database(self):
        db: Database = self.config.database
        if db.driver == "mysql":
            self.storage = MySQLManager(username=db.username, password=db.password,
                                        host=db.host, database=db.name, port=db.port, debug=self.ARGS.debug)
        else:
            # For now, use a simple wrapper for LiteManager
            from .lib.db_wrapper import SimpleLiteWrapper
            self.storage = SimpleLiteWrapper(db.name or "walter.db")
        if not self.config.init:
            if db.driver == "mysql":
                database_sql = PACKAGE_DIR / "database.sql"
                if database_sql.exists():
                    with open(str(database_sql), "r") as sql_file:
                        self.storage.import_database(sql_file)
            else:
                # Initialize SQLite database
                self.storage.init_database()

    def _init_logger(self, debug):
        self.logger = logging.Logger("Walter")
        formater = logging.Formatter('%(asctime)s -> %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formater)
        self.logger.addHandler(handler)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def __create_parser(self):
        """
        Create ArgParser
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-p", "--project", help="Name of project of you want do something on it")
        parser.add_argument(
            "-d", "--debug", help="Enable Verbose log", action="store_true")
        subparsers = parser.add_subparsers(
            help='command to run on your project', dest="command", required=True)
        mark = subparsers.add_parser(
            "mark", description="mark project to com or incom")
        mark.add_argument("mark", help="Project mark com or incom",
                          type=str, choices=['incom', 'com'])
        create = subparsers.add_parser(
            "create", description="mark project to com or incom")
        create.add_argument("-l", "--language",
                            help="language of project", required=True)
        subparsers.add_parser(
            "list", description="mark project to com or incom")
        return parser

    def check_arg(self, args):
        getattr(self, args.command)()

    def list(self):
        projects = self.storage.select("project_tbl", ["*"])
        columns = ["id", "name", "language", "completed"]
        projects_list = []
        for project in projects:
            projects_list.append(list(Project(project)))
        print(tabulate(projects_list, columns, "fancy_grid"))

    def create_symlink(self, path, name):
        self.logger.info("Creating symlink")
        dist = os.path.join(BASE_DIR, getattr(
            self.config, "incomplete_dir"), name)
        if os.path.exists(dist):
            self.logger.warning("Symlink is Exists")
        else:
            os.symlink(path, dist)
    def create(self):
        language, name = self.ARGS.language, self.ARGS.project
        path = os.path.join(self.PROJECT_BASE_DIR, name)
        def python():
            venv = os.path.join(path, "venv")
            if not os.path.exists(path):
                self.logger.info("Creating project Directory")
                os.makedirs(path)
            else:
                self.logger.warning("project Directory Exists")
            self.logger.info("Creating project Virtualenv")
            # Use modern virtualenv API
            import subprocess
            subprocess.run([
                "python", "-m", "virtualenv", venv
            ], check=True)
            return True

        def node():
            if not os.path.exists(path):
                self.logger.info("Creating Project Directory")
                os.makedirs(path)
            else:
                self.logger.warning("Project Directory Exists")
            self.logger.info("Yarn init")
            subprocess.Popen(['yarn', 'init', '-y'], shell=False, cwd=path).wait()
            return True

        def go():
            pass

        def php():
            pass

        def lua():
            pass

        if not self.storage.exists("project_tbl", f'name="{name}"'):
            if locals()[language]():
                self.create_symlink(path, name)
                self.storage.insert("project_tbl", ['name', 'language', "complete"],
                                    [name, language, 0])
                self.logger.info("Created")
        else:
            self.logger.error("Project is EXISTS in database!")

    def mark(self):
        def toggle(mark: str, name: str):
            now = "com" if mark == "incom" else "incom"
            dist = os.path.join(BASE_DIR, getattr(self.config, mark), name)
            now_dir = os.path.join(BASE_DIR, getattr(self.config, now), name)
            path = os.path.join(self.PROJECT_BASE_DIR, name)
            user_mark = "Completed" if mark == "com" else "InCompleted"
            if os.path.exists(dist):
                self.logger.warning(f"Project Already Marked: {user_mark}")
                return
            else:
                os.unlink(now_dir)
                os.symlink(path, dist)
                self.logger.info(f"Project Set to: {user_mark}")

        name, user_mark = self.ARGS.project, self.ARGS.mark
        toggle(user_mark, name)


def main():
    walter = Walter()
    walter.check_arg(walter.ARGS)


if __name__ == "__main__":
    main()
