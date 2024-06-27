from wtpy.wrapper import WtDtWrapper
from wtpy.ExtModuleDefs import BaseExtParser, BaseExtDataDumper
from wtpy.WtUtilDefs import singleton


@singleton
class WtDtEngine:

    def __init__(self):
        self.__wrapper__ = WtDtWrapper(self)  # api接口转换器
        self.__ext_parsers__ = dict()  # 外接的行情接入模块
        self.__ext_dumpers__ = dict()  # 扩展数据Dumper

    def initialize(self, cfgfile: str = "dtcfg.yaml", logprofile: str = "logcfgdt.yaml"):
        """
        数据引擎初始化\n
        @cfgfile    配置文件\n
        @logprofile 日志模块配置文件
        """
        self.__wrapper__.initialize(cfgfile, logprofile)

    def run(self, bAsync: bool = False):
        """
        运行数据引擎
        @bAsync 是否异步，异步则立即返回，默认False
        """
        self.__wrapper__.run_datakit(bAsync)

    def add_exetended_parser(self, parser: BaseExtParser):
        """
        添加扩展parser
        """
        ids = parser.id()
        if ids not in self.__ext_parsers__:
            self.__ext_parsers__[ids] = parser
            if not self.__wrapper__.create_extended_parser(ids):
                self.__ext_parsers__.pop(ids)

    def get_extended_parser(self, ids: str) -> BaseExtParser:
        """
        根据id获取扩展parser
        """
        if ids not in self.__ext_parsers__:
            return None
        return self.__ext_parsers__[ids]

    def push_quote_from_extended_parser(self, ids: str, newTick, uProcFlag: int):
        """
        向底层推送tick数据

        @id parserid
        @newTick    POINTER(WTSTickStruct)
        @uProcFlag  预处理标记，0-不处理，1-切片，2-累加
        """
        self.__wrapper__.push_quote_from_exetended_parser(ids, newTick, uProcFlag)

    def add_extended_data_dumper(self, dumper: BaseExtDataDumper):
        """
        添加扩展dumper
        """
        ids = dumper.id()
        if ids not in self.__ext_dumpers__:
            self.__ext_dumpers__[ids] = dumper
            if not self.__wrapper__.create_extended_dumper(ids):
                self.__ext_dumpers__.pop(ids)
        self.__wrapper__.register_extended_data_dumper()

    def get_extended_data_dumper(self, ids: str) -> BaseExtDataDumper:
        """
        根据id获取扩展dumper
        """
        if ids not in self.__ext_dumpers__:
            return None
        return self.__ext_dumpers__[ids]
