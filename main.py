import sys
from protocol import Protocol
from db import DataBase
from menu_model import MenuModel
from menu_repo import MenuRepo
from client_registry import ClientRegistry
from broadcaster import Broadcaster
from order_router import OrderRouter
from server import Server


def main():
    protocol = Protocol()


    db = DataBase()
    menu_repo = MenuRepo(db)
    menu_model = MenuModel(menu_repo)

    # 의존성 순서: registry -> broadcaster(registry 필요) -> order_router(registry, broadcaster 필요)
    client_registry = ClientRegistry()
    broadcaster = Broadcaster(protocol, client_registry)
    order_router = OrderRouter(protocol, client_registry, broadcaster, menu_model)

    server = Server(protocol, menu_model, client_registry, broadcaster, order_router)

    return server.run()


if __name__ == "__main__":
    sys.exit(main())
