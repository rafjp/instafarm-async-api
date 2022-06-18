from enum import Enum, auto


class MBEnvironment(Enum):
    DEVELOPMENT = auto()
    PRODUCTION = auto()

    _ignore_ = ["current_environment"]
    current_environment = DEVELOPMENT

    @staticmethod
    def on_env(environment: "MBEnvironment"):
        return MBEnvironment.current_environment == environment

    @staticmethod
    def on_prod():
        return MBEnvironment.current_environment == MBEnvironment.PRODUCTION

    @staticmethod
    def on_dev():
        return MBEnvironment.current_environment == MBEnvironment.DEVELOPMENT

    @staticmethod
    def set_env(environment: "MBEnvironment"):
        MBEnvironment.current_environment = environment

    @staticmethod
    def get_env():
        return MBEnvironment.current_environment
