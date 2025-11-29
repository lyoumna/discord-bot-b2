# structures/tree.py
from __future__ import annotations
from typing import Any, Optional

class TreeNode:
    def __init__(self, key: str, prompt: str, children: Optional[list["TreeNode"]] = None, conclusion: Optional[str] = None):
        self.key = key  # identifiant du noeud / sujet
        self.prompt = prompt  # question à poser
        self.children = children or []
        self.conclusion = conclusion  # si feuille, conclusion possible

    def find_topic(self, topic: str) -> bool:
        # Parcours DFS pour vérifier si 'topic' existe comme key dans l'arbre
        if self.key.lower() == topic.lower():
            return True
        for child in self.children:
            if child.find_topic(topic):
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "prompt": self.prompt,
            "conclusion": self.conclusion,
            "children": [c.to_dict() for c in self.children]
        }

    @staticmethod
    def from_dict(d: dict) -> "TreeNode":
        node = TreeNode(d["key"], d["prompt"], conclusion=d.get("conclusion"))
        node.children = [TreeNode.from_dict(c) for c in d.get("children", [])]
        return node

# Exemple d'arbre minimal (tu pourras le modifier)
def sample_tree() -> TreeNode:
    # Racine
    root = TreeNode("start", "Bonjour ! Veux-tu parler de 'jeu', 'travail' ou 'loisir' ?")

    jeu = TreeNode("jeu", "Quel type de jeu préfères-tu ? 'vidéo' ou 'table' ?")
    jeu.children = [
        TreeNode("vidéo", "Tu préfères PC ou console ?", conclusion="Tu es un joueur vidéo."),
        TreeNode("table", "Jeu de stratégie ou familial ?", conclusion="Tu aimes les jeux de société.")
    ]

    travail = TreeNode("travail", "Parlons travail. Es-tu 'étudiant' ou 'professionnel' ?")
    travail.children = [
        TreeNode("étudiant", "Quel est ton domaine d'étude ?", conclusion="Tu es étudiant."),
        TreeNode("professionnel", "Travail en bureau ou remote ?", conclusion="Tu es un professionnel.")
    ]

    loisir = TreeNode("loisir", "Tu préfères 'sport' ou 'créatif' ?")
    loisir.children = [
        TreeNode("sport", "Quel sport ?", conclusion="Tu aimes le sport."),
        TreeNode("créatif", "Peins-tu, écris-tu, ou fais-tu musique ?", conclusion="Tu es créatif.")
    ]

    root.children = [jeu, travail, loisir]
    return root
