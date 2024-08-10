from fastapi import FastAPI, HTTPException
from models import Infirmier, HoraireHebdomadaire
from config import get_snowflake_connection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post('/infirmiers', response_model=Infirmier)
async def ajouter_infirmier(infirmier: Infirmier):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO infirmiers (id, nom, service, email) 
            VALUES (%s, %s, %s, %s)
        """, (infirmier.id, infirmier.nom, infirmier.service, infirmier.email))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return infirmier

@app.get('/infirmiers', response_model=list[Infirmier])
async def obtenir_infirmiers():
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nom, service, email FROM infirmiers")
        infirmiers = cursor.fetchall()
        return [Infirmier(id=row[0], nom=row[1], service=row[2], email=row[3]) for row in infirmiers]
    finally:
        cursor.close()
        conn.close()

@app.get('/infirmiers/{id}', response_model=Infirmier)
async def obtenir_infirmier(id: int):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nom, service, email FROM infirmiers WHERE id = %s", (id,))
        infirmier = cursor.fetchone()
        if infirmier is None:
            raise HTTPException(status_code=404, detail="Infirmier non trouvé")
        return Infirmier(id=infirmier[0], nom=infirmier[1], service=infirmier[2], email=infirmier[3])
    finally:
        cursor.close()
        conn.close()

@app.put('/infirmiers/{id}', response_model=Infirmier)
async def mettre_a_jour_infirmier(id: int, infirmier: Infirmier):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE infirmiers SET nom = %s, service = %s, email = %s 
            WHERE id = %s
        """, (infirmier.nom, infirmier.service, infirmier.email, id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return infirmier

@app.delete('/infirmiers/{id}', response_model=dict)
async def supprimer_infirmier(id: int):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM infirmiers WHERE id = %s", (id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return {"message": "Infirmier supprimé avec succès"}

@app.post('/infirmiers/{id}/horaires', response_model=HoraireHebdomadaire)
async def ajouter_horaire_infirmiers(id: int, horaire: HoraireHebdomadaire):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        heure_debut = horaire.heure_debut.strftime("%H:%M:%S")
        heure_fin = horaire.heure_fin.strftime("%H:%M:%S")

        # Debugging output
        print(f"ID_INFIRMIERS: {id}, JOUR_SEMAINE: {horaire.jour_semaine}, HEURE_DEBUT: {heure_debut}, HEURE_FIN: {heure_fin}")

        cursor.execute("""
            INSERT INTO CENTRE_MEDECINE.CENTREM.HORAIREHEBDOMADAIREINFIRMIERS
            (ID_INFIRMIERS, JOUR_SEMAINE, HEURE_DEBUT, HEURE_FIN) 
            VALUES (%s, %s, %s, %s)
        """, (id, horaire.jour_semaine, heure_debut, heure_fin))
        conn.commit()
    except Exception as e:
        print(f"Exception: {str(e)}")  # Debugging output
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'insertion de l'horaire: {str(e)}")
    finally:
        cursor.close()
        conn.close()
    return horaire


@app.get('/infirmiers/{id}/horaires', response_model=list[HoraireHebdomadaire])
async def obtenir_horaires(id: int):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT JOUR_SEMAINE, HEURE_DEBUT, HEURE_FIN 
            FROM CENTRE_MEDECINE.CENTREM.HORAIREHEBDOMADAIREINFIRMIERS
            WHERE ID_INFIRMIERS = %s
        """, (id,))
        horaires = cursor.fetchall()
        return [HoraireHebdomadaire(jour_semaine=row[0], heure_debut=row[1], heure_fin=row[2]) for row in horaires]
    finally:
        cursor.close()
        conn.close()

@app.put('/infirmiers/{id}/horaires/{horaire_id}', response_model=HoraireHebdomadaire)
async def mettre_a_jour_horaire(id: int, horaire_id: int, horaire: HoraireHebdomadaire):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE CENTRE_MEDECINE.CENTREM.HORAIREHEBDOMADAIREINFIRMIERS
            SET JOUR_SEMAINE = %s, HEURE_DEBUT = %s, HEURE_FIN = %s 
            WHERE ID_INFIRMIERS = %s AND ID = %s
        """, (horaire.jour_semaine, horaire.heure_debut, horaire.heure_fin, id, horaire_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return horaire

@app.delete('/infirmiers/{id}/horaires/{horaire_id}', response_model=dict)
async def supprimer_horaire(id: int, horaire_id: int):
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM CENTRE_MEDECINE.CENTREM.HORAIREHEBDOMADAIREINFIRMIERS
            WHERE ID_INFIRMIERS = %s AND ID = %s
        """, (id, horaire_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return {"message": "Horaire supprimé avec succès"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8804)
