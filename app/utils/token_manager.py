import uuid

class TokenManager:
    def __init__(self):
        self.token_store:dict[str, str] = {}
    
    def get_token(self, entity: str) -> str:
        """
        Get a consistent token for an entity.
        If the entity is new, generate a new token.
        """
        if entity not in self.token_store:
            self.token_store[entity] = f"TOKEN_{uuid.uuid4().hex[:8]}"
        return self.token_store[entity]
    
    def hash_entity(self, entity: str) -> str:
        """
        Hash an entity using a hash function.
        """
        return f"HASH_{hash(entity) % 1000000}" # does not avoid collision!

    def mask_entity(self, entity: str) -> str:
        """
        Mask an entity by replacing characters with asterisks.
        """
        if len(entity) <= 2:
            return "*" * len(entity)
        return entity[0] + "*" * (len(entity) - 2) + entity[-1]