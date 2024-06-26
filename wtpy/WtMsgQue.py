from wtpy.wrapper.WtMQWrapper import WtMQWrapper, CB_ON_MSG
from wtpy.WtUtilDefs import singleton


class WtMQServer:

    def __init__(self):
        self.id = None

    def init(self, wrapper: WtMQWrapper, ids: int):
        self.id = ids
        self.wrapper = wrapper

    def publish_message(self, topic: str, message: str):
        if self.id is None:
            raise Exception("MQServer not initialzied")

        self.wrapper.publish_message(self.id, topic, message)


class WtMQClient:

    def __init__(self):
        return

    def init(self, wrapper: WtMQWrapper, ids: int):
        self.id = ids
        self.wrapper = wrapper

    def start(self):
        if self.id is None:
            raise Exception("MQClient not initialzied")

        self.wrapper.start_client(self.id)

    def subscribe(self, topic: str):
        if self.id is None:
            raise Exception("MQClient not initialzied")
        self.wrapper.subcribe_topic(self.id, topic)

    def on_mq_message(self, topic: str, message: str, dataLen: int):
        pass


@singleton
class WtMsgQue:

    def __init__(self) -> None:
        self._servers = dict()
        self._clients = dict()
        self._wrapper = WtMQWrapper(self)

        self._cb_msg = CB_ON_MSG(self.on_mq_message)

    def get_client(self, client_id: int) -> WtMQClient:
        if client_id not in self._clients:
            return None

        return self._clients[client_id]

    def on_mq_message(self, client_id: int, topic: str, message: str, dataLen: int):
        client = self.get_client(client_id)
        if client is None:
            return

        client.on_mq_message(topic, message, dataLen)

    def add_mq_server(self, url: str, server: WtMQServer = None) -> WtMQServer:
        ids = self._wrapper.create_server(url)
        if server is None:
            server = WtMQServer()

        server.init(self._wrapper, ids)
        self._servers[ids] = server
        return server

    def destroy_mq_server(self, server: WtMQServer):
        ids = server.id
        if ids not in self._servers:
            return

        self._wrapper.destroy_server(ids)
        self._servers.pop(ids)

    def add_mq_client(self, url: str, client: WtMQClient = None) -> WtMQClient:
        ids = self._wrapper.create_client(url, self._cb_msg)
        if client is None:
            client = WtMQClient()
        client.init(self._wrapper, ids)
        self._clients[ids] = client
        return client

    def destroy_mq_client(self, client: WtMQClient):
        ids = client.id
        if ids not in self._clients:
            return

        self._wrapper.destroy_client(ids)
        self._clients.pop(ids)
