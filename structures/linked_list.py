# structures/linked_list.py
from __future__ import annotations
from typing import Optional

class Node:
    def __init__(self, user_id: int, command: str, next: Optional["Node"] = None):
        self.user_id = user_id
        self.command = command
        self.next = next

class LinkedListHistory:
    """
    Liste chaînée simple stockant les commandes par insertion en tête (pour récupérer la dernière rapidement).
    Chaque noeud contient user_id + commande.
    """
    def __init__(self):
        self.head: Optional[Node] = None

    def push(self, user_id: int, command: str):
        node = Node(user_id, command, self.head)
        self.head = node

    def get_last_for_user(self, user_id: int) -> Optional[str]:
        cur = self.head
        while cur:
            if cur.user_id == user_id:
                return cur.command
            cur = cur.next
        return None

    def get_all_for_user(self, user_id: int) -> list[str]:
        res = []
        cur = self.head
        while cur:
            if cur.user_id == user_id:
                res.append(cur.command)
            cur = cur.next
        return res

    def clear(self):
        self.head = None

    def clear_for_user(self, user_id: int):
        # Supprimer tous les noeuds correspondant à l'utilisateur donné
        dummy = Node(-1, "", self.head)
        prev = dummy
        cur = self.head
        while cur:
            if cur.user_id == user_id:
                prev.next = cur.next
            else:
                prev = cur
            cur = cur.next
        self.head = dummy.next

    def to_list(self) -> list[dict]:
        # sérialisation: liste d'objets {user_id, command} du plus récent au plus ancien
        res = []
        cur = self.head
        while cur:
            res.append({"user_id": cur.user_id, "command": cur.command})
            cur = cur.next
        return res

    def from_list(self, items: list[dict]):
        # items attendus du plus récent au plus ancien -> reconstruire en conservant l'ordre
        self.head = None
        for item in reversed(items):  # reversed pour que le premier devienne la tête finale
            self.push(item["user_id"], item["command"])
