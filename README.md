Ce projet implémente un système de **fact-checking automatique** basé sur le dataset **FEVER** et un snapshot de **Wikipédia** fourni avec le dataset.

L'objectif global du projet est de comparer plusieurs approches :

1. **Pipeline classique (principal)**  
   - Indexation BM25 du dump Wikipédia (niveau phrase).  
   - Récupération de phrases candidates pour chaque claim.  
   - Modèle classique (TF-IDF + Logistic Regression / SVM) pour prédire :  
     **SUPPORTS / REFUTES / NOT ENOUGH INFO**.

2. **Pipeline LLM "offline" (secondaire)**  
   - Même index BM25 et mêmes phrases candidates que le pipeline classique.  
   - Un LLM reçoit : *claim + phrases candidates*, sans accès au web, et renvoie un verdict structuré (JSON).

3. **Pipeline multi-agent (exploratoire)**  
   - Système multi-agent orchestré (LangGraph / LangChain).  
   - Agents capables de consulter le web (sites d’actualité, sources externes) en plus de Wikipédia.

> Pour l’instant, le repo contient surtout la **partie Indexation + Retrieval BM25**, qui sert de base commune aux pipelines.

---