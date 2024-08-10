from typing import List, Optional
from pydantic import BaseModel
from pydantic import BaseModel, Field
from datetime import time

class HoraireHebdomadaire(BaseModel):
    jour_semaine: str
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None

class Medecin(BaseModel):
    id: int
    nom: str
    specialite: str
    email: str
    horaires: List[HoraireHebdomadaire] = Field(default_factory=list)

class Infirmier(BaseModel):
    id: int
    nom: str
    service: str
    email: str
