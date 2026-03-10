"""
=============================================================
SYSTÈME MULTI-AGENTS HYBRIDE (SMAH) — Version 2.0
Projet 1 : Explicabilité dans les Systèmes Multi-Agents Hybrides
Elaboré par : Maaoui Asma — Master Recherche SII — ISIGK
=============================================================

Nouveauté v2:
    → Objectif de moyenne générale
    → Calcul automatique de la note cible par matière
    → Plan de révision orienté objectif (goal-driven)

Formalisation :
    Agentᵢ = (Perceptionᵢ, Connaissanceᵢ, Décisionᵢ, Explicationᵢ)
    Décision_globale = f(Décision₁, Décision₂, ..., Décisionₙ)
    Contributionᵢ = g(Décisionᵢ, Interactionᵢ)
    score = difficulté × coeff × facteur_compréhension × facteur_gap
"""

# ===================== DONNÉES FIXES =====================

MATIERES_BASE = [
    {"nom": "Anglais Spécifique",              "difficulte": 1,  "coeff": 1.0},
    {"nom": "Complexité des algorithmes",       "difficulte": 4,  "coeff": 1.5},
    {"nom": "Méthodologie de recherche",        "difficulte": 5,  "coeff": 1.5},
    {"nom": "Apprentissage automatique",        "difficulte": 10, "coeff": 2.0},
    {"nom": "Systèmes multi-agents",            "difficulte": 11, "coeff": 2.0},
    {"nom": "Parallélisme",                     "difficulte": 13, "coeff": 2.0},
    {"nom": "Architecture Multi Tiers",         "difficulte": 15, "coeff": 1.5},
    {"nom": "Développement Web",                "difficulte": 17, "coeff": 1.5},
    {"nom": "Modélisation & Graphes",           "difficulte": 18, "coeff": 1.5},
    {"nom": "Indexation & Images",              "difficulte": 19, "coeff": 1.5},
]

EMPLOI_DU_TEMPS = {
    "Lundi":    ["Anglais Spécifique", "Complexité des algorithmes", "Modélisation & Graphes"],
    "Mardi":    ["Architecture Multi Tiers", "Systèmes multi-agents"],
    "Mercredi": ["Parallélisme", "Indexation & Images"],
    "Jeudi":    ["Méthodologie de recherche", "Développement Web"],
    "Vendredi": ["Apprentissage automatique"],
    "Samedi":   [],
}

HEURES_DISPONIBLES = {
    "Lundi": 3.0, "Mardi": 2.5, "Mercredi": 3.0,
    "Jeudi": 2.0, "Vendredi": 3.5, "Samedi": 4.0
}

HEURE_RETOUR = {
    "Lundi": "13h00", "Mardi": "15h30", "Mercredi": "13h00",
    "Jeudi": "17h00", "Vendredi": "13h00", "Samedi": "08h00"
}


# =====================================================
# MODULE CALCUL OBJECTIF
# Calcule la note cible par matière pour atteindre
# la moyenne générale souhaitée
# =====================================================

class ModuleObjectif:
    """
    Calcule intelligemment la note cible par matière
    en fonction de la moyenne générale souhaitée.

    Stratégie :
        - Matières faciles (diff faible) → note cible haute (plus facile à atteindre)
        - Matières difficiles (diff haute) → note cible réaliste (effort proportionnel)
        - Coeff élevé → priorité d'investissement
    """

    def __init__(self, matieres, moyenne_cible, moyenne_precedente):
        self.matieres = matieres
        self.moyenne_cible = moyenne_cible
        self.moyenne_precedente = moyenne_precedente
        self.total_coeff = sum(m["coeff"] for m in matieres)

    def calculer_notes_cibles(self):
        """
        Distribue la moyenne cible sur les matières.
        effort = f(difficulté, compréhension)
            → Matière difficile + pas comprise = effort élevé
            → Matière facile   + bien comprise = effort faible
        Note: compréhension 1=tout compris, 10=rien compris
        """
        resultats = []
        for m in self.matieres:
            # Note cible : matière facile → note cible haute, difficile → note cible réaliste
            facteur_realisme = 1 - (m["difficulte"] / 20) * 0.4
            note_brute = self.moyenne_cible * facteur_realisme * (1 + m["coeff"] / 10)
            note_cible = max(10, min(19, round(note_brute, 1)))

            # Gap = écart entre note cible et niveau actuel estimé
            gap = max(0, round(note_cible - self.moyenne_precedente * 0.8, 1))

            # Effort = difficulté × non-compréhension (compréhension 1=compris, 10=non compris)
            comp = m.get("comprehension", 5)
            effort_score = (m["difficulte"] / 20) * (comp / 10)
            if effort_score > 0.5:
                effort = "🔴 Élevé"
            elif effort_score > 0.25:
                effort = "🟠 Moyen"
            else:
                effort = "🟢 Faible"

            resultats.append({
                **m,
                "note_cible" : note_cible,
                "gap"        : gap,
                "effort"     : effort,
                "effort_score": effort_score,
            })
        return resultats

    def afficher_objectifs(self, notes_cibles):
        """Affiche le tableau des objectifs par matière"""
        print("\n" + "="*65)
        print(f"  🎯 OBJECTIFS PAR MATIÈRE — Cible: {self.moyenne_cible}/20")
        print(f"  📊 Référence: Moyenne précédente = {self.moyenne_precedente}/20")
        print("="*65)
        print(f"  {'Matière':<38} {'Coeff':>5} {'Cible':>6} {'Effort':>12}")
        print("  " + "-"*60)
        for m in notes_cibles:
            print(f"  {m['nom']:<38} {m['coeff']:>5} "
                  f"{m['note_cible']:>5}/20 {m['effort']:>12}")
        moyenne_estimee = sum(m["note_cible"] * m["coeff"] for m in notes_cibles) / self.total_coeff
        print("  " + "-"*60)
        print(f"  {'Moyenne estimée si objectifs atteints':<38} "
              f"{'':>5} {moyenne_estimee:>5.1f}/20")
        print("="*65)


# =====================================================
# AGENT 1 : Agent ML Classique
# =====================================================

class AgentML:
    """
    Agent ML : calcule les scores de priorité.
    score = difficulté × coeff × facteur_compréhension × facteur_gap
    """

    def __init__(self, matieres):
        self.matieres = matieres
        self.nom = "Agent ML Classique"

    def percevoir(self):
        return self.matieres

    def decider(self):
        """
        score = difficulté × coeff × (1 + (10-compréhension)/10) × (1 + gap/20)
        Intègre : difficulté + importance (coeff) + compréhension + gap objectif
        """
        donnees = self.percevoir()
        scored = []
        for m in donnees:
            comprehension   = m.get("comprehension", 5)
            gap             = m.get("gap", 0)
            facteur_comp    = 1 + (comprehension - 1) / 10  # 1=fаhima → ×1.0 | 10=mafhimtish → ×1.9
            facteur_gap     = 1 + gap / 20
            score = m["difficulte"] * m["coeff"] * facteur_comp * facteur_gap
            scored.append({
                **m,
                "score_ml"     : round(score, 2),
                "facteur_comp" : round(facteur_comp, 2),
                "facteur_gap"  : round(facteur_gap, 2),
            })
        scored.sort(key=lambda x: x["score_ml"], reverse=True)
        return scored

    def expliquer(self, decision):
        return {
            "agent"  : self.nom,
            "type"   : "Score multi-facteurs (difficulté × coeff × compréhension × gap)",
            "scores" : [(m["nom"], m["score_ml"]) for m in decision]
        }


# =====================================================
# AGENT 2 : Agent Neuro-Symbolique
# =====================================================

class AgentNeuroSymbolique:
    """
    Agent hybride : applique des règles SI/ALORS contextuelles.
    Intègre l'état physique, l'emploi du temps et les objectifs.
    """

    def __init__(self):
        self.nom = "Agent Neuro-Symbolique"
        self.regles = [
            self._regle_etat_fatigue,
            self._regle_etat_energique,
            self._regle_etat_normal,
            self._regle_comprehension_faible,
            self._regle_gap_critique,
            self._regle_cours_du_jour,
            self._regle_anglais_quotidien,
            self._regle_coeff_eleve,
        ]

    def percevoir(self, ml_decision, etat_physique, jour):
        return {
            "priorites_ml"      : ml_decision,
            "etat"              : etat_physique,
            "jour"              : jour,
            "cours_aujourd_hui" : EMPLOI_DU_TEMPS.get(jour, [])
        }

    def decider(self, ml_decision, etat_physique, jour):
        perception     = self.percevoir(ml_decision, etat_physique, jour)
        ajustements    = []
        explications   = []

        for regle in self.regles:
            resultat = regle(perception)
            if resultat:
                ajustements.append(resultat["ajustement"])
                explications.append(resultat["explication"])

        matieres_ajustees = list(perception["priorites_ml"])
        for ajust in ajustements:
            matieres_ajustees = ajust(matieres_ajustees)

        return {"matieres_ajustees": matieres_ajustees, "explications": explications}

    # ---- RÈGLES SYMBOLIQUES ----

    def _regle_etat_fatigue(self, perception):
        if perception["etat"] != "fatigue":
            return None
        def ajust(matieres):
            filtrees = [m for m in matieres if m["difficulte"] <= 15][:3]
            faciles  = [m for m in filtrees if m["difficulte"] <= 8]
            moyennes = [m for m in filtrees if 8 < m["difficulte"] <= 15]
            ordre, fi, mi, toggle = [], 0, 0, True
            while fi < len(faciles) or mi < len(moyennes):
                if toggle and fi < len(faciles):
                    ordre.append({**faciles[fi], "duree_max": 40}); fi += 1
                elif mi < len(moyennes):
                    ordre.append({**moyennes[mi], "duree_max": 35}); mi += 1
                elif fi < len(faciles):
                    ordre.append({**faciles[fi], "duree_max": 40}); fi += 1
                toggle = not toggle
            return ordre if ordre else [{**m, "duree_max": 35} for m in filtrees]
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : "SI état == fatigué",
                "action"        : "ALORS MAX 3 matières | exclure diff>15 | alterner facile↔moyen",
                "justification" : "Fatigue → éviter surcharge cognitive"
            }
        }

    def _regle_etat_energique(self, perception):
        if perception["etat"] != "energique":
            return None
        def ajust(matieres):
            top4 = sorted(matieres[:5], key=lambda x: x["difficulte"], reverse=True)[:4]
            return [{**m, "duree_max": 75 if m["difficulte"] > 15 else 60} for m in top4]
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : "SI état == énergique",
                "action"        : "ALORS MAX 4 matières | plus difficile en premier | 60-75 min",
                "justification" : "Énergie max → attaquer les matières les plus exigeantes"
            }
        }

    def _regle_etat_normal(self, perception):
        if perception["etat"] != "normal":
            return None
        def ajust(matieres):
            top3       = matieres[:3]
            difficiles = [m for m in top3 if m["difficulte"] > 13]
            moyennes   = [m for m in top3 if 7 < m["difficulte"] <= 13]
            faciles    = [m for m in top3 if m["difficulte"] <= 7]
            ordre      = moyennes + difficiles + faciles
            return [{**m, "duree_max": 55} for m in ordre] if ordre else [{**m, "duree_max": 55} for m in top3]
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : "SI état == normal",
                "action"        : "ALORS MAX 3 matières | ordre: moyen→difficile→facile",
                "justification" : "Warm-up cognitif → pic → récupération"
            }
        }

    def _regle_comprehension_faible(self, perception):
        def ajust(matieres):
            result = []
            for m in matieres:
                comp = m.get("comprehension", 5)
                if comp >= 8:
                    result.append({**m, "duree_max": m.get("duree_max", 60) + 15,
                                   "alerte": "⚠️ Compréhension très faible"})
                else:
                    result.append({**m, "alerte": ""})
            return result
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : "SI compréhension ≤ 3/10",
                "action"        : "ALORS durée +15 min",
                "justification" : "Compréhension faible → besoin de plus de temps"
            }
        }

    def _regle_gap_critique(self, perception):
        """Nouvelle règle : si gap objectif > 5 → session obligatoire même si pas prioritaire"""
        def ajust(matieres):
            critiques  = [m for m in matieres if m.get("gap", 0) > 5]
            normales   = [m for m in matieres if m.get("gap", 0) <= 5]
            # Les matières avec gap critique passent en premier
            return critiques + normales
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : "SI gap_objectif > 5 points",
                "action"        : "ALORS matière remontée en priorité absolue",
                "justification" : "Gap important → risque de ne pas atteindre l'objectif"
            }
        }

    def _regle_cours_du_jour(self, perception):
        cours = perception["cours_aujourd_hui"]
        if not cours:
            return None
        def ajust(matieres):
            result = [{**m, "boost": 1.4 if m["nom"] in cours else 1.0} for m in matieres]
            result.sort(key=lambda x: x["score_ml"] * x.get("boost", 1.0), reverse=True)
            return result
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : f"SI matière ∈ cours_aujourd_hui",
                "action"        : "ALORS boost priorité × 1.4",
                "justification" : "Révision le soir même → consolidation mémoire"
            }
        }

    def _regle_anglais_quotidien(self, perception):
        def ajust(matieres):
            return [{**m, "session_courte": m["nom"] == "Anglais Spécifique"} for m in matieres]
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : "SI matière == 'Anglais Spécifique'",
                "action"        : "ALORS session courte 20 min/jour",
                "justification" : "Langue → progression par répétition espacée"
            }
        }

    def _regle_coeff_eleve(self, perception):
        def ajust(matieres):
            return [{**m, "priorite_haute": m["coeff"] >= 2.0} for m in matieres]
        return {
            "ajustement": ajust,
            "explication": {
                "regle"         : "SI coefficient ≥ 2.0",
                "action"        : "ALORS priorité haute ⭐",
                "justification" : "Impact fort sur la moyenne générale"
            }
        }


# =====================================================
# MODULE D'AGRÉGATION
# =====================================================

class ModuleAggregation:
    """
    Collecte les décisions locales, arbitre les conflits,
    produit la Décision_globale + Explication_globale.
    """

    def __init__(self):
        self.nom = "Module d'Agrégation"

    def agreger(self, decision_ml, decision_ns, heures_dispo, jour):
        matieres_finales = decision_ns["matieres_ajustees"]
        sessions         = []
        heures_restantes = heures_dispo
        utilisees        = set()
        heure_courante   = 19 * 60  # 19h00

        # Anglais toujours en premier (règle NS)
        for m in matieres_finales:
            if m["nom"] == "Anglais Spécifique":
                sessions.append(self._creer_session(m, 20, heure_courante))
                heure_courante   += 30
                heures_restantes -= 20 / 60
                utilisees.add(m["nom"])
                break

        # Reste par priorité
        for m in matieres_finales:
            if m["nom"] in utilisees:
                continue
            if heures_restantes <= 0.3:
                break
            duree = min(m.get("duree_max", 60), heures_restantes * 60)
            duree = round(duree / 5) * 5
            if duree < 20:
                break
            sessions.append(self._creer_session(m, duree, heure_courante))
            heure_courante   += duree + 10
            heures_restantes -= duree / 60
            utilisees.add(m["nom"])

        contributions = self._calculer_contributions(decision_ml, decision_ns)
        return {
            "jour"               : jour,
            "sessions"           : sessions,
            "explication_globale": self._generer_explication(decision_ns["explications"], contributions),
            "contributions"      : contributions
        }

    def _creer_session(self, m, duree, heure_min):
        h, mn = heure_min // 60, heure_min % 60
        return {
            "matiere"       : m["nom"],
            "duree_min"     : duree,
            "heure"         : f"{h}h{mn:02d}",
            "difficulte"    : m["difficulte"],
            "coeff"         : m["coeff"],
            "score_ml"      : m.get("score_ml", 0),
            "comprehension" : m.get("comprehension", "?"),
            "note_cible"    : m.get("note_cible", "?"),
            "gap"           : m.get("gap", 0),
            "effort"        : m.get("effort", ""),
            "priorite_haute": m.get("priorite_haute", False),
            "alerte"        : m.get("alerte", ""),
        }

    def _calculer_contributions(self, decision_ml, decision_ns):
        return {
            "Agent ML": {
                "role"         : "Calcul score multi-facteurs (diff × coeff × compréh × gap)",
                "contribution" : "Fournit l'ordre de priorité basé sur les données objectives",
            },
            "Agent Neuro-Symbolique": {
                "role"         : "Ajustement contextuel par règles SI/ALORS",
                "contribution" : "Intègre état physique, planning et objectifs de moyenne",
            }
        }

    def _generer_explication(self, regles_ns, contributions):
        return {
            "methode"              : "Consensus Agent ML + Agent Neuro-Symbolique",
            "regles_appliquees"    : regles_ns,
            "contributions_agents" : contributions,
            "coherence"            : "✅ Aucun conflit détecté"
        }


# =====================================================
# SMAH — Système Multi-Agents Hybride
# =====================================================

class SMAH:
    def __init__(self, matieres):
        self.agent_ml          = AgentML(matieres)
        self.agent_ns          = AgentNeuroSymbolique()
        self.module_aggregation= ModuleAggregation()
        print("\n" + "="*60)
        print("  SMAH v2.0 — Système Multi-Agents Hybride")
        print(f"  {self.agent_ml.nom} + {self.agent_ns.nom}")
        print("="*60)

    def generer_plan(self, etat_physique="normal"):
        print(f"\n🔄 État physique : {etat_physique}\n")
        plan_semaine = {}
        for jour, heures in HEURES_DISPONIBLES.items():
            print(f"  📅 Traitement : {jour}...")
            decision_ml  = self.agent_ml.decider()
            decision_ns  = self.agent_ns.decider(decision_ml, etat_physique, jour)
            plan_jour    = self.module_aggregation.agreger(decision_ml, decision_ns, heures, jour)
            plan_semaine[jour] = plan_jour
        return plan_semaine

    def afficher_plan(self, plan):
        print("\n" + "="*65)
        print("  PLAN DE RÉVISION HEBDOMADAIRE — SMAH v2.0")
        print("="*65)

        for jour, data in plan.items():
            cours = ', '.join(EMPLOI_DU_TEMPS[jour]) or 'Aucun'
            print(f"\n📅 {jour.upper()} [Retour: {HEURE_RETOUR[jour]} | Cours: {cours}]")
            print("  " + "-"*60)

            for s in data["sessions"]:
                flag   = "⭐" if s["priorite_haute"] else "  "
                alerte = s.get("alerte", "")
                print(f"  {flag} {s['heure']} | {s['duree_min']:3d} min | "
                      f"{s['matiere']:<35} | "
                      f"cible={s['note_cible']}/20 | "
                      f"gap={s['gap']} | {s['effort']}")
                if alerte:
                    print(f"       {alerte}")

            total = sum(s["duree_min"] for s in data["sessions"])
            print(f"\n  ⏱  Total : {total // 60}h{total % 60:02d}min")

        # Explication globale
        dernier = list(plan.values())[-1]
        exp     = dernier["explication_globale"]
        print("\n" + "="*65)
        print("  EXPLICATION GLOBALE — Module d'Agrégation")
        print("="*65)
        print(f"\n  Méthode  : {exp['methode']}")
        print(f"  Cohérence: {exp['coherence']}")
        print("\n  Règles Neuro-Symboliques appliquées :")
        for r in exp["regles_appliquees"]:
            print(f"    • {r['regle']}")
            print(f"      → {r['action']}")
            print(f"      💡 {r['justification']}")
        print("\n  Contributions des agents :")
        for agent, c in exp["contributions_agents"].items():
            print(f"\n  [{agent}]")
            print(f"    Rôle        : {c['role']}")
            print(f"    Contribution: {c['contribution']}")


# =====================================================
# INTERFACE INTERACTIVE
# =====================================================

def saisir_donnees():
    print("\n" + "="*60)
    print("  🎓 SMAH v2.0 — Study Planner Intelligent")
    print("="*60)

    # --- Moyenne précédente ---
    print("\n📊 Quelle était ta moyenne générale l'année/semestre précédent ?")
    while True:
        try:
            moy_prec = float(input("   → Moyenne précédente (/20) : "))
            if 0 <= moy_prec <= 20: break
            else: print("   ⚠️  Entre une valeur entre 0 et 20 !")
        except ValueError:
            print("   ⚠️  Nombre invalide !")

    # --- Objectif ---
    print(f"\n🎯 Quelle moyenne veux-tu atteindre ce semestre ?")
    print(f"   (Référence : tu avais {moy_prec}/20 avant)")
    while True:
        try:
            moy_cible = float(input("   → Moyenne cible (/20) : "))
            if 0 <= moy_cible <= 20: break
            else: print("   ⚠️  Entre une valeur entre 0 et 20 !")
        except ValueError:
            print("   ⚠️  Nombre invalide !")

    # Calcul des objectifs par matière
    module_obj = ModuleObjectif(MATIERES_BASE, moy_cible, moy_prec)
    notes_cibles = module_obj.calculer_notes_cibles()
    module_obj.afficher_objectifs(notes_cibles)

    # --- État physique ---
    print("\n❓ Quel est ton état physique aujourd'hui ?")
    print("   1. 😴 Fatigué(e)   2. 😊 Normal   3. ⚡ Énergique")
    while True:
        choix = input("   → Ton choix (1/2/3) : ").strip()
        if choix == "1":   etat = "fatigue";   break
        elif choix == "2": etat = "normal";    break
        elif choix == "3": etat = "energique"; break
        else: print("   ⚠️  Entre 1, 2 ou 3 !")
    print(f"   ✅ État : {etat}")

    # --- Compréhension ---
    print("\n" + "─"*60)
    print("📚 Compréhension par matière (1=tout compris ✅ → 10=rien compris ❌):")
    print("─"*60)

    matieres_finales = []
    for m in notes_cibles:
        while True:
            try:
                val = int(input(f"  {m['nom']:<40} (cible={m['note_cible']}/20) → ").strip())
                if 1 <= val <= 10:
                    matieres_finales.append({**m, "comprehension": val})
                    break
                else: print("   ⚠️  Entre 1 et 10 !")
            except ValueError:
                print("   ⚠️  Nombre invalide !")

    print("\n✅ Données saisies ! Génération du plan en cours...\n")
    return etat, matieres_finales, moy_cible, moy_prec


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ["fatigue", "normal", "energique"]:
        # Mode rapide pour test
        etat = sys.argv[1]
        from copy import deepcopy
        module_obj   = ModuleObjectif(MATIERES_BASE, 15.0, 11.0)
        notes_cibles = module_obj.calculer_notes_cibles()
        matieres_finales = [{**m, "comprehension": 5} for m in notes_cibles]
        moy_cible, moy_prec = 15.0, 11.0
        module_obj.afficher_objectifs(notes_cibles)
        print(f"\n🚀 Mode rapide — État: {etat}")
    else:
        etat, matieres_finales, moy_cible, moy_prec = saisir_donnees()

    # Lancer le SMAH
    smah = SMAH(matieres_finales)
    plan = smah.generer_plan(etat_physique=etat)
    smah.afficher_plan(plan)

    print(f"\n{'='*65}")
    print(f"  ✅ Plan généré — Objectif: {moy_cible}/20 | Référence: {moy_prec}/20")
    print(f"  Agent ML + Agent Neuro-Symbolique + Module d'Agrégation")
    print(f"  Projet 1 — Maaoui Asma — Master Recherche SII")
    print(f"{'='*65}\n")