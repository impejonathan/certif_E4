import subprocess
from typing import List
from dagster import asset, AssetExecutionContext, define_asset_job, Definitions, ScheduleDefinition, AssetSelection, Failure
from dagster import asset, AssetIn

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from Script_projet.leboncoin.leboncoin.spiders.carter_cash import ImmoSpider
from dagster import Failure
import os

####################################################################################################
################################     partie 1 scraping    ############################################
####################################################################################################

@asset(key="1_Azure_Scrapy", group_name="azure_tasks")
def execute_Scrapy(context: AssetExecutionContext):
    """
    Lancement du scraping de carter cash
    """
    context.log.info("Début de l'exécution de la tâche de scraping.")
    try:
        # Run the Scrapy spider
        scrapy_project_path = "Script_projet/leboncoin/leboncoin/spiders"

        # Change the current working directory to the Scrapy project directory
        os.chdir(scrapy_project_path)
        
        # Run the Scrapy spider
        subprocess.run(["scrapy", "crawl", "carter"])

        context.log.info("Scraping terminé avec succès.")
        return True
    except Exception as e:
        raise Failure(f"Erreur lors de l'exécution du scraping : {str(e)}")


####################################################################################################
################################     partie 2 comptage    ############################################
####################################################################################################

@asset(key="2_Azure_Count", group_name="azure_tasks", ins={"upstream": AssetIn(key="1_Azure_Scrapy")})
def execute_Count(context: AssetExecutionContext, upstream: bool):
    """

   nombre de lignes injecter lors du dernier scraping 

    """
    if not upstream:
        context.log.info("La tâche précédente a échoué, donc cette tâche ne sera pas exécutée.")
        return
    
    context.log.info("Début de l'exécution de 1_bis_count_inject.py")
    try:
        result = subprocess.run(["python", "Script_projet/1_bis_count_inject.py"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Failure(f"Erreur lors de l'exécution de 1_bis_count_inject.py : {result.stderr}")
        else:
            lines_inserted = [int(s) for s in result.stdout.split() if s.isdigit()]
            if lines_inserted:
                context.log.info(f"{lines_inserted[0]} lignes ont été insérées.")
            context.log.info("1_bis_count_inject.py exécuté avec succès")
            return True
    except FileNotFoundError as e:
        raise Failure(f"Erreur lors de l'exécution de 1_bis_count_inject.py : {str(e)}")


####################################################################################################
################################     Partie 3 Nettoyage    ############################################
####################################################################################################

@asset(key="3_Azure_Nettoyage", group_name="azure_tasks" , ins={"upstream": AssetIn(key="2_Azure_Count")})
def execute_Nettoyage(context: AssetExecutionContext, upstream: bool):
    """

   Nettoyage de la BDD pour avoir la bonne URL 

    """
    if not upstream:
        context.log.info("La tâche précédente a échoué, donc cette tâche ne sera pas exécutée.")
        return
    
    context.log.info("Début de l'exécution de 2_nettoyage.py")
    try:
        result = subprocess.run(["python", "Script_projet/2_nettoyage.py"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Failure(f"Erreur lors de l'exécution de 2_nettoyage.py : {result.stderr}")
        else:
            context.log.info("2_nettoyage.py exécuté avec succès")
            return True
    except FileNotFoundError as e:
        raise Failure(f"Erreur lors de l'exécution de 2_nettoyage.py : {str(e)}")

####################################################################################################
################################     Partie 4 suppresion des doublon     ###########################
####################################################################################################

@asset(key="4_Azure_delete_doublon", group_name="azure_tasks", ins={"upstream": AssetIn(key="3_Azure_Nettoyage")})
def execute_delete_doublon(context: AssetExecutionContext, upstream: bool):
    """

   suppresion des doublon  

    """
    if not upstream:
        context.log.info("La tâche précédente a échoué, donc cette tâche ne sera pas exécutée.")
        return
    
    context.log.info("Début de l'exécution de 3_delete_doublon.py")
    try:
        result = subprocess.run(["python", "Script_projet/3_delete_doublon.py"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Failure(f"Erreur lors de l'exécution de 3_delete_doublon.py : {result.stderr}")
        else:
            lines_inserted = [int(s) for s in result.stdout.split() if s.isdigit()]
            if lines_inserted:
                context.log.info(f"{lines_inserted[0]}  doublon  ont été supprimer de la BDD.")
            context.log.info("3_delete_doublon.py exécuté avec succès")
            return True
    except FileNotFoundError as e:
        raise Failure(f"Erreur lors de l'exécution de 3_delete_doublon.py : {str(e)}")

####################################################################################################
################################     Partie 5 recuperation du bon prix par url    ##################
####################################################################################################

@asset(key="5_Azure_changement_prix", group_name="azure_tasks" , ins={"upstream": AssetIn(key="4_Azure_delete_doublon")})
def execute_changement_prix(context: AssetExecutionContext, upstream: bool):
    """

   changement de prix pour avoir les bon prix par rapport a l' URL

    """
    if not upstream:
        context.log.info("La tâche précédente a échoué, donc cette tâche ne sera pas exécutée.")
        return
    
    context.log.info("Début de l'exécution de 4_good_price.py")
    try:
        result = subprocess.run(["python", "Script_projet/4_good_price.py"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Failure(f"Erreur lors de l'exécution de 4_good_price.py : {result.stderr}")
        else:
            context.log.info("4_good_price exécuté avec succès")
            return True
    except FileNotFoundError as e:
        raise Failure(f"Erreur lors de l'exécution de 4_good_price.py : {str(e)}")
    
####################################################################################################
################################     Partie 6 recuperation ajout de la marque     ##################
####################################################################################################

@asset(key="6_Azure_ajouts_marque", group_name="azure_tasks" , ins={"upstream": AssetIn(key="5_Azure_changement_prix")})
def execute_ajouts_marque(context: AssetExecutionContext, upstream: bool):
    """

   ajouts de la marque ( prend le 1er mots de description )

    """
    if not upstream:
        context.log.info("La tâche précédente a échoué, donc cette tâche ne sera pas exécutée.")
        return
    
    context.log.info("Début de l'exécution de 5_update_marque.py")
    try:
        result = subprocess.run(["python", "Script_projet/5_update_marque.py"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Failure(f"Erreur lors de l'exécution de 5_update_marque.py : {result.stderr}")
        else:
            context.log.info("5_update_marque exécuté avec succès")
            return True
    except FileNotFoundError as e:
        raise Failure(f"Erreur lors de l'exécution de 5_update_marque.py : {str(e)}")
      
    
####################################################################################################
################################     Partie 7 suppresion des prix a 666      ##################
####################################################################################################

@asset(key="7_Azure_delete_666", group_name="azure_tasks" , ins={"upstream": AssetIn(key="6_Azure_ajouts_marque")})
def execute_delete_666(context: AssetExecutionContext, upstream: bool):
    """

   suppression des prix égale à 666 

    """
    if not upstream:
        context.log.info("La tâche précédente a échoué, donc cette tâche ne sera pas exécutée.")
        return
    
    context.log.info("Début de l'exécution de 6_delete_price_666.py")
    
    try:
        result = subprocess.run(["python", "Script_projet/6_delete_price_666.py"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Failure(f"Erreur lors de l'exécution de 6_delete_price_666.py : {result.stderr}")
        else:
            context.log.info("5_update_marque exécuté avec succès")
            return True
    except FileNotFoundError as e:
        raise Failure(f"Erreur lors de l'exécution de 6_delete_price_666.py : {str(e)}")
      
        

# Définition des horaires pour chaque tâche

def schedule_azure_test():
    return ScheduleDefinition(
        name="azure_test_schedule",
        job_name="Azure_Test_Job",
        cron_schedule="00 08 * * *",
        execution_timezone="Europe/Paris",
    )


# Définition des assets, jobs et schedules

defs = Definitions(
    assets=[execute_Scrapy, execute_Count, execute_Nettoyage, execute_delete_doublon
            , execute_changement_prix , execute_ajouts_marque ,execute_delete_666],# ,execute_delete_666
    jobs=[
        define_asset_job(
            name="Azure_Test_Job",
            selection=AssetSelection.groups("azure_tasks"),
        )
        

    ],
    schedules=[
        schedule_azure_test()

    ],
)