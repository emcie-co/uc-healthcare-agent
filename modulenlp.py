from lagom import Container
from parlant.core.nlp.service import NLPService
from parlant.core.engines.alpha.hooks import EngineHooks
from parlant.core.nlp.embedding import Embedder
from parlant.core.nlp.generation import T, SchematicGenerator
from parlant.core.nlp.moderation import ModerationService

# class YannNLPService(NLPService):
#     pass

class YannNLPService(NLPService):
    async def get_schematic_generator(self, t: type[T]) -> SchematicGenerator[T]:
        # TODO: Return a real SchematicGenerator here
        raise NotImplementedError("get_schematic_generator is not implemented yet")

    async def get_embedder(self) -> Embedder:
        # TODO: Return a real Embedder here
        raise NotImplementedError("get_embedder is not implemented yet")

    async def get_moderation_service(self) -> ModerationService:
        # TODO: Return a real ModerationService here
        raise NotImplementedError("get_moderation_service is not implemented yet")

async def configure_module(container: Container) -> Container:
    container[NLPService] = YannNLPService
    return container

# async def initialize_module(container: Container) -> None:
#    container[NLPService] = YannNLPService
#    pass

async def shutdown_module() -> None:
    pass
