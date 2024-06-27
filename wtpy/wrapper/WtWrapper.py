from ctypes import c_int32, cdll, c_char_p, c_bool, c_ulong, c_uint64, c_double, POINTER, sizeof, addressof
from wtpy.WtCoreDefs import CB_EXECUTER_CMD, CB_EXECUTER_INIT, CB_PARSER_EVENT, CB_PARSER_SUBCMD
from wtpy.WtCoreDefs import CB_STRATEGY_INIT, CB_STRATEGY_TICK, CB_STRATEGY_CALC, CB_STRATEGY_BAR, CB_STRATEGY_GET_BAR, \
    CB_STRATEGY_GET_TICK, CB_STRATEGY_GET_POSITION
from wtpy.WtCoreDefs import EVENT_PARSER_CONNECT, EVENT_PARSER_DISCONNECT, EVENT_PARSER_INIT, EVENT_PARSER_RELEASE
from wtpy.WtCoreDefs import CB_HFTSTRA_CHNL_EVT, CB_HFTSTRA_ENTRUST, CB_HFTSTRA_ORD, CB_HFTSTRA_TRD, CB_SESSION_EVENT, \
    CB_HFTSTRA_POSITION
from wtpy.WtCoreDefs import CB_HFTSTRA_ORDQUE, CB_HFTSTRA_ORDDTL, CB_HFTSTRA_TRANS, CB_HFTSTRA_GET_ORDQUE, \
    CB_HFTSTRA_GET_ORDDTL, CB_HFTSTRA_GET_TRANS
from wtpy.WtCoreDefs import CHNL_EVENT_READY, CHNL_EVENT_LOST, CB_ENGINE_EVENT
from wtpy.WtCoreDefs import FUNC_LOAD_HISBARS, FUNC_LOAD_HISTICKS, FUNC_LOAD_ADJFACTS
from wtpy.WtCoreDefs import EVENT_ENGINE_INIT, EVENT_SESSION_BEGIN, EVENT_SESSION_END, EVENT_ENGINE_SCHDL
from wtpy.WtCoreDefs import WTSTickStruct, WTSBarStruct, WTSOrdQueStruct, WTSOrdDtlStruct, WTSTransStruct
from wtpy.WtUtilDefs import singleton
from .PlatformHelper import PlatformHelper as ph
import os


# Python对接C接口的库
@singleton
class WtWrapper:
    """
    Wt平台C接口底层对接模块
    """

    # api可以作为公共变量
    api = None
    ver = "Unknown"

    # 构造函数，传入动态库名
    def __init__(self, engine):
        self._engine = engine
        paths = os.path.split(__file__)
        dllname = ph.getModule("WtPorter")
        a = (paths[:-1] + (dllname,))
        _path = os.path.join(*a)
        self.api = cdll.LoadLibrary(_path)

        self.api.get_version.restype = c_char_p
        self.api.cta_get_last_entertime.restype = c_uint64
        self.api.cta_get_first_entertime.restype = c_uint64
        self.api.cta_get_detail_entertime.restype = c_uint64
        self.api.cta_enter_long.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_enter_short.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_exit_long.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_exit_short.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.api.cta_set_position.argtypes = [c_ulong, c_char_p, c_double, c_char_p, c_double, c_double]
        self.ver = bytes.decode(self.api.get_version())

        self.api.cta_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.cta_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.cta_load_userdata.restype = c_char_p

        self.api.cta_get_position.restype = c_double
        self.api.cta_get_position_profit.restype = c_double
        self.api.cta_get_position_avgpx.restype = c_double
        self.api.cta_get_detail_cost.restype = c_double
        self.api.cta_get_detail_profit.restype = c_double
        self.api.cta_get_price.restype = c_double
        self.api.cta_get_fund_data.restype = c_double

        self.api.sel_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.sel_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.sel_load_userdata.restype = c_char_p
        self.api.sel_get_position.restype = c_double
        self.api.sel_set_position.argtypes = [c_ulong, c_char_p, c_double, c_char_p]
        self.api.sel_get_price.restype = c_double

        self.api.hft_save_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.hft_load_userdata.argtypes = [c_ulong, c_char_p, c_char_p]
        self.api.hft_load_userdata.restype = c_char_p
        self.api.hft_get_position.restype = c_double
        self.api.hft_get_position_profit.restype = c_double
        self.api.hft_get_undone.restype = c_double
        self.api.hft_get_price.restype = c_double

        self.api.hft_buy.restype = c_char_p
        self.api.hft_buy.argtypes = [c_ulong, c_char_p, c_double, c_double, c_char_p, c_int32]
        self.api.hft_sell.restype = c_char_p
        self.api.hft_sell.argtypes = [c_ulong, c_char_p, c_double, c_double, c_char_p, c_int32]
        self.api.hft_cancel_all.restype = c_char_p

        self.api.create_ext_parser.restype = c_bool
        self.api.create_ext_parser.argtypes = [c_char_p]

    def on_engine_event(self, evtid: int, evtDate: int, evtTime: int):
        engine = self._engine
        if evtid == EVENT_ENGINE_INIT:
            engine.on_init()
        elif evtid == EVENT_ENGINE_SCHDL:
            engine.on_schedule(evtDate, evtTime)
        elif evtid == EVENT_SESSION_BEGIN:
            engine.on_session_begin(evtDate)
        elif evtid == EVENT_SESSION_END:
            engine.on_session_end(evtDate)
        return

    # 回调函数
    def on_stra_init(self, ids: int):
        engine = self._engine
        ctx = engine.get_context(ids)
        if ctx is not None:
            ctx.on_init()
        return

    def on_session_event(self, ids: int, udate: int, isBegin: bool):
        engine = self._engine
        ctx = engine.get_context(ids)
        if ctx is not None:
            if isBegin:
                ctx.on_session_begin(udate)
            else:
                ctx.on_session_end(udate)
        return

    def on_stra_tick(self, ids: int, stdCode: str, newTick: POINTER(WTSTickStruct)):
        engine = self._engine
        ctx = engine.get_context(ids)

        realTick = newTick.contents
        if ctx is not None:
            ctx.on_tick(bytes.decode(stdCode), realTick.to_tuple())
        return

    def on_stra_calc(self, ids: int, curDate: int, curTime: int):
        engine = self._engine
        ctx = engine.get_context(ids)
        if ctx is not None:
            ctx.on_calculate()
        return

    def on_stra_bar(self, ids: int, stdCode: str, period: str, newBar: POINTER(WTSBarStruct)):
        period = bytes.decode(period)
        engine = self._engine
        ctx = engine.get_context(ids)
        newBar = newBar.contents
        if ctx is not None:
            ctx.on_bar(bytes.decode(stdCode), period, newBar.to_tuple(period[0] == 'd'))
        return

    def on_stra_get_bar(self, ids: int, stdCode: str, period: str, curBar: POINTER(WTSBarStruct), count: int,
                        isLast: bool):
        """
        获取K线回调，该回调函数因为是python主动发起的，需要同步执行，所以不走事件推送
        @ids     策略ids
        @stdCode   合约代码
        @period K线周期
        @curBar 最新一条K线
        @isLast 是否是最后一条
        """
        engine = self._engine
        ctx = engine.get_context(ids)
        period = bytes.decode(period)

        bsSize = sizeof(WTSBarStruct)
        addr = addressof(curBar.contents)  # 获取内存地址
        isDay = period[0] == 'd'

        bars = [None] * count  # 预先分配list的长度
        for i in range(count):
            realBar = WTSBarStruct.from_address(addr)  # 从内存中直接解析成WTSBarStruct
            bars[i] = realBar.to_tuple(isDay)
            addr += bsSize

        if ctx is not None:
            ctx.on_getbars(bytes.decode(stdCode), period, bars)
        return

    def on_stra_get_tick(self, ids: int, stdCode: str, curTick: POINTER(WTSTickStruct), count: int, isLast: bool):
        """
        获取Tick回调，该回调函数因为是python主动发起的，需要同步执行，所以不走事件推送
        @ids         策略ids
        @stdCode       合约代码
        @curTick    最新一笔Tick
        @isLast     是否是最后一条
        """
        engine = self._engine
        ctx = engine.get_context(ids)

        tsSize = sizeof(WTSTickStruct)
        addr = addressof(curTick.contents)  # 获取内存地址
        ticks = [None] * count  # 预先分配list的长度
        for idx in range(count):
            realTick = WTSTickStruct.from_address(addr)  # 从内存中直接解析成WTSTickStruct
            ticks[idx] = realTick.to_tuple()
            addr += tsSize

        if ctx is not None:
            ctx.on_getticks(bytes.decode(stdCode), ticks)
        return

    def on_stra_get_position(self, ids: int, stdCode: str, qty: float, frozen: float):
        engine = self._engine
        ctx = engine.get_context(ids)
        if ctx is not None:
            ctx.on_getpositions(bytes.decode(stdCode), qty, frozen)

    def on_hftstra_channel_evt(self, ids: int, trader: str, evtid: int):
        engine = self._engine
        ctx = engine.get_context(ids)

        if evtid == CHNL_EVENT_READY:
            ctx.on_channel_ready()
        elif evtid == CHNL_EVENT_LOST:
            ctx.on_channel_lost()

    def on_hftstra_order(self, ids: int, localid: int, stdCode: str, isBuy: bool, totalQty: float, leftQty: float,
                         price: float, isCanceled: bool, userTag: str):
        stdCode = bytes.decode(stdCode)
        userTag = bytes.decode(userTag)
        engine = self._engine
        ctx = engine.get_context(ids)
        ctx.on_order(localid, stdCode, isBuy, totalQty, leftQty, price, isCanceled, userTag)

    def on_hftstra_trade(self, ids: int, localid: int, stdCode: str, isBuy: bool, qty: float, price: float,
                         userTag: str):
        stdCode = bytes.decode(stdCode)
        userTag = bytes.decode(userTag)
        engine = self._engine
        ctx = engine.get_context(ids)
        ctx.on_trade(localid, stdCode, isBuy, qty, price, userTag)

    def on_hftstra_entrust(self, ids: int, localid: int, stdCode: str, bSucc: bool, message: str, userTag: str):
        stdCode = bytes.decode(stdCode)
        message = bytes.decode(message, "gbk")
        userTag = bytes.decode(userTag)
        engine = self._engine
        ctx = engine.get_context(ids)
        ctx.on_entrust(localid, stdCode, bSucc, message, userTag)

    def on_hftstra_position(self, ids: int, stdCode: str, isLong: bool, prevol: float, preavail: float, newvol: float,
                            newavail: float):
        stdCode = bytes.decode(stdCode)
        engine = self._engine
        ctx = engine.get_context(ids)
        ctx.on_position(stdCode, isLong, prevol, preavail, newvol, newavail)

    def on_hftstra_order_queue(self, ids: int, stdCode: str, newOrdQue: POINTER(WTSOrdQueStruct)):
        stdCode = bytes.decode(stdCode)
        engine = self._engine
        ctx = engine.get_context(ids)
        newOrdQue = newOrdQue.contents

        if ctx is not None:
            ctx.on_order_queue(stdCode, newOrdQue.to_tuple())

    def on_hftstra_get_order_queue(self, ids: int, stdCode: str, newOrdQue: POINTER(WTSOrdQueStruct), count: int,
                                   isLast: bool):
        engine = self._engine
        ctx = engine.get_context(ids)
        szItem = sizeof(WTSOrdQueStruct)
        addr = addressof(newOrdQue)
        item_list = [None] * count
        for i in range(count):
            realOrdQue = WTSOrdQueStruct.from_address(addr)
            item_list[i] = realOrdQue.to_tuple()
            addr += szItem

        if ctx is not None:
            ctx.on_get_order_queue(bytes.decode(stdCode), item_list)

    def on_hftstra_order_detail(self, ids: int, stdCode: str, newOrdDtl: POINTER(WTSOrdDtlStruct)):
        engine = self._engine
        ctx = engine.get_context(ids)
        newOrdDtl = newOrdDtl.contents

        if ctx is not None:
            ctx.on_order_detail(stdCode, newOrdDtl.to_tuple())

    def on_hftstra_get_order_detail(self, ids: int, stdCode: str, newOrdDtl: POINTER(WTSOrdDtlStruct), count: int,
                                    isLast: bool):
        engine = self._engine
        ctx = engine.get_context(ids)
        szItem = sizeof(WTSOrdDtlStruct)
        addr = addressof(newOrdDtl)
        item_list = [None] * count
        for i in range(count):
            realOrdDtl = WTSOrdDtlStruct.from_address(addr)
            item_list[i] = realOrdDtl.to_tuple()
            addr += szItem

        if ctx is not None:
            ctx.on_get_order_detail(bytes.decode(stdCode), item_list)

    def on_hftstra_transaction(self, ids: int, stdCode: str, newTrans: POINTER(WTSTransStruct)):
        engine = self._engine
        ctx = engine.get_context(ids)
        newTrans = newTrans.contents

        if ctx is not None:
            ctx.on_transaction(stdCode, newTrans.to_tuple())

    def on_hftstra_get_transaction(self, ids: int, stdCode: str, newTrans: POINTER(WTSTransStruct), count: int,
                                   isLast: bool):
        engine = self._engine
        ctx = engine.get_context(ids)
        szTrans = sizeof(WTSTransStruct)
        addr = addressof(newTrans)
        trans_list = [None] * count
        for i in range(count):
            realTrans = WTSTransStruct.from_address(addr)
            curTrans = dict()
            curTrans["time"] = realTrans.action_date * 1000000000 + realTrans.action_time
            curTrans["index"] = realTrans.index
            curTrans["ttype"] = realTrans.ttype
            curTrans["side"] = realTrans.side
            curTrans["price"] = realTrans.price
            curTrans["volume"] = realTrans.volume
            curTrans["askorder"] = realTrans.askorder
            curTrans["bidorder"] = realTrans.bidorder
            trans_list[i] = curTrans
            addr += szTrans

        if ctx is not None:
            ctx.on_get_transaction(bytes.decode(stdCode), trans_list, isLast)

    def on_parser_event(self, evtId: int, ids: str):
        ids = bytes.decode(ids)
        engine = self._engine
        parser = engine.get_extended_parser(ids)
        if parser is None:
            return

        if evtId == EVENT_PARSER_INIT:
            parser.init(engine)
        elif evtId == EVENT_PARSER_CONNECT:
            parser.connect()
        elif evtId == EVENT_PARSER_DISCONNECT:
            parser.disconnect()
        elif evtId == EVENT_PARSER_RELEASE:
            parser.release()

    def on_parser_sub(self, ids: str, fullCode: str, isForSub: bool):
        ids = bytes.decode(ids)
        engine = self._engine
        parser = engine.get_extended_parser(ids)
        if parser is None:
            return
        fullCode = bytes.decode(fullCode)
        if isForSub:
            parser.subscribe(fullCode)
        else:
            parser.unsubscribe(fullCode)

    def on_executer_init(self, ids: str):
        engine = self._engine
        executer = engine.get_extended_executer(ids)
        if executer is None:
            return

        executer.init()

    def on_executer_cmd(self, ids: str, stdCode: str, targetPos: float):
        engine = self._engine
        executer = engine.get_extended_executer(ids)
        if executer is None:
            return

        executer.set_position(stdCode, targetPos)

    def on_load_fnl_his_bars(self, stdCode: str, period: str):
        engine = self._engine
        loader = engine.get_extended_data_loader()
        if loader is None:
            return False

        # feed_raw_bars(WTSBarStruct* bars, WtUInt32 count);
        loader.load_final_his_bars(bytes.decode(stdCode), bytes.decode(period), self.api.feed_raw_bars)

    def on_load_raw_his_bars(self, stdCode: str, period: str):
        engine = self._engine
        loader = engine.get_extended_data_loader()
        if loader is None:
            return False

        # feed_raw_bars(WTSBarStruct* bars, WtUInt32 count);
        loader.load_raw_his_bars(bytes.decode(stdCode), bytes.decode(period), self.api.feed_raw_bars)

    def feed_adj_factors(self, stdCode: str, dates: list, factors: list):
        stdCode = bytes(stdCode, encoding="utf8")
        """
        TODO 这里类型要转一下! 底层接口是传数组的
        feed_adj_factors(WtString stdCode, WtUInt32* dates, double* factors, WtUInt32 count)
        """
        self.api.feed_adj_factors(stdCode, dates, factors, len(dates))

    def on_load_adj_factors(self, stdCode: str) -> bool:
        engine = self._engine
        loader = engine.get_extended_data_loader()
        if loader is None:
            return False

        stdCode = bytes.decode(stdCode)
        return loader.load_adj_factors(stdCode, self.feed_adj_factors)

    def on_load_his_ticks(self, stdCode: str, uDate: int):
        engine = self._engine
        loader = engine.get_extended_data_loader()
        if loader is None:
            return False

        # feed_raw_ticks(WTSTickStruct* ticks, WtUInt32 count);
        loader.load_his_ticks(bytes.decode(stdCode), uDate, self.api.feed_raw_ticks)

    def write_log(self, level, message: str, catName: str = ""):
        self.api.write_log(level, bytes(message, encoding="utf8").decode('utf-8').encode('gbk'),
                           bytes(catName, encoding="utf8"))

    ### 实盘和回测有差异 ###
    def run(self, bAsync: bool = True):
        self.api.run_porter(bAsync)

    def release(self):
        self.api.release_porter()

    def config(self, cfgfile: str = 'config.yaml', isFile: bool = True):
        self.api.config_porter(bytes(cfgfile, encoding="utf8"), isFile)

    def create_extended_parser(self, ids: str) -> bool:
        return self.api.create_ext_parser(bytes(ids, encoding="utf8"))

    def create_extended_executer(self, ids: str) -> bool:
        return self.api.create_ext_executer(bytes(ids, encoding="utf8"))

    def push_quote_from_exetended_parser(self, ids: str, newTick: POINTER(WTSTickStruct), uProcFlag: int = 1):
        return self.api.parser_push_quote(bytes(ids, encoding="utf8"), newTick, uProcFlag)

    def register_extended_module_callbacks(self, ):
        self.cb_parser_event = CB_PARSER_EVENT(self.on_parser_event)
        self.cb_parser_subcmd = CB_PARSER_SUBCMD(self.on_parser_sub)
        self.cb_executer_init = CB_EXECUTER_INIT(self.on_executer_init)
        self.cb_executer_cmd = CB_EXECUTER_CMD(self.on_executer_cmd)

        self.api.register_parser_callbacks(self.cb_parser_event, self.cb_parser_subcmd)
        self.api.register_exec_callbacks(self.cb_executer_init, self.cb_executer_cmd)

    def register_extended_data_loader(self):
        """
        注册扩展历史数据加载器
        """

        self.cb_load_fnlbars = FUNC_LOAD_HISBARS(self.on_load_fnl_his_bars)
        self.cb_load_rawbars = FUNC_LOAD_HISBARS(self.on_load_raw_his_bars)
        self.cb_load_histicks = FUNC_LOAD_HISTICKS(self.on_load_his_ticks)
        self.cb_load_adjfacts = FUNC_LOAD_ADJFACTS(self.on_load_adj_factors)
        self.api.register_ext_data_loader(self.cb_load_fnlbars, self.cb_load_rawbars, self.cb_load_adjfacts,
                                          self.cb_load_histicks)

        self.cb_load_hisbars = FUNC_LOAD_HISBARS(self.on_load_his_bars)
        self.cb_load_histicks = FUNC_LOAD_HISTICKS(self.on_load_his_ticks)
        self.api.register_ext_data_loader(self.cb_load_fnlbars, self.cb_load_rawbars, self.cb_load_adjfacts,
                                          self.cb_load_histicks)

    # ## 实盘和回测有差异 ###
    def initialize_cta(self, logCfg: str = "logcfg.yaml", isFile: bool = True, genDir: str = 'generated'):
        """
        C接口初始化
        """
        self.cb_stra_init = CB_STRATEGY_INIT(self.on_stra_init)
        self.cb_stra_tick = CB_STRATEGY_TICK(self.on_stra_tick)
        self.cb_stra_calc = CB_STRATEGY_CALC(self.on_stra_calc)
        self.cb_stra_bar = CB_STRATEGY_BAR(self.on_stra_bar)
        self.cb_session_event = CB_SESSION_EVENT(self.on_session_event)

        self.cb_engine_event = CB_ENGINE_EVENT(self.on_engine_event)
        try:
            self.api.register_evt_callback(self.cb_engine_event)
            self.api.register_cta_callbacks(self.cb_stra_init, self.cb_stra_tick, self.cb_stra_calc, self.cb_stra_bar,
                                            self.cb_session_event)
            self.api.init_porter(bytes(logCfg, encoding="utf8"), isFile, bytes(genDir, encoding="utf8"))
            self.register_extended_module_callbacks()
        except OSError as oe:
            print(oe)

        self.write_log(102, "WonderTrader CTA production framework initialzied，version: %s" % self.ver)

    def initialize_hft(self, logCfg: str = "logcfg.yaml", isFile: bool = True, genDir: str = 'generated'):
        """
        C接口初始化
        """
        self.cb_stra_init = CB_STRATEGY_INIT(self.on_stra_init)
        self.cb_stra_tick = CB_STRATEGY_TICK(self.on_stra_tick)
        self.cb_stra_bar = CB_STRATEGY_BAR(self.on_stra_bar)
        self.cb_session_event = CB_SESSION_EVENT(self.on_session_event)

        self.cb_hftstra_chnl_evt = CB_HFTSTRA_CHNL_EVT(self.on_hftstra_channel_evt)
        self.cb_hftstra_order = CB_HFTSTRA_ORD(self.on_hftstra_order)
        self.cb_hftstra_trade = CB_HFTSTRA_TRD(self.on_hftstra_trade)
        self.cb_hftstra_entrust = CB_HFTSTRA_ENTRUST(self.on_hftstra_entrust)
        self.cb_hftstra_position = CB_HFTSTRA_POSITION(self.on_hftstra_position)
        self.cb_hftstra_orddtl = CB_HFTSTRA_ORDDTL(self.on_hftstra_order_detail)
        self.cb_hftstra_ordque = CB_HFTSTRA_ORDQUE(self.on_hftstra_order_queue)
        self.cb_hftstra_trans = CB_HFTSTRA_TRANS(self.on_hftstra_transaction)

        self.cb_engine_event = CB_ENGINE_EVENT(self.on_engine_event)
        try:
            self.api.register_evt_callback(self.cb_engine_event)
            self.api.register_hft_callbacks(self.cb_stra_init, self.cb_stra_tick, self.cb_stra_bar,
                                            self.cb_hftstra_chnl_evt, self.cb_hftstra_order, self.cb_hftstra_trade,
                                            self.cb_hftstra_entrust,
                                            self.cb_hftstra_orddtl, self.cb_hftstra_ordque, self.cb_hftstra_trans,
                                            self.cb_session_event, self.cb_hftstra_position)
            self.api.init_porter(bytes(logCfg, encoding="utf8"), isFile, bytes(genDir, encoding="utf8"))
        except OSError as oe:
            print(oe)

        self.write_log(102, "WonderTrader HFT production framework initialzied，version: %s" % self.ver)

    def initialize_sel(self, logCfg: str = "logcfg.yaml", isFile: bool = True, genDir: str = 'generated'):
        """
        C接口初始化
        """
        self.cb_stra_init = CB_STRATEGY_INIT(self.on_stra_init)
        self.cb_stra_tick = CB_STRATEGY_TICK(self.on_stra_tick)
        self.cb_stra_calc = CB_STRATEGY_CALC(self.on_stra_calc)
        self.cb_stra_bar = CB_STRATEGY_BAR(self.on_stra_bar)
        self.cb_session_event = CB_SESSION_EVENT(self.on_session_event)

        self.cb_engine_event = CB_ENGINE_EVENT(self.on_engine_event)

        try:
            self.api.register_evt_callback(self.cb_engine_event)
            self.api.register_sel_callbacks(self.cb_stra_init, self.cb_stra_tick, self.cb_stra_calc, self.cb_stra_bar,
                                            self.cb_session_event)
            self.api.init_porter(bytes(logCfg, encoding="utf8"), isFile, bytes(genDir, encoding="utf8"))
            self.register_extended_module_callbacks()
        except OSError as oe:
            print(oe)

        self.write_log(102, "WonderTrader SEL production framework initialzied，version: %s" % self.ver)

    def cta_enter_long(self, ids: int, stdCode: str, qty: float, usertag: str, limitprice: float = 0.0,
                       stopprice: float = 0.0):
        """
        开多
        @ids         策略ids
        @stdCode    合约代码
        @qty        手数，大于等于0
        """
        self.api.cta_enter_long(ids, bytes(stdCode, encoding="utf8"), qty, bytes(usertag, encoding="utf8"), limitprice,
                                stopprice)

    def cta_exit_long(self, ids: int, stdCode: str, qty: float, usertag: str, limitprice: float = 0.0,
                      stopprice: float = 0.0):
        """
        平多
        @ids         策略ids
        @stdCode    合约代码
        @qty        手数，大于等于0
        """
        self.api.cta_exit_long(ids, bytes(stdCode, encoding="utf8"), qty, bytes(usertag, encoding="utf8"), limitprice,
                               stopprice)

    def cta_enter_short(self, ids: int, stdCode: str, qty: float, usertag: str, limitprice: float = 0.0,
                        stopprice: float = 0.0):
        """
        开空
        @ids         策略ids
        @stdCode    合约代码
        @qty        手数，大于等于0
        """
        self.api.cta_enter_short(ids, bytes(stdCode, encoding="utf8"), qty, bytes(usertag, encoding="utf8"), limitprice,
                                 stopprice)

    def cta_exit_short(self, ids: int, stdCode: str, qty: float, usertag: str, limitprice: float = 0.0,
                       stopprice: float = 0.0):
        """
        平空
        @ids         策略ids
        @stdCode    合约代码
        @qty        手数，大于等于0
        """
        self.api.cta_exit_short(ids, bytes(stdCode, encoding="utf8"), qty, bytes(usertag, encoding="utf8"), limitprice,
                                stopprice)

    def cta_get_bars(self, ids: int, stdCode: str, period: str, count: int, isMain: bool):
        """
        读取K线
        @ids         策略ids
        @stdCode    合约代码
        @period     周期，如m1/m3/d1等
        @count      条数
        @isMain     是否主K线
        """
        return self.api.cta_get_bars(ids, bytes(stdCode, encoding="utf8"), bytes(period, encoding="utf8"), count, isMain,
                                     CB_STRATEGY_GET_BAR(self.on_stra_get_bar))

    def cta_get_ticks(self, ids: int, stdCode: str, count: int):
        """
        读取Tick
        @ids         策略ids
        @stdCode    合约代码
        @count      条数
        """
        return self.api.cta_get_ticks(ids, bytes(stdCode, encoding="utf8"), count,
                                      CB_STRATEGY_GET_TICK(self.on_stra_get_tick))

    def cta_get_position_profit(self, ids: int, stdCode: str):
        """
        获取浮动盈亏
        @ids         策略ids
        @stdCode    合约代码
        @return     指定合约的浮动盈亏
        """
        return self.api.cta_get_position_profit(ids, bytes(stdCode, encoding="utf8"))

    def cta_get_position_avgpx(self, ids: int, stdCode: str):
        """
        获取持仓均价
        @ids         策略ids
        @stdCode    合约代码
        @return     指定合约的持仓均价
        """
        return self.api.cta_get_position_avgpx(ids, bytes(stdCode, encoding="utf8"))

    def cta_get_all_position(self, ids: int):
        """
        获取全部持仓
        @ids     策略ids
        """
        return self.api.cta_get_all_position(ids, CB_STRATEGY_GET_POSITION(self.on_stra_get_position))

    def cta_get_position(self, ids: int, stdCode: str, bonlyvalid: bool = False, usertag: str = ""):
        """
        获取持仓
        @ids     策略ids
        @stdCode    合约代码
        @bonlyvalid 只读可用持仓，默认为False
        @usertag    进场标记，如果为空则获取该合约全部持仓
        @return 指定合约的持仓手数，正为多，负为空
        """
        return self.api.cta_get_position(ids, bytes(stdCode, encoding="utf8"), bonlyvalid,
                                         bytes(usertag, encoding="utf8"))

    def cta_get_fund_data(self, ids: int, flag: int) -> float:
        """
        获取资金数据
        @ids     策略ids
        @flag   0-动态权益，1-总平仓盈亏，2-总浮动盈亏，3-总手续费
        @return 资金数据
        """
        return self.api.cta_get_fund_data(ids, flag)

    def cta_get_price(self, stdCode: str) -> float:
        """
        @stdCode   合约代码
        @return     指定合约的最新价格 
        """
        return self.api.cta_get_price(bytes(stdCode, encoding="utf8"))

    def cta_set_position(self, ids: int, stdCode: str, qty: float, usertag: str = "", limitprice: float = 0.0,
                         stopprice: float = 0.0):
        """
        设置目标仓位
        @ids         策略ids
        @stdCode    合约代码
        @qty        目标仓位，正为多，负为空
        """
        self.api.cta_set_position(ids, bytes(stdCode, encoding="utf8"), qty, bytes(usertag, encoding="utf8"), limitprice,
                                  stopprice)

    def cta_get_tdate(self) -> int:
        """
        获取当前交易日
        @return    当前交易日
        """
        return self.api.cta_get_tdate()

    def cta_get_date(self) -> int:
        """
        获取当前日期
        @return    当前日期 
        """
        return self.api.cta_get_date()

    def cta_get_time(self) -> int:
        """
        获取当前时间
        @return    当前时间 
        """
        return self.api.cta_get_time()

    def cta_get_first_entertime(self, ids: int, stdCode: str) -> int:
        """
        获取当前持仓的首次进场时间
        @stdCode    合约代码
        @return     进场时间，格式如201907260932 
        """
        return self.api.cta_get_first_entertime(ids, bytes(stdCode, encoding="utf8"))

    def cta_get_last_entertime(self, ids: int, stdCode: str) -> int:
        """
        获取当前持仓的最后进场时间
        @stdCode    合约代码
        @return     进场时间，格式如201907260932 
        """
        return self.api.cta_get_last_entertime(ids, bytes(stdCode, encoding="utf8"))

    def cta_get_last_exittime(self, ids: int, stdCode: str) -> int:
        """
        获取当前持仓的最后出场时间
        @stdCode    合约代码
        @return     进场时间，格式如201907260932 
        """
        return self.api.cta_get_last_exittime(ids, bytes(stdCode, encoding="utf8"))

    def cta_log_text(self, ids: int, message: str):
        """
        日志输出
        @ids         策略ids
        @message    日志内容
        """
        self.api.cta_log_text(ids, bytes(message, encoding="utf8").decode('utf-8').encode('gbk'))

    def cta_get_detail_entertime(self, ids: int, stdCode: str, usertag: str) -> int:
        """
        获取指定标记的持仓的进场时间
        @ids         策略ids
        @stdCode    合约代码
        @usertag    进场标记
        @return     进场时间，格式如201907260932 
        """
        return self.api.cta_get_detail_entertime(ids, bytes(stdCode, encoding="utf8"), bytes(usertag, encoding="utf8"))

    def cta_get_detail_cost(self, ids: int, stdCode: str, usertag: str) -> float:
        """
        获取指定标记的持仓的开仓价
        @ids         策略ids
        @stdCode    合约代码
        @usertag    进场标记
        @return     开仓价 
        """
        return self.api.cta_get_detail_cost(ids, bytes(stdCode, encoding="utf8"), bytes(usertag, encoding="utf8"))

    def cta_get_detail_profit(self, ids: int, stdCode: str, usertag: str, flag: int):
        """
        获取指定标记的持仓的盈亏
        @ids         策略ids
        @stdCode       合约代码
        @usertag    进场标记
        @flag       盈亏记号，0-浮动盈亏，1-最大浮盈，2-最大亏损（负数）
        @return     盈亏 
        """
        return self.api.cta_get_detail_profit(ids, bytes(stdCode, encoding="utf8"), bytes(usertag, encoding="utf8"),
                                              flag)

    def cta_save_user_data(self, ids: int, key: str, val: str):
        """
        保存用户数据
        @ids         策略ids
        @key        数据名
        @val        数据值
        """
        self.api.cta_save_userdata(ids, bytes(key, encoding="utf8"), bytes(val, encoding="utf8"))

    def cta_load_user_data(self, ids: int, key: str, defVal: str = ""):
        """
        加载用户数据
        @ids         策略ids
        @key        数据名
        @defVal     默认值
        """
        ret = self.api.cta_load_userdata(ids, bytes(key, encoding="utf8"), bytes(defVal, encoding="utf8"))
        return bytes.decode(ret)

    def cta_sub_ticks(self, ids: int, stdCode: str):
        """
        订阅行情
        @ids         策略ids
        @stdCode    品种代码
        """
        self.api.cta_sub_ticks(ids, bytes(stdCode, encoding="utf8"))

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    """SEL接口"""

    def sel_get_bars(self, ids: int, stdCode: str, period: str, count: int):
        """
        读取K线
        @ids     策略ids
        @stdCode   合约代码
        @period 周期，如m1/m3/d1等
        @count  条数
        """
        return self.api.sel_get_bars(ids, bytes(stdCode, encoding="utf8"), bytes(period, encoding="utf8"), count,
                                     CB_STRATEGY_GET_BAR(self.on_stra_get_bar))

    def sel_get_ticks(self, ids: int, stdCode: str, count: int):
        """
        读取Tick
        @ids     策略ids
        @stdCode   合约代码
        @count  条数
        """
        return self.api.sel_get_ticks(ids, bytes(stdCode, encoding="utf8"), count,
                                      CB_STRATEGY_GET_TICK(self.on_stra_get_tick))

    def sel_save_user_data(self, ids: int, key: str, val: str):
        """
        保存用户数据
        @ids         策略ids
        @key        数据名
        @val        数据值
        """
        self.api.sel_save_userdata(ids, bytes(key, encoding="utf8"), bytes(val, encoding="utf8"))

    def sel_load_user_data(self, ids: int, key: str, defVal: str = ""):
        """
        加载用户数据
        @ids         策略ids
        @key        数据名
        @defVal     默认值
        """
        ret = self.api.sel_load_userdata(ids, bytes(key, encoding="utf8"), bytes(defVal, encoding="utf8"))
        return bytes.decode(ret)

    def sel_get_all_position(self, ids: int):
        """
        获取全部持仓
        @ids     策略ids
        """
        return self.api.sel_get_all_position(ids, CB_STRATEGY_GET_POSITION(self.on_stra_get_position))

    def sel_get_position(self, ids: int, stdCode: str, bonlyvalid: bool = False, usertag: str = ""):
        """
        获取持仓
        @ids     策略ids
        @stdCode   合约代码
        @usertag    进场标记，如果为空则获取该合约全部持仓
        @return 指定合约的持仓手数，正为多，负为空
        """
        return self.api.sel_get_position(ids, bytes(stdCode, encoding="utf8"), bonlyvalid,
                                         bytes(usertag, encoding="utf8"))

    def sel_get_price(self, stdCode: str):
        """
        @stdCode   合约代码
        @return 指定合约的最新价格 
        """
        return self.api.sel_get_price(bytes(stdCode, encoding="utf8"))

    def sel_set_position(self, ids: int, stdCode: str, qty: float, usertag: str = ""):
        """
        设置目标仓位
        @ids     策略ids
        @stdCode   合约代码
        @qty    目标仓位，正为多，负为空
        """
        self.api.sel_set_position(ids, bytes(stdCode, encoding="utf8"), qty, bytes(usertag, encoding="utf8"))

    def sel_get_date(self):
        """
        获取当前日期
        @return    当前日期 
        """
        return self.api.sel_get_date()

    def sel_get_time(self):
        """
        获取当前时间
        @return    当前时间 
        """
        return self.api.sel_get_time()

    def sel_log_text(self, ids: int, message: str):
        """
        日志输出
        @ids         策略ids
        @message    日志内容
        """
        self.api.sel_log_text(ids, bytes(message, encoding="utf8").decode('utf-8').encode('gbk'))

    def sel_sub_ticks(self, ids: int, stdCode: str):
        """
        订阅行情
        @ids         策略ids
        @stdCode    品种代码
        """
        self.api.sel_sub_ticks(ids, bytes(stdCode, encoding="utf8"))

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    """HFT接口"""

    def hft_get_bars(self, ids: int, stdCode: str, period: str, count: int):
        """
        读取K线
        @ids     策略ids
        @stdCode   合约代码
        @period 周期，如m1/m3/d1等
        @count  条数
        """
        return self.api.hft_get_bars(ids, bytes(stdCode, encoding="utf8"), bytes(period, encoding="utf8"), count,
                                     CB_STRATEGY_GET_BAR(self.on_stra_get_bar))

    def hft_get_ticks(self, ids: int, stdCode: str, count: int):
        """
        读取Tick
        @ids     策略ids
        @stdCode   合约代码
        @count  条数
        """
        return self.api.hft_get_ticks(ids, bytes(stdCode, encoding="utf8"), count,
                                      CB_STRATEGY_GET_TICK(self.on_stra_get_tick))

    def hft_get_ordque(self, ids: int, stdCode: str, count: int):
        """
        读取委托队列
        @ids        策略ids
        @stdCode   合约代码
        @count     条数
        """
        return self.api.hft_get_ordque(ids, bytes(stdCode, encoding="utf8"), count,
                                       CB_HFTSTRA_GET_ORDQUE(self.on_hftstra_get_order_queue))

    def hft_get_orddtl(self, ids: int, stdCode: str, count: int):
        """
        读取逐笔委托
        @ids        策略ids
        @stdCode   合约代码
        @count     条数
        """
        return self.api.hft_get_orddtl(ids, bytes(stdCode, encoding="utf8"), count,
                                       CB_HFTSTRA_GET_ORDDTL(self.on_hftstra_get_order_detail))

    def hft_get_trans(self, ids: int, stdCode: str, count: int):
        """
        读取逐笔成交
        @ids        策略ids
        @stdCode   合约代码
        @count     条数
        """
        return self.api.hft_get_trans(ids, bytes(stdCode, encoding="utf8"), count,
                                      CB_HFTSTRA_GET_TRANS(self.on_hftstra_get_transaction))

    def hft_save_user_data(self, ids: int, key: str, val: str):
        """
        保存用户数据
        @ids         策略ids
        @key        数据名
        @val        数据值
        """
        self.api.hft_save_userdata(ids, bytes(key, encoding="utf8"), bytes(val, encoding="utf8"))

    def hft_load_user_data(self, ids: int, key: str, defVal: str = ""):
        """
        加载用户数据
        @ids         策略ids
        @key        数据名
        @defVal     默认值
        """
        ret = self.api.hft_load_userdata(ids, bytes(key, encoding="utf8"), bytes(defVal, encoding="utf8"))
        return bytes.decode(ret)

    def hft_get_position(self, ids: int, stdCode: str, bonlyvalid: bool = False):
        """
        获取持仓
        @ids     策略ids
        @stdCode   合约代码
        @return 指定合约的持仓手数，正为多，负为空
        """
        return self.api.hft_get_position(ids, bytes(stdCode, encoding="utf8"), bonlyvalid)

    def hft_get_position_profit(self, ids: int, stdCode: str):
        """
        获取持仓盈亏
        @ids     策略ids
        @stdCode   合约代码
        @return 指定持仓的浮动盈亏
        """
        return self.api.hft_get_position_profit(ids, bytes(stdCode, encoding="utf8"))

    def hft_get_undone(self, ids: int, stdCode: str):
        """
        获取持仓
        @ids     策略ids
        @stdCode   合约代码
        @return 指定合约的持仓手数，正为多，负为空
        """
        return self.api.hft_get_undone(ids, bytes(stdCode, encoding="utf8"))

    def hft_get_price(self, stdCode: str):
        """
        @stdCode   合约代码
        @return 指定合约的最新价格 
        """
        return self.api.hft_get_price(bytes(stdCode, encoding="utf8"))

    def hft_get_date(self):
        """
        获取当前日期
        @return    当前日期 
        """
        return self.api.hft_get_date()

    def hft_get_time(self):
        """
        获取当前时间
        @return    当前时间 
        """
        return self.api.hft_get_time()

    def hft_get_secs(self):
        """
        获取当前时间
        @return    当前时间 
        """
        return self.api.hft_get_secs()

    def hft_log_text(self, ids: int, message: str):
        """
        日志输出
        @ids         策略ids
        @message    日志内容
        """
        self.api.hft_log_text(ids, bytes(message, encoding="utf8").decode('utf-8').encode('gbk'))

    def hft_sub_ticks(self, ids: int, stdCode: str):
        """
        订阅实时行情数据
        @ids         策略ids
        @stdCode    品种代码
        """
        self.api.hft_sub_ticks(ids, bytes(stdCode, encoding="utf8"))

    def hft_sub_order_queue(self, ids: int, stdCode: str):
        """
        订阅实时委托队列数据
        @ids         策略ids
        @stdCode    品种代码
        """
        self.api.hft_sub_order_queue(ids, bytes(stdCode, encoding="utf8"))

    def hft_sub_order_detail(self, ids: int, stdCode: str):
        """
        订阅逐笔委托数据
        @ids         策略ids
        @stdCode    品种代码
        """
        self.api.hft_sub_order_detail(ids, bytes(stdCode, encoding="utf8"))

    def hft_sub_transaction(self, ids: int, stdCode: str):
        """
        订阅逐笔成交数据
        @ids         策略ids
        @stdCode    品种代码
        """
        self.api.hft_sub_transaction(ids, bytes(stdCode, encoding="utf8"))

    def hft_cancel(self, ids: int, localid: int):
        """
        撤销指定订单
        @ids         策略ids
        @localid    下单时返回的本地订单号
        """
        return self.api.hft_cancel(ids, localid)

    def hft_cancel_all(self, ids: int, stdCode: str, isBuy: bool):
        """
        撤销指定品种的全部买入订单or卖出订单
        @ids         策略ids
        @stdCode    品种代码
        @isBuy      买入or卖出
        """
        ret = self.api.hft_cancel_all(ids, bytes(stdCode, encoding="utf8"), isBuy)
        return bytes.decode(ret)

    def hft_buy(self, ids: int, stdCode: str, price: float, qty: float, userTag: str, flag: int):
        """
        买入指令
        @ids         策略ids
        @stdCode    品种代码
        @price      买入价格, 0为市价
        @qty        买入数量
        @flag       下单标志, 0-normal, 1-fak, 2-fok
        """
        ret = self.api.hft_buy(ids, bytes(stdCode, encoding="utf8"), price, qty, bytes(userTag, encoding="utf8"), flag)
        return bytes.decode(ret)

    def hft_sell(self, ids: int, stdCode: str, price: float, qty: float, userTag: str, flag: int):
        """
        卖出指令
        @ids         策略ids
        @stdCode    品种代码
        @price      卖出价格, 0为市价
        @qty        卖出数量
        @flag       下单标志, 0-normal, 1-fak, 2-fok
        """
        ret = self.api.hft_sell(ids, bytes(stdCode, encoding="utf8"), price, qty, bytes(userTag, encoding="utf8"), flag)
        return bytes.decode(ret)

    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    """CTA接口"""

    def create_cta_context(self, name: str) -> int:
        """
        创建策略环境
        @name      策略名称
        @return    系统内策略ID 
        """
        return self.api.create_cta_context(bytes(name, encoding="utf8"))

    def create_hft_context(self, name: str, trader: str, agent: bool) -> int:
        """
        创建策略环境
        @name      策略名称
        @trader    交易通道ID
        @agent     数据是否托管
        @return    系统内策略ID 
        """
        return self.api.create_hft_context(bytes(name, encoding="utf8"), bytes(trader, encoding="utf8"), agent)

    def create_sel_context(self, name: str, date: int, time: int, period: str, trdtpl: str = 'CHINA',
                           session: str = "TRADING") -> int:
        """
        创建策略环境
        @name      策略名称
        @return    系统内策略ID 
        """
        return self.api.create_sel_context(bytes(name, encoding="utf8"), date, time,
                                           bytes(period, encoding="utf8"), bytes(trdtpl, encoding="utf8"),
                                           bytes(session, encoding="utf8"))

    def reg_cta_factories(self, factFolder: str):
        return self.api.reg_cta_factories(bytes(factFolder, encoding="utf8"))

    def reg_hft_factories(self, factFolder: str):
        return self.api.reg_hft_factories(bytes(factFolder, encoding="utf8"))

    def reg_sel_factories(self, factFolder: str):
        return self.api.reg_sel_factories(bytes(factFolder, encoding="utf8"))

    def reg_exe_factories(self, factFolder: str):
        return self.api.reg_exe_factories(bytes(factFolder, encoding="utf8"))
