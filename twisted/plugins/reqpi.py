from twisted.application import service

serviceMaker = service.ServiceMaker(
    "ReqPI",
    "reqpi.plugin",
    "A ReqPI thingy",
    "reqpi",
)

